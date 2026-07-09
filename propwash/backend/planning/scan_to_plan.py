"""scan → plan — turn classified scan zones into safety-gated work orders.

This is the join between the drone-scan pipeline and the PROPWASH cleaning loop.
The three guarantees:
  1. EXCLUSION zones (HVAC, chimneys, people) NEVER become work orders.
  2. Every cleanable zone gets a prescription from the versioned surface table.
  3. Every prescription passes the deterministic safety layer BEFORE it is queued —
     a rejected zone is dropped for human review, never silently cleaned (CLAUDE.md §2).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from propwash.backend.fusion.scan_pipeline import ScannedZone
from propwash.backend.models.work_order import WorkOrder
from propwash.backend.planning.prescriber import TablePrescriber, scanned_zone_to_signature
from propwash.backend.safety.checks import SafetyChecker

logger = logging.getLogger(__name__)


@dataclass
class PlanResult:
    work_orders: List[WorkOrder] = field(default_factory=list)
    excluded: List[Tuple[str, str]] = field(default_factory=list)         # (zone_id, reason)
    safety_rejected: List[Tuple[str, str]] = field(default_factory=list)  # (zone_id, rules)

    @property
    def summary(self) -> str:
        return (
            f"{len(self.work_orders)} queued · {len(self.excluded)} excluded · "
            f"{len(self.safety_rejected)} safety-rejected"
        )


def plan_from_scan(
    scanned_zones: List[ScannedZone],
    job_id: str,
    property_id: str,
    prescriber: Optional[TablePrescriber] = None,
    safety: Optional[SafetyChecker] = None,
) -> PlanResult:
    """Bridge scan output → safety-gated work orders."""
    prescriber = prescriber or TablePrescriber()
    safety = safety or SafetyChecker()
    result = PlanResult()

    for z in scanned_zones:
        # Guarantee 1: exclusion zones are never cleaned.
        if z.is_exclusion:
            result.excluded.append((z.zone_id, z.reason))
            logger.info("EXCLUDED zone=%s: %s", z.zone_id, z.reason)
            continue

        # Guarantee 2: prescription from the versioned table.
        signature = scanned_zone_to_signature(z, property_id, job_id)
        prescription = prescriber.prescribe(signature)

        # Guarantee 3: deterministic safety gate before queuing.
        check = safety.check_prescription(prescription, signature.surface_type)
        if not check.passed:
            rules = "; ".join(v.rule for v in check.violations)
            result.safety_rejected.append((z.zone_id, rules))
            for v in check.violations:
                logger.error("SAFETY REJECT zone=%s rule=%s: %s", z.zone_id, v.rule, v.message)
            continue

        result.work_orders.append(WorkOrder(
            job_id=f"{job_id}_{z.zone_id}",
            zone=signature,
            prescription=prescription,
        ))

    logger.info("plan_from_scan job=%s: %s", job_id, result.summary)
    return result
