"""Tests for the tamper-evident safety & compliance audit log.

The property that makes this *evidence* rather than a log file: any alteration,
deletion, or reordering must be detectable.
"""

from __future__ import annotations

from dataclasses import asdict

import pytest

from propwash.backend.safety.audit_log import (
    AuditEntry,
    AuditLog,
    EventType,
    GENESIS_HASH,
)


class FakeClock:
    def __init__(self, t: float = 1_700_000_000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


def _populated():
    log = AuditLog(clock=FakeClock())
    log.record(EventType.MISSION_DISPATCHED, "job_1", "Mission uploaded", zone_id="SOL-ROOF")
    log.record(EventType.HUMAN_DETECTED, "job_1", "Thermal blob — halted", zone_id="RF-S")
    log.record(EventType.ZONE_COMPLETED, "job_1", "Zone done", zone_id="SOL-ROOF")
    log.record(EventType.WATCHDOG_TRIP, "job_2", "Payload link lost — pump OFF")
    return log


# ── chaining ──────────────────────────────────────────────────────────────────

def test_first_entry_chains_from_genesis():
    log = AuditLog(clock=FakeClock())
    e = log.record(EventType.MISSION_DISPATCHED, "job_1", "start")
    assert e.prev_hash == GENESIS_HASH
    assert e.entry_hash


def test_entries_chain_to_previous():
    log = _populated()
    entries = log.entries
    for prev, cur in zip(entries, entries[1:]):
        assert cur.prev_hash == prev.entry_hash


def test_clean_log_verifies():
    assert _populated().verify_integrity().valid is True


# ── tamper detection (the whole point) ────────────────────────────────────────

def test_altered_content_is_detected():
    log = _populated()
    # Simulate someone editing a damning entry's text.
    tampered = AuditEntry(**{**asdict(log._entries[1]),
                             "event_type": log._entries[1].event_type,
                             "detail": "nothing happened"})
    log._entries[1] = tampered
    result = log.verify_integrity()
    assert result.valid is False
    assert "Altered content" in result.note


def test_deleted_entry_is_detected():
    log = _populated()
    del log._entries[1]
    assert log.verify_integrity().valid is False


def test_reordering_is_detected():
    log = _populated()
    log._entries[1], log._entries[2] = log._entries[2], log._entries[1]
    assert log.verify_integrity().valid is False


def test_appending_a_forged_entry_is_detected():
    log = _populated()
    forged = AuditEntry(
        seq=len(log._entries), timestamp=1.0, event_type=EventType.ZONE_COMPLETED,
        job_id="job_1", zone_id="X", detail="fake pass",
        prev_hash="deadbeef", entry_hash="bogus",
    )
    log._entries.append(forged)
    assert log.verify_integrity().valid is False


# ── append-only / immutability ────────────────────────────────────────────────

def test_entries_property_returns_a_copy():
    log = _populated()
    got = log.entries
    got.clear()
    assert len(log) == 4          # internal chain untouched


def test_no_update_or_delete_api():
    log = AuditLog()
    for forbidden in ("update", "delete", "edit", "remove"):
        assert not hasattr(log, forbidden)


# ── querying + export ─────────────────────────────────────────────────────────

def test_filter_by_job_and_safety_events():
    log = _populated()
    assert len(log.for_job("job_1")) == 3
    kinds = {e.event_type for e in log.safety_events()}
    assert EventType.HUMAN_DETECTED in kinds
    assert EventType.WATCHDOG_TRIP in kinds
    assert EventType.ZONE_COMPLETED not in kinds   # operational, not safety-critical


def test_compliance_export_includes_integrity_proof():
    log = _populated()
    export = log.compliance_export(job_id="job_1")
    assert export["entry_count"] == 3
    assert export["safety_event_count"] == 1
    assert export["integrity_valid"] is True
    assert export["chain_head"] == log.entries[-1].entry_hash
    assert all("entry_hash" in row for row in export["entries"])


def test_compliance_export_flags_a_tampered_chain():
    log = _populated()
    del log._entries[0]
    assert log.compliance_export()["integrity_valid"] is False
