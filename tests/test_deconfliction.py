"""Tests for multi-aircraft spatial deconfliction.

The safety property: two aircraft are never scheduled into zones whose operating
volumes come within the minimum separation.
"""

from __future__ import annotations

import pytest

from propwash.backend.models.prescription import ChemicalType, Prescription
from propwash.backend.planning.deconfliction import (
    DEFAULT_MIN_SEPARATION_M,
    ConflictMap,
    ZoneVolume,
    can_work_concurrently,
    separation,
)
from propwash.backend.planning.treatment_phases import (
    TreatmentPhase,
    build_phase_plan,
    schedule_phases,
)


def _vol(zone_id, x, y=0.0, z=0.0, r=3.0):
    return ZoneVolume(zone_id=zone_id, center=(x, y, z), radius_m=r)


def _presc(zone_id, dwell=30):
    return Prescription(
        zone_id=zone_id, pressure_bar=4.0, chemical=ChemicalType.STANDARD_DEGREASER,
        chemical_mix_ratio=0.30, dwell_seconds=dwell, nozzle_id=3, standoff_m=1.0,
    )


# ── volumes & separation ──────────────────────────────────────────────────────

def test_volume_from_points_includes_standoff_and_spray_reach():
    pts = [(0, 0, 0), (4, 0, 0)]
    v = ZoneVolume.from_points("Z", pts, standoff_m=1.0)
    assert v.center == pytest.approx((2.0, 0.0, 0.0))
    assert v.radius_m > 2.0          # extent + standoff + spray reach


def test_separation_is_volume_to_volume_not_centre_to_centre():
    a, b = _vol("A", 0, r=3.0), _vol("B", 20, r=3.0)
    assert separation(a, b) == pytest.approx(20 - 6)


def test_overlapping_volumes_give_negative_separation():
    assert separation(_vol("A", 0, r=5.0), _vol("B", 4, r=5.0)) < 0


def test_far_zones_may_work_concurrently_close_ones_may_not():
    assert can_work_concurrently(_vol("A", 0), _vol("B", 50)) is True
    assert can_work_concurrently(_vol("A", 0), _vol("B", 8)) is False


def test_empty_points_rejected():
    with pytest.raises(ValueError):
        ZoneVolume.from_points("Z", [], standoff_m=1.0)


# ── conflict map ──────────────────────────────────────────────────────────────

def test_conflict_map_flags_close_pairs_only():
    cm = ConflictMap([_vol("A", 0), _vol("B", 8), _vol("C", 60)])
    assert cm.conflicts("A", "B") is True
    assert cm.conflicts("A", "C") is False


def test_a_zone_always_conflicts_with_itself():
    cm = ConflictMap([_vol("A", 0)])
    assert cm.conflicts("A", "A") is True


def test_compatible_with_all_checks_every_active_zone():
    cm = ConflictMap([_vol("A", 0), _vol("B", 60), _vol("C", 8)])
    assert cm.compatible_with_all("B", ["A"]) is True
    assert cm.compatible_with_all("C", ["A"]) is False       # C is close to A


def test_max_concurrent_aircraft_reflects_geometry():
    tight = ConflictMap([_vol("A", 0), _vol("B", 5), _vol("C", 10)])
    spread = ConflictMap([_vol("A", 0), _vol("B", 60), _vol("C", 120)])
    assert tight.max_concurrent_aircraft() == 1
    assert spread.max_concurrent_aircraft() == 3


def test_separation_report_is_waiver_evidence():
    cm = ConflictMap([_vol("A", 0), _vol("B", 60)])
    rows = cm.separation_report()
    assert len(rows) == 1
    assert rows[0]["concurrent_ok"] is True
    assert rows[0]["separation_m"] > DEFAULT_MIN_SEPARATION_M


# ── the safety property, enforced in scheduling ───────────────────────────────

def _plans(ids, dwell=30, pass_s=60.0):
    return [build_phase_plan(z, _presc(z, dwell), pass_s) for z in ids]


def _concurrent_violations(sched, cm):
    """Any two airborne steps overlapping in time on conflicting zones."""
    air = [s for s in sched.steps if s.aircraft is not None]
    bad = []
    for i, a in enumerate(air):
        for b in air[i + 1:]:
            if a.zone_id == b.zone_id:
                continue
            if a.start_s < b.end_s and b.start_s < a.end_s and cm.conflicts(a.zone_id, b.zone_id):
                bad.append((a.zone_id, b.zone_id))
    return bad


def test_scheduler_never_puts_two_aircraft_in_conflicting_zones():
    cm = ConflictMap([_vol("A", 0), _vol("B", 6), _vol("C", 12)])   # all mutually close
    sched = schedule_phases(_plans(["A", "B", "C"]), aircraft_count=3, conflicts=cm)
    assert _concurrent_violations(sched, cm) == []


def test_well_separated_zones_still_run_in_parallel():
    cm = ConflictMap([_vol("A", 0), _vol("B", 80), _vol("C", 160)])
    sched = schedule_phases(_plans(["A", "B", "C"]), aircraft_count=3, conflicts=cm)
    assert _concurrent_violations(sched, cm) == []
    # Separated zones should not be forced into a single-file schedule.
    solo = schedule_phases(_plans(["A", "B", "C"]), aircraft_count=1)
    assert sched.makespan_s < solo.makespan_s


def test_deconfliction_only_delays_never_speeds_up():
    plans = _plans(["A", "B", "C"])
    cm = ConflictMap([_vol("A", 0), _vol("B", 6), _vol("C", 12)])
    free = schedule_phases(plans, aircraft_count=3)
    safe = schedule_phases(plans, aircraft_count=3, conflicts=cm)
    assert safe.makespan_s >= free.makespan_s


def test_all_steps_still_scheduled_under_deconfliction():
    plans = _plans(["A", "B", "C"])
    cm = ConflictMap([_vol("A", 0), _vol("B", 6), _vol("C", 12)])
    sched = schedule_phases(plans, aircraft_count=2, conflicts=cm)
    assert len(sched.steps) == sum(len(p) for p in plans)


def test_dwell_does_not_block_a_conflicting_zone():
    """Dwell occupies no airspace, so it must not gate a neighbour's work."""
    cm = ConflictMap([_vol("A", 0), _vol("B", 6)])
    sched = schedule_phases(_plans(["A", "B"], dwell=120), aircraft_count=2, conflicts=cm)
    dwell = [s for s in sched.steps if s.phase is TreatmentPhase.DWELL]
    assert dwell and all(s.aircraft is None for s in dwell)
    assert _concurrent_violations(sched, cm) == []
