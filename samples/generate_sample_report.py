"""Generate a sample ROI report so you can see the sales weapon in action.

Run: python -m samples.generate_sample_report
Opens samples/sample_roi_report.html
"""

from __future__ import annotations

import os
from datetime import date

from propwash.backend.models.verification import Verdict
from propwash.backend.models.zone import SurfaceType
from propwash.backend.reports.roi_report import (
    ROIReport,
    SolarROIInput,
    ZoneResult,
    generate_html_report,
)


def build_sample() -> ROIReport:
    return ROIReport(
        property_name="Carlsbad Commerce Center — Building C",
        property_address="2200 Faraday Ave, Carlsbad, CA 92008",
        job_id="job_20260622_001",
        job_date=date(2026, 6, 22),
        zones=[
            ZoneResult(
                zone_id="SOL-ROOF",
                label="Rooftop solar array",
                surface_type=SurfaceType.SOLAR_PANEL,
                pre_grime_confidence=0.78,
                post_residual_confidence=0.06,
                verdict=Verdict.PASS,
                solar=SolarROIInput(
                    system_kw=120.0,
                    annual_kwh_per_kw=1600.0,
                    electricity_price_per_kwh=0.32,
                    months_until_resoil=6,
                ),
            ),
            ZoneResult(
                zone_id="SOL-CANOPY",
                label="Parking canopy solar",
                surface_type=SurfaceType.SOLAR_PANEL,
                pre_grime_confidence=0.64,
                post_residual_confidence=0.08,
                verdict=Verdict.PASS,
                solar=SolarROIInput(
                    system_kw=85.0,
                    annual_kwh_per_kw=1650.0,
                    electricity_price_per_kwh=0.32,
                    months_until_resoil=6,
                ),
            ),
            ZoneResult(
                zone_id="STUCCO-N",
                label="North façade — stucco",
                surface_type=SurfaceType.STUCCO,
                pre_grime_confidence=0.71,
                post_residual_confidence=0.10,
                verdict=Verdict.PASS,
            ),
        ],
    )


def main() -> None:
    report = build_sample()
    html_out = generate_html_report(report)
    out_path = os.path.join(os.path.dirname(__file__), "sample_roi_report.html")
    with open(out_path, "w") as f:
        f.write(html_out)
    print(f"Wrote {out_path}")
    print(f"Estimated recovered value: ${report.total_recovered_value():,.0f}")
    print(f"Estimated recovered output: {report.total_recovered_kwh():,.0f} kWh")
    print(f"Zones verified clean: {report.zones_passed()}/{len(report.zones)}")


if __name__ == "__main__":
    main()
