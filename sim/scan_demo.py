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


def synth_thermal_samples(faces: List[Face]) -> Dict[str, List[ThermalSample]]:
    """Synthesize thermal samples per face from its truth label (sim only)."""
    out: Dict[str, List[ThermalSample]] = {}
    for f in faces:
        label = f.truth_label or "stucco"
        # The chimney protrusion is caught by geometry, give it wall-like temps.
        key = label if label in _THERMAL_BY_TRUTH else "stucco"
        out[f.face_id] = [ThermalSample(temp_c=t, view_angle_deg=a) for t, a in _THERMAL_BY_TRUTH[key]]
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
