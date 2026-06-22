"""PROPWASH orchestrator — drives the full Sense→Fuse→Plan→Execute→Verify→(re-queue) loop.

This is Tier 2 (soft real-time, ~1 Hz). It calls Tier-3 agents and enforces
the deterministic Tier-1 safety checks before any dispatch. See CLAUDE.md §2.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from propwash.backend.agents.cleaning import CleaningAgent
from propwash.backend.agents.post_clean import PostCleanAgent
from propwash.backend.agents.supervisor import SupervisorAgent
from propwash.backend.execution.transport import ExecutionTransport
from propwash.backend.execution.work_order_transport import WorkOrderTransport
from propwash.backend.fusion.pipeline import FusionPipeline
from propwash.backend.models.verification import Verdict, VerificationResult
from propwash.backend.models.work_order import WorkOrder, WorkOrderStatus
from propwash.backend.safety.checks import SafetyChecker

logger = logging.getLogger(__name__)

_SURFACE_TABLE_PATH = Path(__file__).parent.parent.parent.parent / "prescriptions" / "surface_treatment_v1.json"


def _load_surface_table() -> Dict[str, Any]:
    with open(_SURFACE_TABLE_PATH) as f:
        return json.load(f)


class Orchestrator:
    """Coordinates all agents and enforces safety gates for a cleaning job."""

    def __init__(self, transport: Optional[ExecutionTransport] = None) -> None:
        self._fusion_pipeline = FusionPipeline()
        self._supervisor = SupervisorAgent()
        self._cleaning_agent = CleaningAgent()
        self._post_clean_agent = PostCleanAgent()
        self._safety = SafetyChecker()
        self._transport: ExecutionTransport = transport or WorkOrderTransport()
        self._surface_table = _load_surface_table()

    async def run_survey_phase(
        self,
        property_id: str,
        job_id: str,
        thermal_refs: List[str],
        rgb_refs: List[str],
        sfm_ref: Optional[str] = None,
    ) -> List[WorkOrder]:
        """Phase 1+2+3: Sense + Fuse + Plan — return queued work orders."""
        logger.info("Orchestrator.run_survey_phase property_id=%s job_id=%s", property_id, job_id)

        # Fuse: thermal+RGB+SfM → zone signatures
        zones = await self._fusion_pipeline.run(
            property_id=property_id,
            job_id=job_id,
            thermal_refs=thermal_refs,
            rgb_refs=rgb_refs,
            sfm_ref=sfm_ref,
        )
        logger.info("Survey produced %d zones", len(zones))

        # Plan: zone signatures → prescriptions → work orders
        work_orders = await self._supervisor.prescribe(zones, self._surface_table)
        logger.info("Supervisor generated %d work orders", len(work_orders))

        # Safety gate: validate every prescription before queuing
        safe_orders = []
        for wo in work_orders:
            result = self._safety.check_prescription(wo.prescription, wo.zone.surface_type)
            if result.passed:
                safe_orders.append(wo)
            else:
                for v in result.violations:
                    logger.error(
                        "SAFETY VIOLATION job_id=%s zone=%s rule=%s: %s",
                        wo.job_id, wo.zone.zone_id, v.rule, v.message,
                    )
                # Do not queue — log and skip. Human review required.

        logger.info(
            "%d/%d work orders passed safety checks", len(safe_orders), len(work_orders)
        )
        return safe_orders

    async def dispatch_work_order(self, work_order: WorkOrder) -> str:
        """Phase 4: Execute — dispatch to transport, return operator brief."""
        brief = await self._cleaning_agent.generate_operator_brief(work_order)
        result = await self._transport.dispatch(work_order)
        logger.info(
            "Dispatched job_id=%s via %s status=%s",
            work_order.job_id, self._transport.name, result.status,
        )
        return brief

    async def verify_zone(
        self,
        work_order: WorkOrder,
        post_scan_thermal_ref: str,
        post_scan_rgb_ref: str,
        threshold: float = 0.15,
    ) -> VerificationResult:
        """Phase 5: Verify — run post-clean agent, return verdict."""
        await self._transport.mark_verifying(work_order.job_id)

        verification = await self._post_clean_agent.verify(
            work_order=work_order,
            post_scan_thermal_ref=post_scan_thermal_ref,
            post_scan_rgb_ref=post_scan_rgb_ref,
            threshold=threshold,
        )

        if verification.verdict == Verdict.PASS:
            await self._transport.mark_done(work_order.job_id)
            logger.info("PASS zone=%s residual=%.3f", work_order.zone.zone_id, verification.residual_confidence)
        else:
            await self._transport.mark_reflagged(work_order.job_id)
            logger.warning(
                "FAIL zone=%s residual=%.3f — will re-queue if within limits",
                work_order.zone.zone_id, verification.residual_confidence,
            )

        return verification

    async def requeue_if_needed(
        self, work_order: WorkOrder, verification: VerificationResult
    ) -> Optional[WorkOrder]:
        """Re-queue a failed zone with bumped pressure, subject to safety checks."""
        if not self._post_clean_agent.should_requeue(verification, work_order):
            return None

        delta = work_order.prescription.requeue_on_fail_pressure_delta
        new_wo = work_order.next_attempt(delta)

        # Safety gate on re-queued prescription
        safety_result = self._safety.check_prescription(
            new_wo.prescription, new_wo.zone.surface_type
        )
        if not safety_result.passed:
            for v in safety_result.violations:
                logger.error(
                    "Re-queue BLOCKED by safety zone=%s rule=%s: %s",
                    new_wo.zone.zone_id, v.rule, v.message,
                )
            return None

        verification.delta_applied = {"pressure_bar": delta}
        logger.info(
            "Re-queuing zone=%s attempt=%d pressure=%.2f bar",
            new_wo.zone.zone_id, new_wo.attempt, new_wo.prescription.pressure_bar,
        )
        return new_wo
