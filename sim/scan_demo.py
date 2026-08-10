"""Drone-scan pipeline demo — runs capture → 3D model → surface types + grime
layer end-to-end on a synthetic building, no hardware required.

    python -m sim.scan_demo
"""

from __future__ import annotations

from typing import Dict, List

from propwash.backend.geometry.source import Face, SyntheticBuildingSource
from propwash.backend.fusion.thermal_registration import ThermalSample
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline, ScannedZone


# Plausible per-surface thermal behaviour for the synthetic scan (°C).
# Multiple samples per face at varying view angles → exercises the weighting +
# reflection-rejection logic. Glass/solar get high-variance samples (IR reflection).
_THERMAL_BY_TRUTH = {
    "composite_shingle": [(52, 5), (55, 20), (54, 35)],
    "stucco":            [(31, 10), (32, 25), (30, 40)],
    "window_glass":      [(28, 10), (41, 25), (22, 40)],   # high variance → reflection
    "solar_panel":       [(38, 5), (39, 20), (37, 35)],
    "exclusion":         [(45, 10), (46, 25), (45, 40)],   # HVAC: warm + uniform
}


#: Peak evaporative-cooling depression (°C) for each soiling mechanism below.
#: SIM ONLY — plausible magnitudes, not measured. Field calibration replaces these.
_RUNOFF_C, _SHADE_C, _EAVE_C = 4.5, 2.5, 3.5


def _soiling_offset_c(face: Face) -> float:
    """How many °C BELOW its class baseline a face reads because water lingers.

    Buildings do not soil uniformly, and the pattern is not random — it follows
    where water sits and how long it takes to leave. Damp surfaces evaporate and
    read cooler, which is precisely the signal thermal gives us (CLAUDE.md §5), so
    the sim encodes the soiling pattern as a temperature depression and lets the
    pipeline infer grime from it rather than being handed a grime number.

    Three mechanisms, all deterministic from geometry:

      1. **Runoff pooling** — water runs down and lingers at the base of walls;
         splash-back off hardscape keeps the bottom metre damp longest.
      2. **Shade** — north elevations (northern hemisphere) never dry fully, which
         is why biofilm shows up there first.
      3. **Eaves** — pitched roofs shed toward the lower edge, so debris and
         biofilm band along the eaves while the field near the ridge stays clean.

    Powered equipment is exempt: an HVAC condenser's thermal signature comes from
    the compressor, not from surface moisture.
    """
    if face.truth_label == "exclusion":
        return 0.0

    _, _, cz = face.sample_at
    normal = face.normal

    # 1. Runoff — strongest at grade, gone by ~3.2 m.
    offset = _RUNOFF_C * max(0.0, 1.0 - cz / 3.2)

    # 2. Shade — scales with how far the face points north (+y).
    offset += _SHADE_C * max(0.0, normal[1])

    # 3. Eaves — pitched surfaces only, banded toward their lower edge.
    if 10.0 <= face.pitch_deg <= 60.0:
        offset += _EAVE_C * max(0.0, min(1.0, (4.8 - cz) / 1.8))

    return offset


def synth_thermal_samples(faces: List[Face]) -> Dict[str, List[ThermalSample]]:
    """Synthesize thermal samples per face from its truth label (sim only).

    Each face gets its class baseline minus its soiling offset, so faces within
    one zone differ — which is what makes the per-face grime layer meaningful.
    """
    out: Dict[str, List[ThermalSample]] = {}
    for f in faces:
        label = f.truth_label or "stucco"
        # The chimney protrusion is caught by geometry, give it wall-like temps.
        key = label if label in _THERMAL_BY_TRUTH else "stucco"
        offset = _soiling_offset_c(f)
        out[f.face_id] = [
            ThermalSample(temp_c=t - offset, view_angle_deg=a)
            for t, a in _THERMAL_BY_TRUTH[key]
        ]
    return out


def main() -> None:
    source = SyntheticBuildingSource(property_id="sim_carlsbad_bldg_c")
    recon = source.load()
    samples = synth_thermal_samples(recon.faces)
    zones: List[ScannedZone] = run_scan_pipeline(source, samples)

    print("\nPROPWASH — drone-scan pipeline (synthetic building)\n")
    print(f"{'ZONE':<12}{'SURFACE':<20}{'PITCH':>6}{'TEMP':>7}{'GRIME':>7}{'CONF':>6}  NOTE")
    print("-" * 88)
    for z in zones:
        tag = "  ⛔ EXCLUDE" if z.is_exclusion else ("  ☀ SOLAR" if z.solar else "")
        temp = f"{z.temp_c:.0f}°" if z.temp_c == z.temp_c else "  -"
        print(
            f"{z.zone_id:<12}{z.surface_type:<20}{z.pitch_deg:>5.0f}°{temp:>7}"
            f"{z.grime_proxy:>7.2f}{z.confidence:>6.2f}{tag}"
        )
    print("-" * 88)
    cleanable = [z for z in zones if not z.is_exclusion]
    excluded = [z for z in zones if z.is_exclusion]
    print(f"\n{len(cleanable)} cleanable zones · {len(excluded)} exclusion zones "
          f"(no spray). grime = PROXY (thermal+RGB, not spectral — CLAUDE.md §5)\n")


if __name__ == "__main__":
    main()
