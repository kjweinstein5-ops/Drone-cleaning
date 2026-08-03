"""Autel EVO MAX 4T V2 ingest — survey capture → pipeline input.

The scout's job is to hand the pipeline **geotagged imagery + camera poses**.
This module models that handoff and implements the part that is genuinely ours:
**pairing the thermal and RGB frames and deriving their poses.**

Why this is simple on the 4T V2 (and hard on a two-aircraft rig): thermal and RGB
share the SAME gimbal, so a paired capture has
  * the same aircraft position,
  * the same gimbal attitude, and
  * effectively the same instant,
differing only by a FIXED, once-measured lens offset (boresight). That turns
cross-sensor registration from an alignment problem into a constant offset —
which is why co-registered sensors matter for Stage 2
(docs/decisions/SENSOR_PLATFORM_SHORTLIST.md §1).

EXIF/XMP extraction is a documented seam (needs Pillow/piexif/exiftool on real
files); the pairing + pose logic below is pure Python and fully tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class CameraPose:
    """Where a frame was taken from, and where it was pointing."""

    lat: float
    lon: float
    alt_m: float          # relative or AMSL, consistent within a flight
    yaw_deg: float        # gimbal heading, 0 = north
    pitch_deg: float      # gimbal pitch, negative = looking down
    roll_deg: float = 0.0


@dataclass(frozen=True)
class Boresight:
    """Fixed geometric offset between the RGB and thermal lenses on one gimbal.

    Measured ONCE per airframe (checkerboard calibration). Because both lenses
    ride the same gimbal, this constant is the entire cross-sensor relationship.
    """

    dx_m: float = 0.0
    dy_m: float = 0.0
    dz_m: float = 0.0
    dyaw_deg: float = 0.0
    dpitch_deg: float = 0.0


@dataclass(frozen=True)
class Frame:
    """One captured image and its metadata."""

    path: str
    timestamp: float
    sensor: str           # "rgb" | "thermal"
    pose: CameraPose
    width: int = 0
    height: int = 0


@dataclass
class PairedCapture:
    """An RGB + thermal pair from the same gimbal at the same instant."""

    rgb: Frame
    thermal: Frame
    dt_s: float

    @property
    def pose(self) -> CameraPose:
        """Shared pose — the RGB frame's, which SfM solves against."""
        return self.rgb.pose

    def thermal_pose(self, boresight: Boresight) -> CameraPose:
        """Thermal camera pose = RGB pose + the fixed boresight offset."""
        p = self.rgb.pose
        return CameraPose(
            lat=p.lat, lon=p.lon,
            alt_m=p.alt_m + boresight.dz_m,
            yaw_deg=p.yaw_deg + boresight.dyaw_deg,
            pitch_deg=p.pitch_deg + boresight.dpitch_deg,
            roll_deg=p.roll_deg,
        )


@dataclass
class SurveyCapture:
    """A complete scout flight, normalised for the pipeline."""

    property_id: str
    captured_at: str
    pairs: List[PairedCapture] = field(default_factory=list)
    unpaired: List[Frame] = field(default_factory=list)
    boresight: Boresight = field(default_factory=Boresight)

    @property
    def rgb_paths(self) -> List[str]:
        """Frames handed to photogrammetry (RGB only — thermal can't feature-match)."""
        return [p.rgb.path for p in self.pairs]

    @property
    def thermal_paths(self) -> List[str]:
        return [p.thermal.path for p in self.pairs]

    @property
    def pair_rate(self) -> float:
        total = len(self.pairs) * 2 + len(self.unpaired)
        return (len(self.pairs) * 2 / total) if total else 0.0


# ── pairing ───────────────────────────────────────────────────────────────────

def pair_frames(
    frames: Sequence[Frame],
    max_dt_s: float = 0.25,
) -> Tuple[List[PairedCapture], List[Frame]]:
    """Pair RGB and thermal frames captured at the same instant.

    Greedy nearest-timestamp matching within `max_dt_s`. Because both sensors are
    on one gimbal and trigger together, real pairs are near-simultaneous; a frame
    with no partner inside the window is returned as unpaired rather than
    force-matched (a wrong pair would corrupt the thermal overlay).
    """
    rgb = sorted((f for f in frames if f.sensor == "rgb"), key=lambda f: f.timestamp)
    thermal = sorted((f for f in frames if f.sensor == "thermal"), key=lambda f: f.timestamp)

    pairs: List[PairedCapture] = []
    used_thermal: set = set()
    ti = 0

    for r in rgb:
        best_idx: Optional[int] = None
        best_dt = max_dt_s
        # advance a window pointer; thermal is time-sorted
        while ti < len(thermal) and thermal[ti].timestamp < r.timestamp - max_dt_s:
            ti += 1
        for j in range(ti, len(thermal)):
            t = thermal[j]
            if t.timestamp > r.timestamp + max_dt_s:
                break
            if j in used_thermal:
                continue
            dt = abs(t.timestamp - r.timestamp)
            if dt <= best_dt:
                best_dt, best_idx = dt, j
        if best_idx is not None:
            used_thermal.add(best_idx)
            pairs.append(PairedCapture(rgb=r, thermal=thermal[best_idx], dt_s=best_dt))

    unpaired = [r for r in rgb if not any(p.rgb is r for p in pairs)]
    unpaired += [t for j, t in enumerate(thermal) if j not in used_thermal]
    return pairs, unpaired


def build_survey_capture(
    frames: Sequence[Frame],
    property_id: str,
    captured_at: str,
    boresight: Optional[Boresight] = None,
    max_dt_s: float = 0.25,
) -> SurveyCapture:
    """Normalise a raw scout flight into the pipeline's SurveyCapture."""
    pairs, unpaired = pair_frames(frames, max_dt_s=max_dt_s)
    return SurveyCapture(
        property_id=property_id,
        captured_at=captured_at,
        pairs=pairs,
        unpaired=unpaired,
        boresight=boresight or Boresight(),
    )


# ── the real-file seam ────────────────────────────────────────────────────────

def load_frames_from_directory(directory: str) -> List[Frame]:  # pragma: no cover
    """Read an Autel flight folder into Frames (EXIF/XMP → CameraPose).

    TODO(PROPWASH): implement with Pillow/piexif (or exiftool) —
      * GPS: EXIF GPSLatitude/GPSLongitude/GPSAltitude
      * gimbal attitude: Autel XMP tags (GimbalYaw/Pitch/RollDegree)
      * timestamp: EXIF DateTimeOriginal + SubSecTime
      * sensor: distinguish thermal (R-JPEG/TIFF) from RGB by tag/dimensions
    Kept as a seam so the pairing/pose logic above is testable with no files.
    """
    raise NotImplementedError(
        "EXIF/XMP ingest not implemented — needs Pillow/piexif and real Autel files. "
        "See docs/decisions/SENSOR_PLATFORM_SHORTLIST.md (confirm programmatic export)."
    )
