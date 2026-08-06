"""Tests for phased flight plans and multi-aircraft economics."""

from __future__ import annotations

import pytest

from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.planning.coverage_path import (
    build_flight_plan,
    build_phased_flight_plan,
)
from propwash.backend.planning.scan_to_plan import plan_from_scan
from propwash.backend.planning.treatment_phases import ACTIVE_PHASES, TreatmentPhase
from propwash.backend.reports.revenue_model import (
    Assumptions,
    crew_annual_capacity_revenue,
    crew_annual_capacity_revenue_multi,
    crews_needed_for_target,
    throughput_multiplier,
)
from sim.scan_demo import synth_thermal_samples


def _plan():
    src = SyntheticBuildingSource()
    recon = src.load()
    zones = run_scan_pipeline(src, synth_thermal_samples(recon.faces))
    plan = plan_from_scan(zones, job_id="j", property_id="p")
    return recon, plan


# ── phased flight plans ───────────────────────────────────────────────────────

def test_phased_plan_has_one_pass_per_active_phase():
    recon, plan = _plan()
    base = build_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    assert len(phased.zone_paths) == len(base.zone_paths) * len(ACTIVE_PHASES)


def test_no_pass_is_generated_for_dwell():
    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    assert all(zp.phase != TreatmentPhase.DWELL.value for zp in phased.zone_paths)


def test_phases_appear_in_treatment_order_within_a_zone():
    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    seen: dict = {}
    for zp in phased.zone_paths:
        seen.setdefault(zp.zone_id, []).append(zp.phase)
    expected = [p.value for p in ACTIVE_PHASES]
    for zone, phases in seen.items():
        assert phases == expected, zone


def test_wet_phases_never_exceed_the_approved_pressure():
    """A phased plan can't sneak past what the safety layer approved."""
    recon, plan = _plan()
    approved = {wo.zone.zone_id: wo.prescription.pressure_bar for wo in plan.work_orders}
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    for zp in phased.zone_paths:
        assert zp.phase_pressure_bar <= approved[zp.zone_id] + 1e-9


def test_pre_soak_and_rinse_are_water_only_even_on_chemical_surfaces():
    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    for zp in phased.zone_paths:
        if zp.phase in (TreatmentPhase.PRE_SOAK.value, TreatmentPhase.RINSE.value):
            assert zp.phase_chemical == "di_water_only"


def test_solar_stays_water_only_across_all_phases():
    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    solar = [zp for zp in phased.zone_paths if zp.zone_id == "SOL-ROOF"]
    assert solar
    assert all(zp.phase_chemical == "di_water_only" for zp in solar)
    assert all(zp.phase_pressure_bar <= 2.0 for zp in solar)


def test_label_distinguishes_phase_passes():
    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    labels = {zp.label for zp in phased.zone_paths}
    assert len(labels) == len(phased.zone_paths)     # every pass uniquely labelled
    assert any(":pre_soak" in l for l in labels)


# ── multi-aircraft economics ──────────────────────────────────────────────────

def test_no_waiver_means_no_multiplier():
    """Legally decisive: without 107.35 a second aircraft buys nothing."""
    assert throughput_multiplier(2, waiver_107_35=False) == 1.0
    assert throughput_multiplier(3, waiver_107_35=False) == 1.0


def test_waiver_unlocks_a_gain_below_the_theoretical_max():
    m = throughput_multiplier(2, waiver_107_35=True, eligible_fraction=0.6)
    assert 1.0 < m < 1.91          # blended down by geometry-ineligible jobs


def test_full_eligibility_reaches_the_measured_gain():
    assert throughput_multiplier(2, True, eligible_fraction=1.0) == pytest.approx(1.91)


def test_zero_eligibility_yields_no_gain():
    assert throughput_multiplier(2, True, eligible_fraction=0.0) == pytest.approx(1.0)


