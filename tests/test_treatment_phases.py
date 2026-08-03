"""Tests for multi-phase treatment and dwell pipelining."""

from __future__ import annotations

import pytest

from propwash.backend.models.prescription import ChemicalType, Prescription
from propwash.backend.planning.treatment_phases import (
    ACTIVE_PHASES,
    TreatmentPhase,
    build_phase_plan,
    schedule_phases,
    throughput_gain,
)


def _presc(zone_id="Z", pressure=4.0, chem=ChemicalType.STANDARD_DEGREASER,
           ratio=0.30, dwell=30):
    return Prescription(
        zone_id=zone_id, pressure_bar=pressure, chemical=chem,
        chemical_mix_ratio=ratio, dwell_seconds=dwell, nozzle_id=3,
        standoff_m=1.0,
    )


# ── phase expansion ───────────────────────────────────────────────────────────

def test_plan_has_all_four_phases_in_order():
    steps = build_phase_plan("Z", _presc(), active_pass_seconds=100.0)
    assert [s.phase for s in steps] == [
        TreatmentPhase.PRE_SOAK, TreatmentPhase.CHEMICAL,
        TreatmentPhase.DWELL, TreatmentPhase.RINSE,
    ]


def test_pre_soak_and_rinse_are_water_only():
    steps = build_phase_plan("Z", _presc(), active_pass_seconds=100.0)
    for s in steps:
        if s.phase in (TreatmentPhase.PRE_SOAK, TreatmentPhase.RINSE):
            assert s.chemical is ChemicalType.DI_WATER_ONLY
            assert s.chemical_mix_ratio == 0.0


def test_only_the_chemical_phase_carries_detergent():
    steps = build_phase_plan("Z", _presc(chem=ChemicalType.ECO_DEGREASER, ratio=0.35),
                             active_pass_seconds=100.0)
    chem = next(s for s in steps if s.phase is TreatmentPhase.CHEMICAL)
    assert chem.chemical is ChemicalType.ECO_DEGREASER
    assert chem.chemical_mix_ratio == 0.35


def test_solar_stays_water_only_through_every_phase():
    """DI-water-only surfaces must never see detergent in any phase."""
    steps = build_phase_plan(
        "SOL-ROOF",
        _presc(pressure=1.8, chem=ChemicalType.DI_WATER_ONLY, ratio=0.0, dwell=20),
        active_pass_seconds=90.0,
    )
    assert all(s.chemical is ChemicalType.DI_WATER_ONLY for s in steps)
    assert all(s.chemical_mix_ratio == 0.0 for s in steps)


def test_wet_phases_are_gentler_than_the_prescribed_pressure():
    presc = _presc(pressure=4.0)
    steps = build_phase_plan("Z", presc, active_pass_seconds=100.0)
    for s in steps:
        if s.phase in ACTIVE_PHASES:
            assert 0 < s.pressure_bar <= presc.pressure_bar


def test_dwell_needs_no_aircraft_and_no_pressure():
    steps = build_phase_plan("Z", _presc(dwell=42), active_pass_seconds=100.0)
    dwell = next(s for s in steps if s.phase is TreatmentPhase.DWELL)
    assert dwell.needs_aircraft is False
    assert dwell.pressure_bar == 0.0
    assert dwell.duration_s == 42.0


# ── scheduling ────────────────────────────────────────────────────────────────

def _plans(n, dwell=60, pass_s=60.0):
    return [
        build_phase_plan(f"Z{i}", _presc(zone_id=f"Z{i}", dwell=dwell), pass_s)
        for i in range(n)
    ]


def test_phases_of_a_zone_never_overlap_and_stay_ordered():
    sched = schedule_phases(_plans(3), aircraft_count=2)
    for zone in {s.zone_id for s in sched.steps}:
        zs = sorted((s for s in sched.steps if s.zone_id == zone), key=lambda s: s.start_s)
        order = [s.phase for s in zs]
        assert order == [TreatmentPhase.PRE_SOAK, TreatmentPhase.CHEMICAL,
                         TreatmentPhase.DWELL, TreatmentPhase.RINSE]
        for a, b in zip(zs, zs[1:]):
            assert b.start_s >= a.end_s - 1e-9      # strictly sequential


def test_an_aircraft_only_does_one_thing_at_a_time():
    sched = schedule_phases(_plans(4), aircraft_count=2)
    for ac in range(2):
        busy = sorted((s for s in sched.steps if s.aircraft == ac), key=lambda s: s.start_s)
        for a, b in zip(busy, busy[1:]):
            assert b.start_s >= a.end_s - 1e-9


def test_dwell_occupies_no_aircraft():
    sched = schedule_phases(_plans(3), aircraft_count=2)
    assert all(s.aircraft is None for s in sched.steps if s.phase is TreatmentPhase.DWELL)


def test_second_aircraft_hides_dwell_and_beats_solo():
    """The core claim: pipelining through dwell is faster."""
    plans = _plans(4, dwell=90, pass_s=60.0)
    solo = schedule_phases(plans, 1)
    duo = schedule_phases(plans, 2)
    assert duo.makespan_s < solo.makespan_s
    assert duo.dwell_seconds_hidden > solo.dwell_seconds_hidden


def test_throughput_gain_is_a_speedup():
    plans = _plans(4, dwell=90, pass_s=60.0)
    gain = throughput_gain(plans, aircraft_count=2)
    assert gain > 1.0


def test_extra_aircraft_helps_most_when_work_is_aircraft_bound():
    """Counter-intuitive but correct, and it matters commercially.

    A SECOND aircraft pays off most when the bottleneck is aircraft time (short
    dwell, lots of surface). With very long dwell, dwell sits on every zone's
    critical path and can't be parallelised away — AND a single aircraft already
    hides most dwell by switching to another zone. So the marginal gain from
    aircraft #2 is *lower* when dwell dominates, not higher.

    Business read: buy the second aircraft for AREA, not for dwell.
    """
    aircraft_bound = throughput_gain(_plans(4, dwell=10, pass_s=60.0), 2)
    dwell_bound = throughput_gain(_plans(4, dwell=180, pass_s=60.0), 2)
    assert aircraft_bound > dwell_bound
    assert aircraft_bound > 1.5      # near-linear speed-up when aircraft-bound


def test_one_aircraft_already_hides_dwell_by_switching_zones():
    """Single-aircraft scheduling pipelines across zones on its own."""
    solo = schedule_phases(_plans(4, dwell=120, pass_s=60.0), aircraft_count=1)
    assert solo.dwell_seconds_hidden > 0


def test_single_aircraft_schedule_is_valid():
    sched = schedule_phases(_plans(2), aircraft_count=1)
    assert sched.makespan_s > 0
    assert all(s.aircraft in (0, None) for s in sched.steps)


def test_rejects_zero_aircraft():
    with pytest.raises(ValueError):
        schedule_phases(_plans(1), aircraft_count=0)


def test_every_step_is_scheduled():
    plans = _plans(3)
    sched = schedule_phases(plans, aircraft_count=2)
    assert len(sched.steps) == sum(len(p) for p in plans)
