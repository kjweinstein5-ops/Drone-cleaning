"""Fusion pipeline — orchestrates thermal+RGB+SfM → zone signatures.

Wraps the FusionAgent with input validation enforcing the §5 sensor caveat:
no multispectral claims, grime_confidence is a proxy score only.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from propwash.backend.agents.fusion import FusionAgent
from propwash.backend.agents.mapping import MappingAgent
from propwash.backend.models.zone import DataSource, ZoneSignature

logger = logging.getLogger(__name__)


class FusionPipeline:
    """End-to-end pipeline: imagery refs → enriched zone signatures.

    Sensor caveat (CLAUDE.md §5): Autel 640T = thermal + RGB ONLY.
    grime_confidence is a thermal+visible proxy, not spectral detection.
    """

    def __init__(self) -> None:
        self._mapping_agent = MappingAgent()
        self._fusion_agent = FusionAgent()

    async def run(
        self,
        property_id: str,
        job_id: str,
        thermal_refs: List[str],
        rgb_refs: List[str],
        sfm_ref: Optional[str] = None,
    ) -> List[ZoneSignature]:
        # Step 1: Map — identify zones and surfaces
        imagery_refs = thermal_refs + rgb_refs
        zones = await self._mapping_agent.map_property(
            property_id=property_id,
            job_id=job_id,
            imagery_refs=imagery_refs,
            sfm_ref=sfm_ref,
        )

        # Step 2: Fuse — compute grime proxy + moisture from thermal+RGB
        enriched = await self._fusion_agent.fuse_zones(
            zones=zones,
            thermal_refs=thermal_refs,
            rgb_refs=rgb_refs,
            sfm_ref=sfm_ref,
        )

        self._assert_no_multispectral_claims(enriched)
        return enriched

    @staticmethod
    def _assert_no_multispectral_claims(zones: List[ZoneSignature]) -> None:
        """Guard: verify no zone claims a multispectral source (§5)."""
        forbidden = set(DataSource) - {DataSource.THERMAL, DataSource.RGB, DataSource.SFM}
        for zone in zones:
            bad = [s for s in zone.source if s in forbidden]
            if bad:
                raise ValueError(
                    f"Zone {zone.zone_id} claims multispectral sources {bad} — "
                    "Autel 640T has no multispectral/NIR bands. See CLAUDE.md §5."
                )
