"""Post-Clean Agent — verification re-scan, PASS/FAIL verdict, re-queue loop.

Triggers Autel re-scan, computes residual proxy score, decides PASS/FAIL,
and feeds outcomes back to the learning model. See CLAUDE.md §3, §6.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from propwash.backend.agents.base import PropwashAgent
from propwash.backend.models.verification import VerificationResult, Verdict
from propwash.backend.models.work_order import WorkOrder

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = 3


class PostCleanAgent(PropwashAgent):
    prompt_file = "post_clean.txt"

    async def verify(
        self,
        work_order: WorkOrder,
        post_scan_thermal_ref: str,
        post_scan_rgb_ref: str,
        threshold: float = 0.15,
    ) -> VerificationResult:
        """Compute residual confidence from re-scan and return a VerificationResult."""
        user_content = json.dumps(
            {
                "work_order": work_order.model_dump(),
                "post_scan_thermal_ref": post_scan_thermal_ref,
                "post_scan_rgb_ref": post_scan_rgb_ref,
                "threshold": threshold,
                "instruction": (
                    "Compute residual_confidence from post-clean thermal+RGB imagery "
                    "(proxy score, same basis as pre-clean). Compare against threshold. "
                    "Return a JSON VerificationResult object."
                ),
            }
        )
        logger.info(
            "PostCleanAgent.verify job_id=%s zone=%s attempt=%d",
            work_order.job_id,
            work_order.zone.zone_id,
            work_order.attempt,
        )
        raw = self._call(user_content)

        try:
            data: Dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("PostCleanAgent returned non-JSON: %s", raw[:200])
            raise ValueError("PostCleanAgent did not return valid JSON")

        result = VerificationResult(**data)
        logger.info(
            "PostCleanAgent verdict=%s residual=%.3f zone=%s",
            result.verdict,
            result.residual_confidence,
            result.zone_id,
        )
        return result

    def should_requeue(self, result: VerificationResult, work_order: WorkOrder) -> bool:
        """Determine if a FAIL should trigger re-queue or escalate to human review."""
        if result.verdict == Verdict.PASS:
            return False
        if work_order.attempt >= _MAX_ATTEMPTS:
            logger.warning(
                "Zone %s has failed %d times — escalating to human review instead of re-queuing.",
                work_order.zone.zone_id,
                work_order.attempt,
            )
            return False
        return True
