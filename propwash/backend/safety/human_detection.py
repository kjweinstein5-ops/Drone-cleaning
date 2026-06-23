"""Deterministic human presence detector — pre-pass safety clearance.

Runs on thermal frame data BEFORE any cleaning pass is dispatched.
Tier 1 safety layer — NOT a Claude agent. Detection thresholds are
constants, not runtime config, so no agent or misconfiguration can
silently lower the sensitivity.

Algorithm: connected-component blob detection in the human temperature
range + shape/area filter. No ML model — intentionally deterministic
for auditability and liability documentation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Hard detection constants (never configurable at runtime) ──────────────────
_HUMAN_TEMP_MIN_C: float = 29.0    # lower on cold days / heavy clothing
_HUMAN_TEMP_MAX_C: float = 40.0    # fever upper bound

# Human figure viewed from drone altitude (~10–20 m AGL)
_HUMAN_AREA_MIN_M2: float = 0.10   # prone / compressed
_HUMAN_AREA_MAX_M2: float = 1.60   # standing, arms-out from 15 m

_HUMAN_ASPECT_MIN: float = 1.0     # standing directly below: roughly square
_HUMAN_ASPECT_MAX: float = 5.5     # prone / stretched out
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ThermalBlob:
    center_x: float       # metres from frame origin
    center_y: float
    area_m2: float
    mean_temp_c: float
    aspect_ratio: float   # long_side / short_side of bounding box
    pixel_count: int


@dataclass
class HumanDetectionResult:
    cleared: bool
    blobs_detected: List[ThermalBlob] = field(default_factory=list)
    reason: str = ""

    @property
    def halt(self) -> bool:
        return not self.cleared


def detect_human_presence(
    thermal_pixels: List[List[float]],
    pixel_size_m: float = 0.05,
    surface_temp_c: Optional[float] = None,
) -> HumanDetectionResult:
    """Run the pre-pass human presence check on a 2D thermal frame.

    Two detection modes:
    - Normal (morning): human WARMER than background → warm blob detection.
    - Afternoon (hot roof >50°C): human COOLER than surface → cool blob detection.

    Returns cleared=True only when no blob matches both the temperature range
    AND the human-shape/area filter. Ambiguous or empty frames return cleared=False.
    """
    if not thermal_pixels or not thermal_pixels[0]:
        logger.warning("human_detection: empty thermal frame — returning UNCLEAR")
        return HumanDetectionResult(
            cleared=False,
            reason="Empty thermal frame — cannot confirm zone is clear of people.",
        )

    rows = len(thermal_pixels)
    cols = len(thermal_pixels[0])

    # In afternoon-sun mode the human is cooler than a very hot surface.
    if surface_temp_c is not None and surface_temp_c > 50.0:
        t_min = _HUMAN_TEMP_MIN_C
        t_max = min(_HUMAN_TEMP_MAX_C, surface_temp_c - 8.0)
    else:
        t_min = _HUMAN_TEMP_MIN_C
        t_max = _HUMAN_TEMP_MAX_C

    blobs = _connected_components(thermal_pixels, rows, cols, pixel_size_m, t_min, t_max)
    candidates = [b for b in blobs if _is_human_shaped(b)]

    if candidates:
        logger.warning(
            "human_detection: %d human candidate blob(s) — HALT dispatch",
            len(candidates),
        )
        return HumanDetectionResult(
            cleared=False,
            blobs_detected=candidates,
            reason=(
                f"{len(candidates)} thermal blob(s) match human presence criteria "
                f"(temp {t_min}–{t_max}°C, area {_HUMAN_AREA_MIN_M2}–"
                f"{_HUMAN_AREA_MAX_M2} m²). Operator must visually confirm zone "
                "is clear before proceeding."
            ),
        )

    return HumanDetectionResult(
        cleared=True,
        reason="No human-range thermal signature detected in zone.",
    )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _connected_components(
    pixels: List[List[float]],
    rows: int,
    cols: int,
    pixel_size_m: float,
    t_min: float,
    t_max: float,
) -> List[ThermalBlob]:
    mask = [[t_min <= pixels[r][c] <= t_max for c in range(cols)] for r in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    blobs: List[ThermalBlob] = []

    for sr in range(rows):
        for sc in range(cols):
            if not mask[sr][sc] or visited[sr][sc]:
                continue
            component: List[Tuple[int, int]] = []
            queue = [(sr, sc)]
            while queue:
                r, c = queue.pop()
                if r < 0 or r >= rows or c < 0 or c >= cols:
                    continue
                if visited[r][c] or not mask[r][c]:
                    continue
                visited[r][c] = True
                component.append((r, c))
                queue.extend([(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)])

            if len(component) < 4:
                continue

            rs = [p[0] for p in component]
            cs_all = [p[1] for p in component]
            temps = [pixels[p[0]][p[1]] for p in component]

            h_px = max(rs) - min(rs) + 1
            w_px = max(cs_all) - min(cs_all) + 1
            long_side = max(h_px, w_px)
            short_side = max(min(h_px, w_px), 1)

            blobs.append(ThermalBlob(
                center_x=(min(cs_all) + max(cs_all)) / 2 * pixel_size_m,
                center_y=(min(rs) + max(rs)) / 2 * pixel_size_m,
                area_m2=len(component) * pixel_size_m ** 2,
                mean_temp_c=sum(temps) / len(temps),
                aspect_ratio=long_side / short_side,
                pixel_count=len(component),
            ))

    return blobs


def _is_human_shaped(blob: ThermalBlob) -> bool:
    return (
        _HUMAN_AREA_MIN_M2 <= blob.area_m2 <= _HUMAN_AREA_MAX_M2
        and _HUMAN_ASPECT_MIN <= blob.aspect_ratio <= _HUMAN_ASPECT_MAX
    )
