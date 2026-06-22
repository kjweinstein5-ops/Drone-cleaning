"""Cleaning Agent — translates work orders into operator instructions and monitors execution.

ADVISORY ONLY — does NOT control Lucid hardware (Path A).
The operator remains in command (FAA Part 107). See CLAUDE.md §7, §10.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from propwash.backend.agents.base import PropwashAgent
from propwash.backend.models.work_order import WorkOrder

logger = logging.getLogger(__name__)


class CleaningAgent(PropwashAgent):
    prompt_file = "cleaning.txt"

    async def generate_operator_brief(self, work_order: WorkOrder) -> str:
        """Return plain-language operator instructions for this work order."""
        user_content = json.dumps(
            {
                "work_order": work_order.model_dump(),
                "instruction": (
                    "Generate a numbered operator checklist for this work order. "
                    "Include: nozzle to fit, chemical to load, standoff distance, "
                    "sweep pattern, dwell time. Plain language for a trained non-expert operator."
                ),
            }
        )
        logger.info(
            "CleaningAgent.generate_operator_brief job_id=%s zone=%s",
            work_order.job_id,
            work_order.zone.zone_id,
        )
        return self._call(user_content)

    async def analyse_telemetry(
        self,
        work_order: WorkOrder,
        telemetry: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compare live telemetry against prescription; return deviation report."""
        user_content = json.dumps(
            {
                "work_order": work_order.model_dump(),
                "telemetry": telemetry,
                "instruction": (
                    "Compare the telemetry against the prescription. Flag any deviation > 20%. "
                    "Return a JSON object with keys: deviations (list), alerts (list), "
                    "execution_log (dict with actual values)."
                ),
            }
        )
        raw = self._call(user_content)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"deviations": [], "alerts": [], "execution_log": {}, "raw": raw}
