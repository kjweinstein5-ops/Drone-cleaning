"""Signal A — RGB surface classification (Stage 3).

Interface + a lightweight scaffold implementation. The production path stands on
an off-the-shelf backbone (Segment Anything for region proposals) with OUR
classifier head trained on OUR labelled San Diego roof dataset — the head and the
dataset are the trade secret (docs/3D_DATA_PIPELINE.md §4). That heavy model plugs
in behind `SurfaceClassifier`; the scaffold below uses coarse colour heuristics so
the pipeline runs with no torch/SAM installed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

from propwash.backend.geometry.source import Face
from propwash.backend.models.zone import SurfaceType


class SurfaceClassifier(ABC):
    @abstractmethod
    def classify(self, face: Face) -> Dict[SurfaceType, float]:
        """Return a probability-ish score per candidate surface class (0..1)."""
        ...


class SamSurfaceClassifier(SurfaceClassifier):
    """Production seam: SAM region proposals + our trained head.

    TODO(PROPWASH): implement with segment-anything + our classifier weights.
    Kept as a documented seam; not used in sim/tests.
    """

    def classify(self, face: Face) -> Dict[SurfaceType, float]:  # pragma: no cover
        raise NotImplementedError("Wire SAM + the trained classifier head here.")


class HeuristicColorClassifier(SurfaceClassifier):
    """Scaffold: classify from the face's coarse mean colour. Deliberately simple
    and NOT the real model — it exists so the full pipeline runs end-to-end.
    """

    def classify(self, face: Face) -> Dict[SurfaceType, float]:
        rgb = face.rgb_hint or (128, 128, 128)
        r, g, b = rgb
        brightness = (r + g + b) / 3.0
        scores: Dict[SurfaceType, float] = {}

        # Very dark + bluish → solar panel (and often confused with HVAC — the
        # conservative fusion + thermal disambiguate that later).
        if brightness < 45:
            scores[SurfaceType.SOLAR_PANEL] = 0.7
            scores[SurfaceType.WINDOW_GLASS] = 0.3
        # Dark, cool-toned, mid brightness → glass.
        elif b > r and brightness < 110:
            scores[SurfaceType.WINDOW_GLASS] = 0.6
            scores[SurfaceType.SOLAR_PANEL] = 0.25
        # Light, warm, matte → stucco.
        elif brightness > 170:
            scores[SurfaceType.STUCCO] = 0.75
        # Mid, warm/brown → shingle/tile roof.
        else:
            scores[SurfaceType.COMPOSITE_SHINGLE] = 0.5
            scores[SurfaceType.CLAY_TILE] = 0.3

        return scores