def test_more_aircraft_helps_but_is_capped_by_the_model():
    assert throughput_multiplier(3, True, 1.0) > throughput_multiplier(2, True, 1.0)
    # Beyond the measured range the multiplier saturates rather than extrapolating.
    assert throughput_multiplier(9, True, 1.0) == throughput_multiplier(3, True, 1.0)


def test_single_aircraft_and_invalid_inputs():
    assert throughput_multiplier(1, True) == 1.0
    with pytest.raises(ValueError):
        throughput_multiplier(0, True)
    with pytest.raises(ValueError):
        throughput_multiplier(2, True, eligible_fraction=1.5)


def test_capacity_scales_with_the_multiplier():
    a = Assumptions()
    solo = crew_annual_capacity_revenue(a)
    duo = crew_annual_capacity_revenue_multi(a, 2, waiver_107_35=True)
    assert duo > solo
    assert duo == pytest.approx(solo * throughput_multiplier(2, True))


def test_waiver_reduces_the_crews_needed_for_10m():
    """The waiver's real payoff: fewer crews for the same revenue."""
    a = Assumptions(price_per_kw_per_clean=16.0, upsell_uplift_fraction=0.55)
    without = crews_needed_for_target(10_000_000, a, 1, waiver_107_35=False)
    with_waiver = crews_needed_for_target(10_000_000, a, 2, waiver_107_35=True)
    assert with_waiver < without


# ── phased plans through the MAVLink translator ───────────────────────────────

def test_phased_plan_translates_to_a_phase_tagged_mission():
    from propwash.backend.execution.mavlink_mission import GeoPoint
    from propwash.backend.execution.mavlink_transport import MavlinkPayloadTransport

    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    presc = {wo.zone.zone_id: wo.prescription for wo in plan.work_orders}
    surfaces = {wo.zone.zone_id: wo.zone.surface_type for wo in plan.work_orders}

    mission = MavlinkPayloadTransport().build_mission(
        phased, presc, surfaces, GeoPoint(33.1281, -117.3506, 30.0)
    )
    phases = {i.phase for i in mission.items}
    assert phases == {p.value for p in ACTIVE_PHASES}


def test_actuator_pressure_follows_the_phase_not_the_prescription():
    """Pre-soak must actuate gentler than the full cleaning pressure."""
    from propwash.backend.execution.mavlink_mission import GeoPoint
    from propwash.backend.execution.mavlink_transport import MavlinkPayloadTransport

    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    presc = {wo.zone.zone_id: wo.prescription for wo in plan.work_orders}
    surfaces = {wo.zone.zone_id: wo.zone.surface_type for wo in plan.work_orders}
    mission = MavlinkPayloadTransport().build_mission(
        phased, presc, surfaces, GeoPoint(33.1281, -117.3506, 30.0)
    )

    def first_pressure(phase):
        for i in mission.items:
            if i.phase != phase:
                continue
            for a in i.actuators:
                if a.purpose == "pressure":
                    return a.value
        return None

    pre = first_pressure(TreatmentPhase.PRE_SOAK.value)
    rinse = first_pressure(TreatmentPhase.RINSE.value)
    assert pre is not None and rinse is not None
    assert pre < rinse          # pre-soak is the gentlest pass


def test_phase_is_recorded_in_the_engineering_value():
    from propwash.backend.execution.mavlink_mission import GeoPoint
    from propwash.backend.execution.mavlink_transport import MavlinkPayloadTransport

    recon, plan = _plan()
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    presc = {wo.zone.zone_id: wo.prescription for wo in plan.work_orders}
    surfaces = {wo.zone.zone_id: wo.zone.surface_type for wo in plan.work_orders}
    mission = MavlinkPayloadTransport().build_mission(
        phased, presc, surfaces, GeoPoint(33.1281, -117.3506, 30.0)
    )
    eng = [a.engineering_value for i in mission.items for a in i.actuators
           if a.purpose == "pressure"]
    assert any("pre_soak" in e and "di_water_only" in e for e in eng)
