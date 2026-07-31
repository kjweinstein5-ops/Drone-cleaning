"""Tests for FlightPlan → MAVLink mission translation + the safety gate."""

from __future__ import annotations

import math

import pytest

from propwash.backend.execution.mavlink_mission import (
    GeoPoint,
    PressureCeilingExceeded,
    PUMP_CHANNEL,
    PRESSURE_CHANNEL,
    NOZZLE_CHANNEL,
    local_to_geo,
    normalize_nozzle,
    normalize_pressure,
    pump_value,
    translate_flight_plan,
)
from propwash.backend.execution.mavlink_transport import MavlinkPayloadTransport
from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.planning.scan_to_plan import plan_from_scan
from propwash.backend.planning.coverage_path import build_flight_plan
from propwash.backend.safety.checks import SafetyChecker
from propwash.backend.models.zone import SurfaceType
from sim.scan_demo import synth_thermal_samples

DATUM = GeoPoint(lat=33.1281, lon=-117.3506, alt_m=30.0)  # Carlsbad, CA


def _pipeline():
    source = SyntheticBuildingSource()
    recon = source.load()
    zones = run_scan_pipeline(source, synth_thermal_samples(recon.faces))
    plan = plan_from_scan(zones, job_id="job_test", property_id="prop_test")
    flight = build_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    prescriptions = {wo.zone.zone_id: wo.prescription for wo in plan.work_orders}
    surfaces = {wo.zone.zone_id: wo.zone.surface_type for wo in plan.work_orders}
    return flight, prescriptions, surfaces


# ── normalization ─────────────────────────────────────────────────────────────

def test_pressure_normalizes_into_actuator_range():
    assert normalize_pressure(0.0, 5.0) == pytest.approx(-1.0)
    assert normalize_pressure(5.0, 5.0) == pytest.approx(1.0)
    assert normalize_pressure(2.5, 5.0) == pytest.approx(0.0)


def test_pressure_above_ceiling_raises_never_clamps():
    # Safety: an unsafe request must fail loudly, not be silently reduced.
    with pytest.raises(PressureCeilingExceeded):
        normalize_pressure(6.0, 2.0)   # e.g. 6 bar on a solar panel


def test_nozzle_slots_map_across_range():
    assert normalize_nozzle(1, slots=4) == pytest.approx(-1.0)
    assert normalize_nozzle(4, slots=4) == pytest.approx(1.0)
    assert normalize_nozzle(99, slots=4) == pytest.approx(1.0)   # clamped


def test_pump_values():
    assert pump_value(True) == 1.0
    assert pump_value(False) == -1.0


# ── coordinate conversion ─────────────────────────────────────────────────────

def test_local_to_geo_origin_is_datum():
    g = local_to_geo(0, 0, 0, DATUM)
    assert g.lat == pytest.approx(DATUM.lat)
    assert g.lon == pytest.approx(DATUM.lon)
    assert g.alt_m == pytest.approx(DATUM.alt_m)


def test_local_to_geo_north_increases_lat_and_alt_tracks_z():
    g = local_to_geo(0, 100, 5, DATUM)          # 100 m north, 5 m up
    assert g.lat > DATUM.lat
    assert g.alt_m == pytest.approx(DATUM.alt_m + 5)
    # 100 m north ≈ 0.0009 deg latitude
    assert (g.lat - DATUM.lat) == pytest.approx(0.0009, abs=1e-4)


# ── translation ───────────────────────────────────────────────────────────────

def test_translate_emits_items_and_actuators():
    flight, presc, surfaces = _pipeline()
    ceilings = {s.value: SafetyChecker().hard_ceiling_bar(s) for s in set(surfaces.values())}
    mission = translate_flight_plan(flight, presc, ceilings, DATUM)

    assert mission.items, "expected mission items"
    assert mission.spray_items > 0
    # First item of a zone sets nozzle + pressure before spraying.
    first = mission.items[0]
    purposes = {a.purpose for a in first.actuators}
    assert {"nozzle", "pressure"} <= purposes


def test_every_zone_ends_with_pump_off():
    flight, presc, surfaces = _pipeline()
    ceilings = {s.value: SafetyChecker().hard_ceiling_bar(s) for s in set(surfaces.values())}
    mission = translate_flight_plan(flight, presc, ceilings, DATUM)

    by_zone = {}
    for item in mission.items:
        by_zone.setdefault(item.zone_id, []).append(item)
    for zone_id, items in by_zone.items():
        last = items[-1]
        assert last.spraying is False, f"{zone_id} must end not spraying"
        assert any(a.purpose == "pump" and a.value == -1.0 for a in last.actuators)


def test_exclusions_become_geofence_volumes():
    flight, presc, surfaces = _pipeline()
    ceilings = {s.value: SafetyChecker().hard_ceiling_bar(s) for s in set(surfaces.values())}
    mission = translate_flight_plan(flight, presc, ceilings, DATUM)

    ids = {g["zone_id"] for g in mission.geofence_exclusions}
    assert {"HVAC", "CHIMNEY"} <= ids
    for g in mission.geofence_exclusions:
        assert g["radius_m"] > 0


def test_solar_pressure_stays_within_its_ceiling():
    flight, presc, surfaces = _pipeline()
    checker = SafetyChecker()
    ceilings = {s.value: checker.hard_ceiling_bar(s) for s in set(surfaces.values())}
    mission = translate_flight_plan(flight, presc, ceilings, DATUM)

    solar_ceiling = checker.hard_ceiling_bar(SurfaceType.SOLAR_PANEL)
    for item in mission.items:
        if item.zone_id != "SOL-ROOF":
            continue
        for a in item.actuators:
            if a.purpose == "pressure":
                # denormalize back to bar and confirm it's within the ceiling
                bar = (a.value + 1.0) / 2.0 * solar_ceiling
                assert bar <= solar_ceiling + 1e-9


# ── the safety gate on the transport ──────────────────────────────────────────

def test_build_mission_runs_safety_and_works_with_flag_off():
    # Translation is allowed with the flag off so plans can be reviewed on the ground.
    flight, presc, surfaces = _pipeline()
    t = MavlinkPayloadTransport()
    assert t.is_available is False
    mission = t.build_mission(flight, presc, surfaces, DATUM)
    assert mission.items


def test_build_mission_blocks_unsafe_prescription():
    flight, presc, surfaces = _pipeline()
    # Over-pressure the solar zone — the safety gate must refuse to emit anything.
    presc["SOL-ROOF"] = presc["SOL-ROOF"].model_copy(update={"pressure_bar": 6.0})
    t = MavlinkPayloadTransport()
    with pytest.raises(RuntimeError, match="SAFETY BLOCK"):
        t.build_mission(flight, presc, surfaces, DATUM)


def test_hard_ceiling_lookup_matches_table():
    checker = SafetyChecker()
    assert checker.hard_ceiling_bar(SurfaceType.SOLAR_PANEL) == pytest.approx(2.0)
    assert checker.hard_ceiling_bar(SurfaceType.STUCCO) > 2.0
