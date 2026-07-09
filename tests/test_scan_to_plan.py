"""Tests for the scan → plan bridge.

The three guarantees that matter (CLAUDE.md §2):
  1. exclusion zones never become work orders,
  2. every cleanable zone gets a table-driven prescription,
  3. every queued work order passed the deterministic safety gate.
"""

from __future__ import annotations

import pytest

from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.fusion.scan_pipeline import ScannedZone, run_scan_pipeline
from propwash.backend.planning.prescriber import (
    TablePrescriber,
    scanned_zone_to_signature,
)
from propwash.backend.planning.scan_to_plan import plan_from_scan
from propwash.backend.models.prescription import ChemicalType
from propwash.backend.models.zone import SurfaceType
from propwash.backend.safety.checks import SafetyChecker
from sim.scan_demo import synth_thermal_samples


def _scan():
    source = SyntheticBuildingSource()
    recon = source.load()
    return run_scan_pipeline(source, synth_thermal_samples(recon.faces))


def _plan():
    return plan_from_scan(_scan(), job_id="job_test", property_id="prop_test")


# ── Guarantee 1: exclusions never queued ──────────────────────────────────────

def test_exclusion_zones_never_become_work_orders():
    plan = _plan()
    queued_ids = {wo.zone.zone_id for wo in plan.work_orders}
    assert "HVAC" not in queued_ids
    assert "CHIMNEY" not in queued_ids
    excluded_ids = {zid for zid, _ in plan.excluded}
    assert {"HVAC", "CHIMNEY"} <= excluded_ids


def test_signature_conversion_rejects_exclusion():
    excl = ScannedZone(
        zone_id="HVAC", surface_type="exclusion", is_exclusion=True, confidence=0.75,
        pitch_deg=0, temp_c=45, grime_proxy=0.3, moisture_index=0.0, solar=False,
        face_count=2, reason="HVAC",
    )
    with pytest.raises(ValueError):
        scanned_zone_to_signature(excl, "prop", "job")


# ── Guarantee 2: table-driven prescriptions ───────────────────────────────────

def test_solar_zone_prescribed_di_water_low_pressure():
    plan = _plan()
    solar = next(wo for wo in plan.work_orders if wo.zone.zone_id == "SOL-ROOF")
    assert solar.prescription.chemical == ChemicalType.DI_WATER_ONLY
    assert solar.prescription.pressure_bar <= 2.0
    assert solar.prescription.chemical_mix_ratio == 0.0


def test_grime_proxy_carried_into_signature():
    zones = _scan()
    cleanable = next(z for z in zones if not z.is_exclusion)
    sig = scanned_zone_to_signature(cleanable, "prop", "job")
    assert sig.grime_confidence == cleanable.grime_proxy


# ── Guarantee 3: safety gate integrity ────────────────────────────────────────

def test_every_queued_work_order_passes_safety():
    plan = _plan()
    safety = SafetyChecker()
    for wo in plan.work_orders:
        result = safety.check_prescription(wo.prescription, wo.zone.surface_type)
        assert result.passed, f"{wo.zone.zone_id} queued but fails safety"


def test_cleanable_count_matches_and_none_rejected_on_defaults():
    plan = _plan()
    zones = _scan()
    cleanable = [z for z in zones if not z.is_exclusion]
    # Default table prescriptions are all within ceilings → nothing rejected.
    assert plan.safety_rejected == []
    assert len(plan.work_orders) == len(cleanable)


def test_unsafe_prescription_is_rejected_not_queued():
    # A prescriber that over-pressures solar must be caught by the safety gate.
    class BadPrescriber(TablePrescriber):
        def prescribe(self, signature):
            presc = super().prescribe(signature)
            if signature.surface_type == SurfaceType.SOLAR_PANEL:
                return presc.model_copy(update={"pressure_bar": 6.0})  # way over 2.0 ceiling
            return presc

    plan = plan_from_scan(
        _scan(), job_id="job_bad", property_id="prop", prescriber=BadPrescriber()
    )
    queued_ids = {wo.zone.zone_id for wo in plan.work_orders}
    assert "SOL-ROOF" not in queued_ids
    assert any(zid == "SOL-ROOF" for zid, _ in plan.safety_rejected)
