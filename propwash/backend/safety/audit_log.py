"""Tamper-evident safety & compliance audit log.

Dual-purpose by design (docs/REGULATORY_STRATEGY.md §3):
  1. **Waiver / compliance evidence.** FAA waivers are granted on demonstrated
     safety mitigation. A hash-chained, append-only record of every safety
     decision is far stronger evidence than prose.
  2. **Learning-model input.** The same execution-vs-prescription deltas feed
     the calibration loop (IP_PROTECTION.md §2 — the data moat).

Tamper-evidence via hash chaining: every entry embeds the hash of the previous
entry, so any alteration or deletion breaks the chain and is detectable. This is
what makes the log *evidence* rather than just a file.

Append-only: there is deliberately no update or delete API.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

GENESIS_HASH = "0" * 64


class EventType(str, Enum):
    # Safety-critical (waiver evidence)
    SAFETY_VIOLATION = "safety_violation"      # prescription rejected by Tier-1
    HUMAN_DETECTED = "human_detected"          # thermal human-presence halt
    WATCHDOG_TRIP = "watchdog_trip"            # loss of positive control
    KEEPOUT_BREACH = "keepout_breach"          # path entered an exclusion volume
    OPERATOR_ABORT = "operator_abort"          # human pressed abort/override
    PRESSURE_CLAMPED = "pressure_clamped"      # setpoint hit a ceiling
    # Operational (learning input)
    MISSION_DISPATCHED = "mission_dispatched"
    ZONE_COMPLETED = "zone_completed"
    VERIFICATION = "verification"              # PASS/FAIL + residual
    REQUEUE = "requeue"                        # failed zone re-queued


# Events that must never be filtered out of a compliance export.
SAFETY_CRITICAL = {
    EventType.SAFETY_VIOLATION,
    EventType.HUMAN_DETECTED,
    EventType.WATCHDOG_TRIP,
    EventType.KEEPOUT_BREACH,
    EventType.OPERATOR_ABORT,
    EventType.PRESSURE_CLAMPED,
}


@dataclass(frozen=True)
class AuditEntry:
    seq: int
    timestamp: float
    event_type: EventType
    job_id: str
    zone_id: Optional[str]
    detail: str
    data: Dict[str, Any] = field(default_factory=dict)
    prev_hash: str = GENESIS_HASH
    entry_hash: str = ""

    def compute_hash(self) -> str:
        payload = {
            "seq": self.seq,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "job_id": self.job_id,
            "zone_id": self.zone_id,
            "detail": self.detail,
            "data": self.data,
            "prev_hash": self.prev_hash,
        }
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    @property
    def is_safety_critical(self) -> bool:
        return self.event_type in SAFETY_CRITICAL


class AuditLog:
    """Append-only, hash-chained safety log.

        log = AuditLog()
        log.record(EventType.HUMAN_DETECTED, job_id="job_1", zone_id="RF-S",
                   detail="Thermal blob matched human criteria — dispatch halted")
        assert log.verify_integrity().valid
    """

    def __init__(self, clock: Optional[Callable[[], float]] = None) -> None:
        self._entries: List[AuditEntry] = []
        self._clock = clock or time.time

    # ── append ────────────────────────────────────────────────────────────────

    def record(
        self,
        event_type: EventType,
        job_id: str,
        detail: str,
        zone_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        prev = self._entries[-1].entry_hash if self._entries else GENESIS_HASH
        draft = AuditEntry(
            seq=len(self._entries),
            timestamp=self._clock(),
            event_type=event_type,
            job_id=job_id,
            zone_id=zone_id,
            detail=detail,
            data=dict(data or {}),
            prev_hash=prev,
        )
        entry = AuditEntry(**{**asdict(draft), "event_type": draft.event_type,
                              "entry_hash": draft.compute_hash()})
        self._entries.append(entry)
        return entry

    # ── read ──────────────────────────────────────────────────────────────────

    @property
    def entries(self) -> List[AuditEntry]:
        return list(self._entries)   # copy — callers cannot mutate the chain

    def __len__(self) -> int:
        return len(self._entries)

    def for_job(self, job_id: str) -> List[AuditEntry]:
        return [e for e in self._entries if e.job_id == job_id]

    def safety_events(self) -> List[AuditEntry]:
        return [e for e in self._entries if e.is_safety_critical]

    # ── integrity ─────────────────────────────────────────────────────────────

    def verify_integrity(self) -> "IntegrityResult":
        """Recompute the chain. Detects any alteration, deletion, or reordering."""
        prev = GENESIS_HASH
        for i, e in enumerate(self._entries):
            if e.seq != i:
                return IntegrityResult(False, i, f"Sequence break at index {i} (seq={e.seq})")
            if e.prev_hash != prev:
                return IntegrityResult(False, i, f"Broken chain at seq {e.seq}")
            if e.entry_hash != e.compute_hash():
                return IntegrityResult(False, i, f"Altered content at seq {e.seq}")
            prev = e.entry_hash
        return IntegrityResult(True, None, "Chain intact")

    # ── export ────────────────────────────────────────────────────────────────

    def compliance_export(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Export for an FAA waiver package / customer compliance report.

        Includes the integrity proof so a reviewer can verify nothing was edited.
        """
        rows = self.for_job(job_id) if job_id else self._entries
        integrity = self.verify_integrity()
        return {
            "generated_at": self._clock(),
            "job_id": job_id,
            "entry_count": len(rows),
            "safety_event_count": sum(1 for e in rows if e.is_safety_critical),
            "integrity_valid": integrity.valid,
            "integrity_note": integrity.note,
            "chain_head": self._entries[-1].entry_hash if self._entries else GENESIS_HASH,
            "entries": [
                {
                    "seq": e.seq,
                    "timestamp": e.timestamp,
                    "event_type": e.event_type.value,
                    "job_id": e.job_id,
                    "zone_id": e.zone_id,
                    "detail": e.detail,
                    "data": e.data,
                    "safety_critical": e.is_safety_critical,
                    "entry_hash": e.entry_hash,
                }
                for e in rows
            ],
        }


@dataclass
class IntegrityResult:
    valid: bool
    failed_at: Optional[int]
    note: str
