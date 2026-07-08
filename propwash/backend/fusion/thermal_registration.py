"""Stage 2 — Thermal registration (BUILD, this is ours).

Paints radiometric thermal readings onto each mesh face. The photogrammetry
engine only used RGB, so thermal must be projected on separately.

The defensible logic here (docs/3D_DATA_PIPELINE.md §3):
  1. view-angle weighting — a face seen head-on is more trustworthy than one
     seen at a grazing angle, so weight its contribution higher.
  2. reflection rejection — glass/solar reflect sky/sun IR; a face whose
     temperature varies wildly across frames is flagged THERMAL_UNCERTAIN and
     its grime proxy is down-weighted downstream.

The camera ray-casting that produces the per-face samples is a documented seam
(real version: Open3D raycast from thermal camera poses). The aggregation logic
below is the part that is ours and is unit-tested.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Dict, List

# Above this per-face sample stdev (°C) we suspect an IR reflection artifact.
_REFLECTION_STDEV_C = 4.0


@dataclass
class ThermalSample:
    """One observation of one face from one thermal frame."""

    temp_c: float
    view_angle_deg: float  # 0 = head-on (best), 90 = edge-on (worst)


@dataclass
class ThermalFaceReading:
    face_id: str
    temp_c: float                 # view-angle-weighted mean
    temp_min_c: float
    temp_max_c: float
    sample_count: int
    reflection_suspect: bool = False  # THERMAL_UNCERTAIN flag
    stdev_c: float = 0.0


def _view_weight(view_angle_deg: float) -> float:
    """Weight ∝ cos(angle): head-on ~1.0, grazing → 0. Clamped so edge samples
    still count a little (floor 0.05)."""
    import math

    w = math.cos(math.radians(max(0.0, min(90.0, view_angle_deg))))
    return max(0.05, w)


def register_face(face_id: str, samples: List[ThermalSample]) -> ThermalFaceReading:
    """Aggregate all thermal observations of a single face into one reading."""
    if not samples:
        # No thermal coverage — mark uncertain, neutral temperature.
        return ThermalFaceReading(
            face_id=face_id, temp_c=float("nan"), temp_min_c=float("nan"),
            temp_max_c=float("nan"), sample_count=0, reflection_suspect=True,
        )

    temps = [s.temp_c for s in samples]
    weights = [_view_weight(s.view_angle_deg) for s in samples]
    wsum = sum(weights)
    weighted_mean = sum(t * w for t, w in zip(temps, weights)) / wsum

    stdev = statistics.pstdev(temps) if len(temps) > 1 else 0.0
    reflection = stdev > _REFLECTION_STDEV_C

    return ThermalFaceReading(
        face_id=face_id,
        temp_c=round(weighted_mean, 2),
        temp_min_c=round(min(temps), 2),
        temp_max_c=round(max(temps), 2),
        sample_count=len(samples),
        reflection_suspect=reflection,
        stdev_c=round(stdev, 2),
    )


def register_thermal(
    samples_by_face: Dict[str, List[ThermalSample]],
) -> Dict[str, ThermalFaceReading]:
    """Register every face's thermal samples into per-face readings."""
    return {fid: register_face(fid, s) for fid, s in samples_by_face.items()}
