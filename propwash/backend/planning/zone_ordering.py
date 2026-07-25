"""Stage 5 — zone sequencing (docs/3D_DATA_PIPELINE.md §5, step 5).

Orders cleanable zones for the flight plan. The sequence encodes real physics and
safety, and the ordering logic is calibration-informed (trade secret):

  1. SOLAR FIRST — clean panels before any detergent is near them (DI-water only;
     detergent overspray degrades output). Panels must precede chemical zones.
  2. TOP-DOWN — gravity carries dirt/runoff downward, so clean high before low
     (roof before façade) to avoid re-soiling cleaned surfaces.
  3. GUTTERS LAST — they collect everything that runs off above them.
"""

from __future__ import annotations

from typing import Dict, List

from propwash.backend.models.zone import SurfaceType

# Lower sort key = cleaned earlier.
_SURFACE_ORDER = {
    SurfaceType.SOLAR_PANEL: 0,       # always first — protect from detergent
    SurfaceType.COMPOSITE_SHINGLE: 2,
    SurfaceType.CLAY_TILE: 2,
    SurfaceType.CONCRETE_TILE: 2,
    SurfaceType.STUCCO: 3,
    SurfaceType.WINDOW_GLASS: 3,
    SurfaceType.GUTTER_ALUMINUM: 5,   # always last — catches runoff from above
}


def order_key(surface_type: SurfaceType, mean_height_m: float) -> tuple:
    """Sort key: (surface priority, then higher surfaces first)."""
    surface_rank = _SURFACE_ORDER.get(surface_type, 4)
    # Negative height so HIGHER zones sort earlier within the same surface rank.
    return (surface_rank, -mean_height_m)


def order_zone_ids(
    zone_surface: Dict[str, SurfaceType],
    zone_height: Dict[str, float],
) -> List[str]:
    """Return zone_ids ordered for the flight plan."""
    return sorted(
        zone_surface.keys(),
        key=lambda zid: order_key(zone_surface[zid], zone_height.get(zid, 0.0)),
    )
