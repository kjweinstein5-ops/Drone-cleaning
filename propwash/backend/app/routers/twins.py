"""Digital twin API — serves thermographic twin data to the frontend viewer."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from propwash.backend.models.digital_twin import (
    AlertEntry,
    DigitalTwin,
    JobHistoryEntry,
    SoilingRateEstimate,
    ZoneThermalReading,
)

router = APIRouter()

# ── In-memory demo twin (replace with DB query in production) ─────────────────
_DEMO_TWIN = DigitalTwin(
    property_id="prop_carlsbad_bldg_c",
    property_label="Carlsbad Commerce Center — Bldg C",
    address="2200 Faraday Ave, Carlsbad, CA",
    captured_at="2026-06-20T09:14:00Z",
    mesh_ref=None,          # not yet generated — Phase 1 build
    orthomosaic_ref=None,
    total_jobs=3,
    avg_first_pass_rate=0.72,
    zones=[
        ZoneThermalReading(
            zone_id="SOL-ROOF",
            label="Rooftop solar array",
            surface_type="solar_panel",
            pitch_deg=18.0,
            temp_celsius_mean=42.3,
            temp_celsius_min=38.1,
            temp_celsius_max=51.7,
            grime_proxy_pre=0.71,
            grime_proxy_post=0.04,
            moisture_index=0.12,
            human_clear=True,
            human_clear_at=None,
            pressure_prescribed_bar=1.8,
            pressure_actual_bar=1.79,
            verdict="PASS",
            solar=True,
        ),
        ZoneThermalReading(
            zone_id="STUCCO-N",
            label="North façade — stucco",
            surface_type="stucco",
            pitch_deg=90.0,
            temp_celsius_mean=31.5,
            temp_celsius_min=28.9,
            temp_celsius_max=34.2,
            grime_proxy_pre=0.83,
            grime_proxy_post=0.09,
            moisture_index=0.61,
            human_clear=True,
            pressure_prescribed_bar=4.0,
            pressure_actual_bar=3.97,
            verdict="PASS",
            solar=False,
        ),
        ZoneThermalReading(
            zone_id="RF-S",
            label="Roof — south slope",
            surface_type="composite_shingle",
            pitch_deg=38.0,
            temp_celsius_mean=55.8,
            temp_celsius_min=49.3,
            temp_celsius_max=63.1,
            grime_proxy_pre=0.62,
            grime_proxy_post=0.06,
            moisture_index=0.28,
            human_clear=True,
            pressure_prescribed_bar=5.5,
            pressure_actual_bar=5.52,
            verdict="PASS",
            solar=False,
        ),
    ],
    job_history=[
        JobHistoryEntry(
            job_id="job_20260620_001",
            cleaned_at="2026-06-20",
            zones_passed=3,
            zones_failed=0,
            first_pass_rate=0.67,
        ),
        JobHistoryEntry(
            job_id="job_20260312_001",
            cleaned_at="2026-03-12",
            zones_passed=3,
            zones_failed=1,
            first_pass_rate=0.50,
        ),
        JobHistoryEntry(
            job_id="job_20251204_001",
            cleaned_at="2025-12-04",
            zones_passed=3,
            zones_failed=0,
            first_pass_rate=1.00,
        ),
    ],
    soiling_rates=[
        SoilingRateEstimate(
            zone_id="SOL-ROOF",
            weeks_to_threshold=8.2,
            confidence=0.78,
            based_on_visits=3,
        ),
        SoilingRateEstimate(
            zone_id="STUCCO-N",
            weeks_to_threshold=11.4,
            confidence=0.65,
            based_on_visits=3,
        ),
        SoilingRateEstimate(
            zone_id="RF-S",
            weeks_to_threshold=14.1,
            confidence=0.71,
            based_on_visits=3,
        ),
    ],
    alerts=[
        AlertEntry(
            alert_type="HUMAN_DETECTED",
            zone_id="RF-S",
            occurred_at="2026-06-20T09:32:14Z",
            resolved=True,
            detail="Thermal blob detected — operator visually confirmed clear, resumed.",
        ),
        AlertEntry(
            alert_type="RE_QUEUE",
            zone_id="STUCCO-N",
            occurred_at="2026-06-20T10:14:52Z",
            resolved=True,
            detail="First pass FAIL (residual 0.41 > threshold 0.15). Retried at +0.5 bar → PASS.",
        ),
    ],
)

_twins: dict[str, DigitalTwin] = {_DEMO_TWIN.property_id: _DEMO_TWIN}


@router.get("/", response_model=list[dict])
async def list_twins():
    return [
        {"property_id": t.property_id, "property_label": t.property_label,
         "address": t.address, "total_jobs": t.total_jobs}
        for t in _twins.values()
    ]


@router.get("/scan/demo")
async def get_scan_demo():
    """Run the drone-scan pipeline on the synthetic building and return the
    Twin Viewer payload (surface types + grime proxy + exclusion zones), derived
    live from the pipeline — same data the visor renders."""
    from propwash.backend.geometry.source import SyntheticBuildingSource
    from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
    from propwash.backend.fusion.twin_export import scanned_zones_to_view
    from sim.scan_demo import synth_thermal_samples

    source = SyntheticBuildingSource(property_id="sim_carlsbad_bldg_c")
    recon = source.load()
    zones = run_scan_pipeline(source, synth_thermal_samples(recon.faces))
    return scanned_zones_to_view(
        recon, zones,
        property_label="Carlsbad Commerce Center — Bldg C",
        address="2200 Faraday Ave, Carlsbad, CA",
    )


@router.get("/{property_id}", response_model=DigitalTwin)
async def get_twin(property_id: str):
    twin = _twins.get(property_id)
    if not twin:
        raise HTTPException(status_code=404, detail=f"No twin found for property '{property_id}'")
    return twin
