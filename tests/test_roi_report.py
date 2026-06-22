"""Tests for the ROI report generator (the sales weapon)."""

from datetime import date

import pytest

from propwash.backend.models.verification import Verdict
from propwash.backend.models.zone import SurfaceType
from propwash.backend.reports.roi_report import (
    ROIReport,
    SolarROIInput,
    ZoneResult,
    generate_html_report,
)


def _solar_zone(pre=0.8, post=0.05, kw=100.0):
    return ZoneResult(
        zone_id="SOL-1",
        label="Solar array",
        surface_type=SurfaceType.SOLAR_PANEL,
        pre_grime_confidence=pre,
        post_residual_confidence=post,
        verdict=Verdict.PASS,
        solar=SolarROIInput(
            system_kw=kw,
            annual_kwh_per_kw=1600.0,
            electricity_price_per_kwh=0.30,
            months_until_resoil=6,
        ),
    )


class TestSoilingMetrics:
    def test_soiling_removed_pct(self):
        z = _solar_zone(pre=0.80, post=0.05)
        assert z.soiling_removed_pct == 75.0

    def test_soiling_removed_never_negative(self):
        z = _solar_zone(pre=0.10, post=0.30)  # residual higher than pre (shouldn't happen)
        assert z.soiling_removed_pct == 0.0


class TestSolarRecovery:
    def test_recovered_kwh_positive(self):
        z = _solar_zone(pre=0.80, post=0.05, kw=100.0)
        # recovered loss fraction = 0.75 * 0.20 = 0.15
        # annual kwh = 100 * 1600 = 160000; horizon = 0.5 yr
        # recovered = 160000 * 0.15 * 0.5 = 12000 kWh
        assert z.estimated_recovered_kwh() == pytest.approx(12000.0)

    def test_recovered_value(self):
        z = _solar_zone(pre=0.80, post=0.05, kw=100.0)
        assert z.estimated_recovered_value() == pytest.approx(12000.0 * 0.30)

    def test_non_solar_recovers_nothing(self):
        z = ZoneResult(
            zone_id="STUCCO-N",
            label="Stucco",
            surface_type=SurfaceType.STUCCO,
            pre_grime_confidence=0.7,
            post_residual_confidence=0.1,
            verdict=Verdict.PASS,
        )
        assert z.estimated_recovered_kwh() == 0.0
        assert z.estimated_recovered_value() == 0.0


class TestReportRendering:
    def test_report_totals(self):
        report = ROIReport(
            property_name="Test Property",
            property_address="123 Test St",
            job_id="job_test_001",
            job_date=date(2026, 6, 22),
            zones=[_solar_zone(), _solar_zone()],
        )
        assert report.total_recovered_kwh() > 0
        assert report.zones_passed() == 2

    def test_html_contains_key_fields(self):
        report = ROIReport(
            property_name="Carlsbad Center",
            property_address="2200 Faraday Ave",
            job_id="job_001",
            job_date=date(2026, 6, 22),
            zones=[_solar_zone()],
        )
        out = generate_html_report(report)
        assert "Carlsbad Center" in out
        assert "PROPWASH" in out
        assert "estimates" in out.lower()  # honesty disclaimer present
        assert "<!DOCTYPE html>" in out
