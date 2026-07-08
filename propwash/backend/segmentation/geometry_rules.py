"""Signal B — deterministic geometry rules (Stage 3).

Facts the mesh gives us that ML can't hallucinate: a vertical plane is a wall or
window, not a roof; a low-slope high face is a candidate roof/solar surface; a
face at ground height on a vertical plane is a ground-floor window. These rules
constrain what the RGB classifier is *allowed* to conclude, and they are
deterministic and auditable — exactly what should feed the safety layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set

from propwash.backend.geometry.source import Face
from propwash.backend.models.zone import SurfaceType


@dataclass
class GeometryConstraints:
    """Which surface classes the geometry permits for a face, plus raw facts."""

    allowed: Set[SurfaceType] = field(default_factory=set)
    pitch_deg: float = 0.0
    height_m: float = 0.0
    is_vertical: bool = False
    is_low_slope: bool = False


def classify_by_geometry(face: Face) -> GeometryConstraints:
    pitch = face.pitch_deg
    height = face.height_m
    is_vertical = pitch >= 70.0
    is_low_slope = pitch <= 25.0

    allowed: Set[SurfaceType] = set()

    if is_vertical:
        # Vertical planes: walls (stucco), windows, or gutters at roofline.
        allowed |= {SurfaceType.STUCCO, SurfaceType.WINDOW_GLASS, SurfaceType.GUTTER_ALUMINUM}
    else:
        # Sloped/flat roof surfaces → roof family. Solar panels mount on pitched
        # AND flat roofs, so solar is permitted on any non-vertical face.
        allowed |= {
            SurfaceType.COMPOSITE_SHINGLE,
            SurfaceType.CLAY_TILE,
            SurfaceType.CONCRETE_TILE,
            SurfaceType.SOLAR_PANEL,
        }

    return GeometryConstraints(
        allowed=allowed,
        pitch_deg=round(pitch, 1),
        height_m=round(height, 2),
        is_vertical=is_vertical,
        is_low_slope=is_low_slope,
    )
