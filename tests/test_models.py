"""Tests for Pydantic models — schema validation and business rules."""

import pytest
from pydantic import ValidationError

from propwash.backend.models.zone import DataSource, SurfaceType, ZoneSignature
from propwash.backend.models.prescription import ChemicalType, Prescription, CoveragePattern
from propwash.backend.models.work_order import WorkOrder, WorkOrderStatus
from propwash.backend.models.verification import VerificationResult, Verdict


def _zone(**kwargs) -> ZoneSignature:
    defaults = dict(
        zone_id="RF-S",
        label="Roof south",
        surface_type=SurfaceType.COMPOSITE_SHINGLE,
        pitch_deg=32,
        grime_confidence=0.8,
        moisture_index=0.5,
        source=[DataSource.THERMAL, DataSource.RGB],
    )
    defaults.update(kwargs)
    return ZoneSignature(**defaults)


def _prescription(**kwargs) -> Prescription:
    defaults = dict(
        zone_id="RF-S",
        pressure_bar=5.5,
        chemical=ChemicalType.ECO_DEGREASER,
        chemical_mix_ratio=0.35,
        dwell_seconds=35,
        nozzle_id=2,
        standoff_m=1.2,
    )
    defaults.update(kwargs)
    return Prescription(**defaults)


class TestZoneSignature:
    def test_valid_zone(self):
        z = _zone()
        assert z.zone_id == "RF-S"
        assert z.surface_type == SurfaceType.COMPOSITE_SHINGLE

    def test_grime_confidence_bounds(self):
        with pytest.raises(ValidationError):
            _zone(grime_confidence=1.5)
        with pytest.raises(ValidationError):
            _zone(grime_confidence=-0.1)

    def test_pitch_bounds(self):
        with pytest.raises(ValidationError):
            _zone(pitch_deg=91)

    def test_no_multispectral_source(self):
        # DataSource only has thermal/rgb/sfm — enum itself prevents invalid values
        with pytest.raises((ValidationError, ValueError)):
            ZoneSignature(
                zone_id="X",
                label="X",
                surface_type=SurfaceType.STUCCO,
                pitch_deg=0,
                grime_confidence=0.5,
                moisture_index=0.5,
                source=["multispectral"],  # type: ignore
            )


class TestPrescription:
    def test_valid_prescription(self):
        p = _prescription()
        assert p.pressure_bar == 5.5

    def test_pressure_bounds(self):
        with pytest.raises(ValidationError):
            _prescription(pressure_bar=11.0)  # > 10 bar absolute max
        with pytest.raises(ValidationError):
            _prescription(pressure_bar=0.0)  # must be > 0


class TestVerificationResult:
    def test_pass_verdict(self):
        r = VerificationResult.evaluate("RF-S", "job_001", 1, residual_confidence=0.05)
        assert r.verdict == Verdict.PASS

    def test_fail_verdict(self):
        r = VerificationResult.evaluate("RF-S", "job_001", 1, residual_confidence=0.25)
        assert r.verdict == Verdict.FAIL

    def test_at_threshold_is_pass(self):
        r = VerificationResult.evaluate("RF-S", "job_001", 1, residual_confidence=0.15)
        assert r.verdict == Verdict.PASS


class TestWorkOrderRequeue:
    def test_next_attempt_increments(self):
        zone = _zone()
        prescription = _prescription()
        wo = WorkOrder(job_id="job_001", zone=zone, prescription=prescription)
        wo2 = wo.next_attempt(pressure_delta=0.5)
        assert wo2.attempt == 2
        assert wo2.prescription.pressure_bar == pytest.approx(6.0)
        assert wo2.status == WorkOrderStatus.QUEUED
