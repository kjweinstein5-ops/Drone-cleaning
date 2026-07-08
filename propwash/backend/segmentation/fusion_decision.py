"""Stage 3 fusion — combine RGB + geometry + thermal into one decision.

The safety principle (docs/3D_DATA_PIPELINE.md §4): conflicts resolve to the
MOST pressure-sensitive class. If a face could be solar or glass, treat it as
such — over-cleaning a stucco wall at a solar-safe pressure wastes a little
time; under-protecting a solar panel destroys it. Safety over coverage.

EXCLUSION detection runs first: HVAC units (warm, uniform, equipment-like) and
protrusions (chimneys/vents) get NO spray. These feed the deterministic safety
layer, not a Claude agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from propwash.backend.geometry.source import Face
from propwash.backend.models.zone import SurfaceType
from propwash.backend.segmentation.geometry_rules import GeometryConstraints
from propwash.backend.fusion.thermal_registration import ThermalFaceReading

# Pressure-sensitivity order — most sensitive first (drives conservative pick).
_SENSITIVITY_ORDER: List[SurfaceType] = [
    SurfaceType.SOLAR_PANEL,
    SurfaceType.WINDOW_GLASS,
    SurfaceType.CLAY_TILE,
    SurfaceType.CONCRETE_TILE,
    SurfaceType.STUCCO,
    SurfaceType.COMPOSITE_SHINGLE,
    SurfaceType.GUTTER_ALUMINUM,
]

# A dark/equipment-looking, warm, uniform, flat face is powered equipment (HVAC).
_HVAC_WARM_C = 40.0
# A vertical face whose base sits above the roofline is a protrusion (chimney/vent).
_PROTRUSION_HEIGHT_M = 4.0


@dataclass
class FaceDecision:
    face_id: str
    surface_type: Optional[SurfaceType]  # None when excluded
    is_exclusion: bool
    confidence: float
    reason: str
    contributing: List[str] = field(default_factory=list)


def fuse_face(
    face: Face,
    rgb_scores: Dict[SurfaceType, float],
    geometry: GeometryConstraints,
    thermal: Optional[ThermalFaceReading],
) -> FaceDecision:
    # ── EXCLUSION checks first (safety) ──────────────────────────────────────
    # 1. Protrusion (chimney/vent): vertical face above the roofline.
    if geometry.is_vertical and geometry.height_m > _PROTRUSION_HEIGHT_M:
        return FaceDecision(
            face.face_id, None, True, 0.9,
            reason=f"Protrusion above roofline ({geometry.height_m} m) — no spray.",
            contributing=["geometry"],
        )

    # 2. HVAC / powered equipment: RGB reads dark-equipment (solar-like), thermal
    #    is warm + uniform, and it sits flat (not a pitched roof panel).
    rgb_top = max(rgb_scores, key=rgb_scores.get) if rgb_scores else None
    if (
        rgb_top == SurfaceType.SOLAR_PANEL
        and thermal is not None
        and not thermal.reflection_suspect
        and thermal.sample_count > 0
        and thermal.temp_c >= _HVAC_WARM_C
        and thermal.stdev_c < 3.0
        and geometry.is_low_slope
    ):
        return FaceDecision(
            face.face_id, None, True, 0.75,
            reason=(
                f"Warm ({thermal.temp_c}°C), uniform, flat, equipment-like — "
                "likely HVAC. Excluded from spray."
            ),
            contributing=["rgb", "thermal", "geometry"],
        )

    # ── Viable classes = RGB candidates permitted by geometry ────────────────
    viable = {s: p for s, p in rgb_scores.items() if s in geometry.allowed}
    if not viable:
        # RGB and geometry disagree entirely → fall back to the most conservative
        # class geometry allows, flagged low-confidence for review.
        if geometry.allowed:
            pick = _most_sensitive(list(geometry.allowed))
            return FaceDecision(
                face.face_id, pick, False, 0.3,
                reason="RGB/geometry disagree — conservative geometry fallback.",
                contributing=["geometry"],
            )
        return FaceDecision(
            face.face_id, SurfaceType.UNKNOWN, False, 0.1,
            reason="No viable class — needs manual review.", contributing=[],
        )

    # ── Conservative pick ────────────────────────────────────────────────────
    # If any pressure-sensitive class is viable at all, take the MOST sensitive
    # one — do not let a higher RGB score for a tougher surface override safety.
    pick = _most_sensitive(list(viable.keys()))
    conf = viable[pick]
    contributing = ["rgb", "geometry"]
    if thermal is not None and thermal.sample_count > 0:
        contributing.append("thermal")
    return FaceDecision(
        face.face_id, pick, False, round(conf, 2),
        reason=f"Conservative pick among viable {sorted(s.value for s in viable)}.",
        contributing=contributing,
    )


def _most_sensitive(classes: List[SurfaceType]) -> SurfaceType:
    for s in _SENSITIVITY_ORDER:
        if s in classes:
            return s
    return classes[0]
