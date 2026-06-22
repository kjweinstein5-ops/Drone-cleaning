"""Mapping Agent — ingests Autel 640T imagery, produces georeferenced surface map.

Input: thermal + RGB imagery (+ optional SfM point cloud) from a survey flight.
Output: list of ZoneSignature (surface_type, geometry, pitch; no grime scores yet).
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from propwash.backend.agents.base import PropwashAgent
from propwash.backend.models.zone import DataSource, SurfaceType, ZoneSignature

logger = logging.getLogger(__name__)


class MappingAgent(PropwashAgent):
    prompt_file = "mapping.txt"

    async def map_property(
        self,
        property_id: str,
        job_id: str,
        imagery_refs: List[str],
        sfm_ref: str | None = None,
    ) -> List[ZoneSignature]:
        """Run the mapping pass; return candidate zones."""
        user_content = json.dumps(
            {
                "property_id": property_id,
                "job_id": job_id,
                "imagery_refs": imagery_refs,
                "sfm_ref": sfm_ref,
                "instruction": (
                    "Analyse the provided imagery and produce a surface map. "
                    "Return a JSON array of ZoneSignature objects."
                ),
            }
        )
        logger.info("MappingAgent.map_property property_id=%s job_id=%s", property_id, job_id)
        raw = self._call(user_content)

        try:
            data: List[Dict[str, Any]] = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("MappingAgent returned non-JSON: %s", raw[:200])
            raise ValueError("MappingAgent did not return valid JSON")

        zones = []
        for item in data:
            item.setdefault("property_id", property_id)
            item.setdefault("job_id", job_id)
            # Mapping agent doesn't set grime/moisture — provide defaults
            item.setdefault("grime_confidence", 0.0)
            item.setdefault("moisture_index", 0.0)
            zones.append(ZoneSignature(**item))

        logger.info("MappingAgent produced %d zones", len(zones))
        return zones
