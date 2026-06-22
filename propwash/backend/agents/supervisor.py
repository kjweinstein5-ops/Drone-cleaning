"""Supervisor Agent — prescribes per-zone cleaning parameters and generates work orders.

Reads the versioned surface treatment table. Safety checks are applied after
this agent produces a prescription, before dispatch. See CLAUDE.md §3, §7.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from propwash.backend.agents.base import PropwashAgent
from propwash.backend.models.prescription import Prescription
from propwash.backend.models.work_order import WorkOrder
from propwash.backend.models.zone import ZoneSignature

logger = logging.getLogger(__name__)


class SupervisorAgent(PropwashAgent):
    prompt_file = "supervisor.txt"

    async def prescribe(
        self,
        zones: List[ZoneSignature],
        surface_table: Dict[str, Any],
    ) -> List[WorkOrder]:
        """Generate work orders for all zones."""
        date_str = datetime.utcnow().strftime("%Y%m%d")

        user_content = json.dumps(
            {
                "zones": [z.model_dump() for z in zones],
                "surface_treatment_table": surface_table,
                "instruction": (
                    "For each zone, select parameters from the surface table, sequence "
                    "the zones efficiently, and return a JSON array of WorkOrder objects."
                ),
            }
        )
        logger.info("SupervisorAgent.prescribe zones=%d", len(zones))
        raw = self._call(user_content)

        try:
            data: List[Dict[str, Any]] = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("SupervisorAgent returned non-JSON: %s", raw[:200])
            raise ValueError("SupervisorAgent did not return valid JSON")

        work_orders = []
        for i, item in enumerate(data):
            if "job_id" not in item:
                item["job_id"] = f"job_{date_str}_{i+1:03d}"
            work_orders.append(WorkOrder(**item))

        logger.info("SupervisorAgent produced %d work orders", len(work_orders))
        return work_orders
