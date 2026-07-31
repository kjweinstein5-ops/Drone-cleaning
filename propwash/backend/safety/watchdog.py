"""Tier-1 safety watchdog — pump OFF on any loss of positive control.

Enforces the invariant from docs/COMMUNICATION_AND_AUTONOMY.md §3:

    ANY communication failure results in the pump going OFF and the aircraft
    entering a safe state. There is no failure mode in which spraying continues
    without positive control.

Deterministic, dependency-free, and clock-injectable so it is fully testable.
This is Tier 1 (CLAUDE.md §2): no Claude agent can suppress or delay it, and it
must run locally on the companion computer — never behind a cloud round-trip.

Design decisions that matter for safety:
  * **Fail-closed on unknown.** A channel that has never reported is treated as
    stale, not healthy. Silence is never assumed to be good news.
  * **No auto-resume.** After a trip, restoring the link does NOT restart
    spraying. A human must explicitly re-arm. This prevents a flapping link from
    cycling the pump unattended.
  * **Independent of the PSM firmware ceiling.** This is the software half of a
    defense-in-depth pair; the PSM idles on signal loss in hardware regardless
    (docs/DYNAMIC_PRESSURE_HARDWARE.md §4).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class Channel(str, Enum):
    """Monitored links. Each must beat within its own timeout."""

    COMPANION = "companion"      # companion computer / mission computer alive
    C2 = "c2"                    # command & control link (RC / GCS)
    PAYLOAD = "payload"          # payload command + actual-pressure telemetry
    TELEMETRY = "telemetry"      # position/attitude stream


# Per-channel timeouts (seconds). Tight where loss is most dangerous.
DEFAULT_TIMEOUTS: Dict[Channel, float] = {
    Channel.COMPANION: 0.5,
    Channel.C2: 1.0,
    Channel.PAYLOAD: 0.5,
    Channel.TELEMETRY: 2.0,
}


class WatchdogState(str, Enum):
    DISARMED = "disarmed"   # not spraying; safe by default
    ARMED = "armed"         # positive control confirmed; spraying permitted
    TRIPPED = "tripped"     # failure detected; pump OFF, requires manual re-arm


@dataclass
class WatchdogVerdict:
    state: WatchdogState
    pump_permitted: bool
    stale_channels: List[Channel] = field(default_factory=list)
    reason: str = ""

    @property
    def must_cut_pump(self) -> bool:
        return not self.pump_permitted


class SafetyWatchdog:
    """Heartbeat monitor that cuts the pump on loss of positive control.

    Usage:
        wd = SafetyWatchdog()
        wd.beat(Channel.COMPANION); ...      # feed every channel
        wd.arm()                              # only succeeds if all healthy
        verdict = wd.check()                  # call every control cycle
        if verdict.must_cut_pump: cut_pump()
    """

    def __init__(
        self,
        timeouts: Optional[Dict[Channel, float]] = None,
        clock: Optional[Callable[[], float]] = None,
    ) -> None:
        self._timeouts = dict(timeouts or DEFAULT_TIMEOUTS)
        self._clock = clock or time.monotonic
        self._last_beat: Dict[Channel, float] = {}
        self._state = WatchdogState.DISARMED
        self._trip_reason = ""

    # ── inputs ────────────────────────────────────────────────────────────────

    def beat(self, channel: Channel) -> None:
        """Record a heartbeat from a channel."""
        self._last_beat[channel] = self._clock()

    def beat_all(self) -> None:
        """Convenience for tests/bring-up: mark every channel healthy now."""
        for ch in self._timeouts:
            self.beat(ch)

    # ── state ─────────────────────────────────────────────────────────────────

    @property
    def state(self) -> WatchdogState:
        return self._state

    def stale_channels(self) -> List[Channel]:
        """Channels past their timeout. Never-seen channels count as stale."""
        now = self._clock()
        stale: List[Channel] = []
        for ch, timeout in self._timeouts.items():
            last = self._last_beat.get(ch)
            if last is None or (now - last) > timeout:
                stale.append(ch)
        return stale

    def arm(self) -> WatchdogVerdict:
        """Permit spraying — only if every channel is currently healthy.

        Refuses to arm from TRIPPED unless reset() is called first (explicit
        human acknowledgement of the fault).
        """
        if self._state == WatchdogState.TRIPPED:
            return WatchdogVerdict(
                state=self._state, pump_permitted=False,
                stale_channels=self.stale_channels(),
                reason=f"Cannot arm while TRIPPED ({self._trip_reason}). reset() required.",
            )
        stale = self.stale_channels()
        if stale:
            return WatchdogVerdict(
                state=self._state, pump_permitted=False, stale_channels=stale,
                reason=f"Cannot arm — stale: {', '.join(c.value for c in stale)}",
            )
        self._state = WatchdogState.ARMED
        return WatchdogVerdict(state=self._state, pump_permitted=True,
                               reason="Positive control confirmed.")

    def check(self) -> WatchdogVerdict:
        """Evaluate every control cycle. Trips (latching) on any stale channel."""
        stale = self.stale_channels()

        if self._state == WatchdogState.TRIPPED:
            return WatchdogVerdict(
                state=self._state, pump_permitted=False, stale_channels=stale,
                reason=self._trip_reason,
            )

        if self._state == WatchdogState.ARMED and stale:
            self._trip_reason = (
                f"Loss of positive control on: {', '.join(c.value for c in stale)} — pump OFF."
            )
            self._state = WatchdogState.TRIPPED
            return WatchdogVerdict(
                state=self._state, pump_permitted=False, stale_channels=stale,
                reason=self._trip_reason,
            )

        permitted = self._state == WatchdogState.ARMED
        return WatchdogVerdict(
            state=self._state, pump_permitted=permitted, stale_channels=stale,
            reason="" if permitted else "Disarmed — pump not permitted.",
        )

    def disarm(self) -> WatchdogVerdict:
        """Normal end-of-zone stop. Pump not permitted; not a fault."""
        if self._state != WatchdogState.TRIPPED:
            self._state = WatchdogState.DISARMED
        return self.check()

    def reset(self) -> None:
        """Explicit human acknowledgement of a trip. Returns to DISARMED.

        Deliberately does NOT resume spraying — the operator must arm() again.
        """
        self._state = WatchdogState.DISARMED
        self._trip_reason = ""
