"""Tests for the Tier-1 safety watchdog.

The invariant under test: ANY loss of positive control cuts the pump, and a
restored link never auto-resumes spraying.
"""

from __future__ import annotations

import pytest

from propwash.backend.safety.watchdog import (
    Channel,
    SafetyWatchdog,
    WatchdogState,
)


class FakeClock:
    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


def _armed_watchdog():
    clock = FakeClock()
    wd = SafetyWatchdog(clock=clock)
    wd.beat_all()
    assert wd.arm().pump_permitted is True
    return wd, clock


# ── fail-closed defaults ──────────────────────────────────────────────────────

def test_starts_disarmed_and_pump_not_permitted():
    wd = SafetyWatchdog(clock=FakeClock())
    v = wd.check()
    assert wd.state is WatchdogState.DISARMED
    assert v.pump_permitted is False
    assert v.must_cut_pump is True


def test_never_seen_channels_are_stale_not_healthy():
    # Silence must never be mistaken for health.
    wd = SafetyWatchdog(clock=FakeClock())
    assert set(wd.stale_channels()) == set(Channel)


def test_cannot_arm_with_a_stale_channel():
    clock = FakeClock()
    wd = SafetyWatchdog(clock=clock)
    wd.beat(Channel.COMPANION)
    wd.beat(Channel.C2)
    wd.beat(Channel.PAYLOAD)
    # TELEMETRY never beat → cannot arm
    v = wd.arm()
    assert v.pump_permitted is False
    assert Channel.TELEMETRY in v.stale_channels


# ── the core invariant ────────────────────────────────────────────────────────

@pytest.mark.parametrize("channel", list(Channel))
def test_any_channel_loss_cuts_the_pump(channel):
    wd, clock = _armed_watchdog()
    # Keep every other channel alive; starve exactly one.
    clock.advance(3.0)
    for ch in Channel:
        if ch is not channel:
            wd.beat(ch)
    v = wd.check()
    assert v.must_cut_pump is True
    assert wd.state is WatchdogState.TRIPPED
    assert channel in v.stale_channels


def test_healthy_heartbeats_keep_pump_permitted():
    wd, clock = _armed_watchdog()
    for _ in range(10):
        clock.advance(0.1)
        wd.beat_all()
        assert wd.check().pump_permitted is True


# ── latching / no auto-resume ─────────────────────────────────────────────────

def test_trip_latches_and_restored_link_does_not_auto_resume():
    wd, clock = _armed_watchdog()
    clock.advance(5.0)
    assert wd.check().must_cut_pump is True          # tripped

    # Link comes back — spraying must NOT resume on its own.
    wd.beat_all()
    v = wd.check()
    assert wd.state is WatchdogState.TRIPPED
    assert v.pump_permitted is False


def test_cannot_arm_while_tripped_without_reset():
    wd, clock = _armed_watchdog()
    clock.advance(5.0)
    wd.check()
    wd.beat_all()
    v = wd.arm()
    assert v.pump_permitted is False
    assert "reset()" in v.reason


def test_reset_then_arm_recovers():
    wd, clock = _armed_watchdog()
    clock.advance(5.0)
    wd.check()
    wd.reset()
    assert wd.state is WatchdogState.DISARMED
    assert wd.check().pump_permitted is False        # still off until re-armed
    wd.beat_all()
    assert wd.arm().pump_permitted is True


# ── normal operation ──────────────────────────────────────────────────────────

def test_disarm_is_not_a_fault():
    wd, _ = _armed_watchdog()
    v = wd.disarm()
    assert wd.state is WatchdogState.DISARMED
    assert v.pump_permitted is False
    assert "Disarmed" in v.reason


def test_timeouts_are_per_channel():
    # PAYLOAD (0.5s) goes stale before TELEMETRY (2.0s).
    clock = FakeClock()
    wd = SafetyWatchdog(clock=clock)
    wd.beat_all()
    wd.arm()
    clock.advance(1.0)
    wd.beat(Channel.COMPANION)
    wd.beat(Channel.C2)
    wd.beat(Channel.TELEMETRY)
    stale = wd.stale_channels()
    assert Channel.PAYLOAD in stale
    assert Channel.TELEMETRY not in stale
