"""Fusion (Predictive) Agent — thermal+RGB+SfM → per-zone condition signatures.

CRITICAL: grime_confidence is a PROXY score derived from thermal evaporative
differentials and RGB visible cues. The Autel 640T has NO multispectral/NIR
bands. Do not represent this as spectral biofilm detection. See CLAUDE.md §5.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from propwash.backend.agents.base import PropwashAgent
from propwash.backend.models.zone import ZoneSignature

logger = logging.getLogger(__name__)


class FusionAgent(PropwashAgent):
    prompt_file = "fusion.txt"

    async def fuse_zones(
        self,
        zones: List[ZoneSignature],
        thermal_refs: List[str],
        rgb_refs: List[str],
        sfm_ref: str | None = None,
    ) -> List[ZoneSignature]:
        """Enrich zones with grime_confidence and moisture_index."""
        user_content = json.dumps(
            {
                "zones": [z.model_dump() for z in zones],
                "thermal_refs": thermal_refs,
                "rgb_refs": rgb_refs,
                "sfm_ref": sfm_ref,
                "instruction": (
                    "For each zone compute grime_confidence (proxy, thermal+RGB) and "
                    "moisture_index (thermal). Return a JSON array of updated ZoneSignature objects."
                ),
            }
        )
        logger.info("FusionAgent.fuse_zones zones=%d", len(zones))
        raw = self._call(user_content)

        try:
            data: List[Dict[str, Any]] = json.loads(raw)
        except json.JSONDecodeError:
            logger.error("FusionAgent returned non-JSON: %s", raw[:200])
            raise ValueError("FusionAgent did not return valid JSON")

        enriched = [ZoneSignature(**item) for item in data]
        logger.info("FusionAgent enriched %d zones", len(enriched))
        return enriched
