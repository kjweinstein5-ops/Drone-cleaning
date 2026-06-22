"""Tests for the deterministic safety checker — these must always pass.

The safety layer is authoritative (Tier 1 equivalent at software level).
See CLAUDE.md §2.
"""

import pytest
from propwash.backend.models.prescription import ChemicalType, Prescription, CoveragePattern
from propwash.backend.models.zone import SurfaceType
from propwash.backend.safety.checks import SafetyChecker


@pytest.fixture
def checker():
    return SafetyChecker()


def _make_prescription(zone_id="RF-S", **kwargs) -> Prescription:
    defaults = dict(
        zone_id=zone_id,
        pressure_bar=5.5,
        chemical=ChemicalType.ECO_DEGREASER,
        chemical_mix_ratio=0.35,
        dwell_seconds=35,
        nozzle_id=2,
        standoff_m=1.2,
    )
    defaults.update(kwargs)
    return Prescription(**defaults)


class TestPressureCeilings:
    def test_valid_composite_shingle_passes(self, checker):
        p = _make_prescription(pressure_bar=5.5)
        result = checker.check_prescription(p, SurfaceType.COMPOSITE_SHINGLE)
        assert result.passed

    def test_over_ceiling_composite_shingle_fails(self, checker):
        p = _make_prescription(pressure_bar=7.5)  # ceiling is 7.0
        result = checker.check_prescription(p, SurfaceType.COMPOSITE_SHINGLE)
        assert not result.passed
        assert any(v.rule == "PRESSURE_EXCEEDS_HARD_CEILING" for v in result.violations)

    def test_at_ceiling_composite_shingle_passes(self, checker):
        p = _make_prescription(pressure_bar=7.0)
        result = checker.check_prescription(p, SurfaceType.COMPOSITE_SHINGLE)
        assert result.passed


class TestSolarPanelRules:
    def test_solar_valid_di_water(self, checker):
        p = _make_prescription(
            zone_id="SOL-W",
            pressure_bar=1.8,
            chemical=ChemicalType.DI_WATER_ONLY,
            chemical_mix_ratio=0.0,
        )
        result = checker.check_prescription(p, SurfaceType.SOLAR_PANEL)
        assert result.passed

    def test_solar_chemical_blocked(self, checker):
        p = _make_prescription(
            zone_id="SOL-W",
            pressure_bar=1.8,
            chemical=ChemicalType.ECO_DEGREASER,
            chemical_mix_ratio=0.3,
        )
        result = checker.check_prescription(p, SurfaceType.SOLAR_PANEL)
        assert not result.passed
        assert any(v.rule == "SOLAR_PANEL_NO_CHEMICAL" for v in result.violations)

    def test_solar_overpressure_blocked(self, checker):
        p = _make_prescription(
            zone_id="SOL-W",
            pressure_bar=2.5,  # > 2.0 ceiling for solar
            chemical=ChemicalType.DI_WATER_ONLY,
            chemical_mix_ratio=0.0,
        )
        result = checker.check_prescription(p, SurfaceType.SOLAR_PANEL)
        assert not result.passed
        assert any(v.rule == "SOLAR_PANEL_PRESSURE_CEILING" for v in result.violations)

    def test_solar_di_water_nonzero_ratio_blocked(self, checker):
        p = _make_prescription(
            zone_id="SOL-W",
            pressure_bar=1.8,
            chemical=ChemicalType.DI_WATER_ONLY,
            chemical_mix_ratio=0.1,  # must be 0.0 for DI
        )
        result = checker.check_prescription(p, SurfaceType.SOLAR_PANEL)
        assert not result.passed
        assert any(v.rule == "DI_WATER_ONLY_NONZERO_RATIO" for v in result.violations)


class TestUnknownSurface:
    def test_unknown_surface_blocked(self, checker):
        p = _make_prescription()
        result = checker.check_prescription(p, SurfaceType.UNKNOWN)
        assert not result.passed
        assert any(v.rule == "UNKNOWN_SURFACE" for v in result.violations)
