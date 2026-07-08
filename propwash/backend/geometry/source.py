"""Geometry source — Stage 1 output of the drone-scan pipeline.

A GeometrySource turns a reconstruction (photogrammetry mesh now, LiDAR later)
into a set of Faces the pipeline reasons over. Keeping this behind one interface
means swapping the *source* (SfM ↔ LiDAR) is a Stage-1-only change
(docs/3D_DATA_PIPELINE.md §8).

This module is pure-Python and dependency-light so the full pipeline runs in the
simulator with no GPU, no drone, and no photogrammetry engine installed. The real
implementations (Metashape/ODM output readers, Open3D mesh ops) plug in behind the
same interface — see TODO markers.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Vec3 = Tuple[float, float, float]


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(a: Vec3) -> float:
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def _unit(a: Vec3) -> Vec3:
    n = _norm(a)
    if n == 0:
        return (0.0, 0.0, 1.0)
    return (a[0] / n, a[1] / n, a[2] / n)


@dataclass
class Face:
    """A single triangular mesh face — the atom of the whole pipeline.

    Geometry is computed from the three vertices; RGB/thermal attributes are
    attached by later stages. `rgb_hint` is a coarse mean colour used by the
    scaffold heuristic classifier; the real pipeline pulls per-face texture.
    """

    face_id: str
    v0: Vec3
    v1: Vec3
    v2: Vec3
    rgb_hint: Optional[Tuple[int, int, int]] = None  # coarse mean colour 0..255
    # Optional ground-truth label used only to synthesise sim data / tests.
    truth_label: Optional[str] = None

    @property
    def centroid(self) -> Vec3:
        return (
            (self.v0[0] + self.v1[0] + self.v2[0]) / 3.0,
            (self.v0[1] + self.v1[1] + self.v2[1]) / 3.0,
            (self.v0[2] + self.v1[2] + self.v2[2]) / 3.0,
        )

    @property
    def normal(self) -> Vec3:
        return _unit(_cross(_sub(self.v1, self.v0), _sub(self.v2, self.v0)))

    @property
    def area(self) -> float:
        return 0.5 * _norm(_cross(_sub(self.v1, self.v0), _sub(self.v2, self.v0)))

    @property
    def pitch_deg(self) -> float:
        """Surface pitch from the face normal. 0 = flat (up), 90 = vertical wall."""
        nz = max(-1.0, min(1.0, abs(self.normal[2])))
        return math.degrees(math.acos(nz))

    @property
    def height_m(self) -> float:
        """Height of the face centroid above the reconstruction ground plane (z=0)."""
        return self.centroid[2]


@dataclass
class ReconstructionOutput:
    """What a photogrammetry (or LiDAR) run yields, normalised for the pipeline."""

    property_id: str
    captured_at: str
    faces: List[Face]
    mesh_ref: Optional[str] = None          # object-storage path to .obj/.glb
    point_cloud_ref: Optional[str] = None   # .laz
    orthomosaic_ref: Optional[str] = None   # .tif
    dsm_ref: Optional[str] = None           # digital surface model .tif
    meta: dict = field(default_factory=dict)


class GeometrySource(ABC):
    """Interface for Stage 1. Implementations: SfM (now), LiDAR (future, §8)."""

    @abstractmethod
    def load(self) -> ReconstructionOutput:
        ...


# ── Real source (seam) ────────────────────────────────────────────────────────

class SfmSource(GeometrySource):
    """Reads a photogrammetry engine's output directory (Metashape / ODM).

    TODO(PROPWASH): implement the real reader — parse the textured .obj mesh into
    Faces (trimesh/Open3D), attach per-face mean colour from the texture, and read
    the DSM/ortho GeoTIFFs (rasterio). Kept as a documented seam so the pipeline
    runs on synthetic data today (see SyntheticBuildingSource).
    """

    def __init__(self, output_dir: str, property_id: str, captured_at: str) -> None:
        self.output_dir = output_dir
        self.property_id = property_id
        self.captured_at = captured_at

    def load(self) -> ReconstructionOutput:  # pragma: no cover - needs real deps/data
        raise NotImplementedError(
            "SfmSource needs trimesh/rasterio + a real reconstruction. "
            "Use SyntheticBuildingSource for sim, or implement the reader."
        )


# ── Synthetic source (runs the whole pipeline with no hardware) ───────────────

class SyntheticBuildingSource(GeometrySource):
    """Generates a simple building (two roof slopes, four walls, a rooftop solar
    array, a chimney, and an HVAC unit) so the full drone-scan pipeline runs
    end-to-end with no GPU, drone, or photogrammetry engine.

    Each face carries a `truth_label` so the sim can synthesise plausible thermal
    and RGB signals downstream — the pipeline itself never reads the truth label.
    """

    def __init__(self, property_id: str = "sim_prop", captured_at: str = "2026-07-06T09:00:00Z") -> None:
        self.property_id = property_id
        self.captured_at = captured_at

    def load(self) -> ReconstructionOutput:
        faces: List[Face] = []

        def quad(prefix: str, a: Vec3, b: Vec3, c: Vec3, d: Vec3, rgb, label: str) -> None:
            faces.append(Face(f"{prefix}-0", a, b, c, rgb_hint=rgb, truth_label=label))
            faces.append(Face(f"{prefix}-1", a, c, d, rgb_hint=rgb, truth_label=label))

        # Roof: south slope + north slope (pitched ~35°), apex along y at x=5
        quad("RF-S", (0, 0, 3), (10, 0, 3), (10, 5, 6), (0, 5, 6), (90, 70, 60), "composite_shingle")
        quad("RF-N", (0, 10, 3), (10, 10, 3), (10, 5, 6), (0, 5, 6), (90, 70, 60), "composite_shingle")

        # Four stucco walls (vertical)
        quad("WALL-S", (0, 0, 0), (10, 0, 0), (10, 0, 3), (0, 0, 3), (210, 200, 185), "stucco")
        quad("WALL-N", (0, 10, 0), (10, 10, 0), (10, 10, 3), (0, 10, 3), (210, 200, 185), "stucco")
        quad("WALL-E", (10, 0, 0), (10, 10, 0), (10, 10, 3), (10, 0, 3), (210, 200, 185), "stucco")
        quad("WALL-W", (0, 0, 0), (0, 10, 0), (0, 10, 3), (0, 0, 3), (210, 200, 185), "stucco")

        # Two windows set into the south wall (specular, dark-ish)
        quad("WIN-S1", (2, 0.01, 1), (4, 0.01, 1), (4, 0.01, 2.5), (2, 0.01, 2.5), (60, 80, 95), "window_glass")
        quad("WIN-S2", (6, 0.01, 1), (8, 0.01, 1), (8, 0.01, 2.5), (6, 0.01, 2.5), (60, 80, 95), "window_glass")

        # Rooftop solar array on the south slope (dark, regular)
        quad("SOL-ROOF", (2, 1, 3.9), (8, 1, 3.9), (8, 3, 5.1), (2, 3, 5.1), (20, 22, 30), "solar_panel")

        # Chimney (vertical protrusion) — EXCLUSION
        quad("CHIMNEY", (7, 4.5, 6), (8, 4.5, 6), (8, 4.5, 7.5), (7, 4.5, 7.5), (120, 90, 80), "exclusion")

        # HVAC unit on flat area — warm, rigid — EXCLUSION (looks solar-ish in RGB)
        quad("HVAC", (1, 6, 3), (2.2, 6, 3), (2.2, 7.2, 3), (1, 7.2, 3), (40, 42, 48), "exclusion")

        return ReconstructionOutput(
            property_id=self.property_id,
            captured_at=self.captured_at,
            faces=faces,
            mesh_ref="sim://mesh",
            meta={"synthetic": True},
        )
