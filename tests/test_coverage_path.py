"""Tests for Stage 5 — coverage / flight-path generation + zone ordering."""

from __future__ import annotations

from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.planning.scan_to_plan import plan_from_scan
from propwash.backend.planning.coverage_path import build_flight_plan
from propwash.backend.planning.zone_ordering import order_zone_ids, order_key
from propwash.backend.models.zone import SurfaceType
from sim.scan_demo import synth_thermal_samples


def _flight():
    source = SyntheticBuildingSource()
    recon = source.load()
    zones = run_scan_pipeline(source, synth_thermal_samples(recon.faces))
    plan = plan_from_scan(zones, job_id="job_test", property_id="prop_test")
    return recon, plan, build_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)


# ── Zone ordering ─────────────────────────────────────────────────────────────

def test_solar_orders_first():
    order = order_zone_ids(
        {"A": SurfaceType.STUCCO, "B": SurfaceType.SOLAR_PANEL, "C": SurfaceType.GUTTER_ALUMINUM},
        {"A": 3.0, "B": 5.0, "C": 3.0},
    )
    assert order[0] == "B"          # solar first
    assert order[-1] == "C"         # gutter last


def test_top_down_within_surface():
    # Same surface: higher zone cleaned first.
    high = order_key(SurfaceType.STUCCO, 6.0)
    low = order_key(SurfaceType.STUCCO, 1.0)
    assert high < low


# ── Flight plan ───────────────────────────────────────────────────────────────

def test_flight_plan_solar_first():
    _, _, flight = _flight()
    assert flight.zone_paths[0].solar is True
    assert flight.zone_paths[0].zone_id == "SOL-ROOF"


def test_every_cleanable_zone_has_a_path():
    _, plan, flight = _flight()
    assert len(flight.zone_paths) == len(plan.work_orders)
    for zp in flight.zone_paths:
        assert len(zp.waypoints) >= 2
        assert zp.path_length_m > 0


def test_keepouts_created_for_exclusions():
    _, _, flight = _flight()
    ids = {ko.zone_id for ko in flight.keep_outs}
    assert {"HVAC", "CHIMNEY"} <= ids
    for ko in flight.keep_outs:
        assert ko.radius_m > 0


def test_no_keepout_violations_on_cleanable_zones():
    # Cleanable zones are offset from exclusion volumes → path avoids them.
    _, _, flight = _flight()
    assert flight.total_keepout_violations == 0


def test_spray_width_scales_with_standoff():
    # Wider standoff and fan angle → wider swath (solar narrow < roof wide).
    _, _, flight = _flight()
    by_id = {zp.zone_id: zp for zp in flight.zone_paths}
    assert by_id["SOL-ROOF"].spray_width_m < by_id["RF-S"].spray_width_m


def test_waypoints_offset_by_standoff():
    # Each waypoint should sit roughly `standoff` off the surface plane, i.e.
    # farther from the building center than the raw surface would be.
    recon, _, flight = _flight()
    sol = next(zp for zp in flight.zone_paths if zp.zone_id == "SOL-ROOF")
    # The solar array sits at z ~3.9-5.1; standoff 0.8 along an upward-ish normal
    # should lift waypoints above the panel surface.
    max_panel_z = 5.1
    assert any(w.z > max_panel_z for w in sol.waypoints)


def test_est_minutes_reasonable():
    _, _, flight = _flight()
    # Whole synthetic building should be tens of minutes, not hundreds.
    assert 5 < flight.est_minutes < 120
