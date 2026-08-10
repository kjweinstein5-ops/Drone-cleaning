"""The drone-scan pipeline — capture → 3D model with surface types + grime layer.

This is the "seamless" orchestration that no off-the-shelf tool provides: it
chains geometry (Stage 1) → thermal registration (Stage 2) → surface segmentation
(Stage 3) into ONE automated job and emits per-zone results with surface type and
a grime PROXY layer. (docs/3D_DATA_PIPELINE.md §2b: the engine is bought; the
seamlessness is built here.)

Pure-Python and runnable on synthetic data — no GPU, drone, or photogrammetry
engine required. Swap SyntheticBuildingSource for SfmSource once real data flows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from propwash.backend.geometry.source import Face, GeometrySource, ReconstructionOutput
from propwash.backend.fusion.thermal_registration import (
    ThermalFaceReading,
    ThermalSample,
    register_thermal,
)
from propwash.backend.segmentation.geometry_rules import classify_by_geometry
from propwash.backend.segmentation.surface_classifier import (
    HeuristicColorClassifier,
    SurfaceClassifier,
)
from propwash.backend.segmentation.fusion_decision import fuse_face
from propwash.backend.models.zone import SurfaceType


@dataclass
class ScannedZone:
    """One cleanable (or excluded) zone extracted from the scan."""

    zone_id: str
    surface_type: str          # SurfaceType value, or "exclusion"
    is_exclusion: bool
    confidence: float
    pitch_deg: float
    temp_c: float
    grime_proxy: float         # PROXY (thermal+RGB), NOT spectral — CLAUDE.md §5
    moisture_index: float
    solar: bool
    face_count: int
    reason: str = ""


def _zone_key(face_id: str) -> str:
    """Group faces into zones. Sim face ids are '<ZONE>-<n>' → strip the suffix.
    The real pipeline clusters mesh regions; grouping by id prefix is the scaffold.
    """
    return face_id.rsplit("-", 1)[0] if "-" in face_id else face_id


#: Temperature depression (°C) below a zone's dry baseline that reads as fully wet.
#: A calibration constant — tune from field data, do not treat as measured.
_MOISTURE_SPAN_C = 8.0


def _grime_proxy(
    thermal: Optional[ThermalFaceReading],
    face: Face,
    baseline_c: Optional[float] = None,
) -> tuple[float, float]:
    """Placeholder grime + moisture PROXY from thermal + RGB darkness.

    IMPORTANT (CLAUDE.md §5): this is an inferred PROXY, not spectral biofilm
    detection. The real calibrated scoring model is a trade secret
    (IP_PROTECTION.md §2) and plugs in behind this function.

    Moisture is read DIFFERENTIALLY when a `baseline_c` is supplied: how far this
    face reads below the driest surface of the same zone. Absolute temperature is
    dominated by sun load, not wetness — a shingle roof at 55°C and a shaded wall
    at 30°C tell you about exposure, not moisture. What indicates damp is a patch
    reading several degrees cooler than the surface around it. Anchoring to an
    absolute room-temperature point instead makes the proxy saturate to zero on
    every sun-loaded roof, which is precisely where the grime is.

    Without a baseline (single-face callers) it falls back to the absolute mapping.
    """
    if thermal is None or thermal.sample_count == 0:
        moisture = 0.5
    elif baseline_c is not None and baseline_c == baseline_c:  # not NaN
        # No depression = as dry as anything else of this material = 0. A zone
        # with one face has no internal contrast and correctly reports 0 here;
        # the score then rests on the RGB staining term alone.
        depression = baseline_c - thermal.temp_c
        moisture = max(0.0, min(1.0, depression / _MOISTURE_SPAN_C))
    else:
        moisture = max(0.0, min(1.0, (30.0 - thermal.temp_c) / 20.0 + 0.5))
    # Staining proxy: darker/greener faces read dirtier (visible staining cue).
    r, g, b = face.rgb_hint or (140, 140, 140)
    darkness = max(0.0, min(1.0, (160 - (r + g + b) / 3.0) / 160.0))
    grime = max(0.0, min(1.0, 0.5 * moisture + 0.5 * darkness))
    return round(grime, 3), round(moisture, 3)


def _zone_baselines(
    recon: ReconstructionOutput,
    thermal: Dict[str, ThermalFaceReading],
) -> Dict[str, float]:
    """Per-zone dry baseline = the warmest face in the zone.

    The warmest same-material surface is the one that has finished drying, so it
    is the reference every other face in that zone is measured against.
    """
    best: Dict[str, float] = {}
    for face in recon.faces:
        r = thermal.get(face.face_id)
        if r is None or r.sample_count == 0 or r.temp_c != r.temp_c:
            continue
        zid = _zone_key(face.face_id)
        if zid not in best or r.temp_c > best[zid]:
            best[zid] = r.temp_c
    return best


@dataclass(frozen=True)
class FaceGrime:
    """The grime PROXY for ONE face — the layer beneath the zone average.

    A zone's headline grime figure is a mean, and a mean hides exactly what
    matters operationally: a roof that is clean across the field but heavily
    soiled along the eaves needs different dwell than one soiled uniformly. The
    per-face layer is what makes that visible (and, later, plannable).

    PROXY, not a spectral measurement (CLAUDE.md §5).
    """

    face_id: str
    zone_id: str
    grime: float
    moisture: float


def grime_layer(
    recon: ReconstructionOutput,
    thermal: Dict[str, ThermalFaceReading],
) -> Dict[str, FaceGrime]:
    """Per-face grime + moisture proxy — the full-resolution layer.

    `run_scan_pipeline` averages this into zones; callers that need the detail
    (the twin viewer, re-queue targeting) read it here instead.
    """
    baselines = _zone_baselines(recon, thermal)
    out: Dict[str, FaceGrime] = {}
    for face in recon.faces:
        zid = _zone_key(face.face_id)
        g, m = _grime_proxy(thermal.get(face.face_id), face, baselines.get(zid))
        out[face.face_id] = FaceGrime(
            face_id=face.face_id,
            zone_id=zid,
            grime=g,
            moisture=m,
        )
    return out


def run_scan_pipeline(
    source: GeometrySource,
    samples_by_face: Dict[str, List[ThermalSample]],
    classifier: Optional[SurfaceClassifier] = None,
) -> List[ScannedZone]:
    """Run the full scan → annotated-zone pipeline."""
    classifier = classifier or HeuristicColorClassifier()
    recon: ReconstructionOutput = source.load()
    thermal = register_thermal(samples_by_face)
    layer = grime_layer(recon, thermal)

    # Per-face: geometry rules + RGB classify + conservative fusion.
    faces_by_zone: Dict[str, List[Face]] = {}
    decision_by_face = {}
    for face in recon.faces:
        geo = classify_by_geometry(face)
        rgb = classifier.classify(face)
        decision = fuse_face(face, rgb, geo, thermal.get(face.face_id))
        decision_by_face[face.face_id] = decision
        faces_by_zone.setdefault(_zone_key(face.face_id), []).append(face)

    # Aggregate faces into zones.
    zones: List[ScannedZone] = []
    for zid, faces in faces_by_zone.items():
        decisions = [decision_by_face[f.face_id] for f in faces]
        is_excl = any(d.is_exclusion for d in decisions)

        temps = [thermal[f.face_id].temp_c for f in faces
                 if f.face_id in thermal and thermal[f.face_id].sample_count > 0]
        mean_temp = round(sum(temps) / len(temps), 2) if temps else float("nan")
        mean_pitch = round(sum(f.pitch_deg for f in faces) / len(faces), 1)

        gm = [(layer[f.face_id].grime, layer[f.face_id].moisture) for f in faces]
        grime = round(sum(g for g, _ in gm) / len(gm), 3)
        moisture = round(sum(m for _, m in gm) / len(gm), 3)

        if is_excl:
            excl_reason = next((d.reason for d in decisions if d.is_exclusion), "")
            zones.append(ScannedZone(
                zone_id=zid, surface_type="exclusion", is_exclusion=True,
                confidence=round(max(d.confidence for d in decisions), 2),
                pitch_deg=mean_pitch, temp_c=mean_temp, grime_proxy=grime,
                moisture_index=moisture, solar=False, face_count=len(faces),
                reason=excl_reason,
            ))
            continue

        # Dominant surface among member faces (conservative: most-sensitive wins).
        surfaces = [d.surface_type for d in decisions if d.surface_type is not None]
        pick = _dominant_surface(surfaces)
        zones.append(ScannedZone(
            zone_id=zid,
            surface_type=pick.value if pick else SurfaceType.UNKNOWN.value,
            is_exclusion=False,
            confidence=round(sum(d.confidence for d in decisions) / len(decisions), 2),
            pitch_deg=mean_pitch, temp_c=mean_temp, grime_proxy=grime,
            moisture_index=moisture, solar=(pick == SurfaceType.SOLAR_PANEL),
            face_count=len(faces),
            reason=decisions[0].reason,
        ))

    zones.sort(key=lambda z: z.zone_id)
    return zones


def _dominant_surface(surfaces: List[SurfaceType]) -> Optional[SurfaceType]:
    from propwash.backend.segmentation.fusion_decision import _most_sensitive
    if not surfaces:
        return None
    # If any face in the zone reads as a pressure-sensitive class, the whole zone
    # inherits it (conservative). Otherwise majority vote.
    sensitive = [s for s in surfaces if s in (SurfaceType.SOLAR_PANEL, SurfaceType.WINDOW_GLASS)]
    if sensitive:
        return _most_sensitive(sensitive)
    return max(set(surfaces), key=surfaces.count)
