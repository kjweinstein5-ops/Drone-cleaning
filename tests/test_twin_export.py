"""Tests for the pipeline → Twin Viewer export."""

from __future__ import annotations

from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.fusion.twin_export import scanned_zones_to_view
from sim.scan_demo import synth_thermal_samples


def _build_view():
    source = SyntheticBuildingSource()
    recon = source.load()
    zones = run_scan_pipeline(source, synth_thermal_samples(recon.faces))
    return scanned_zones_to_view(recon, zones, "Test Property", "123 Test St")


def test_view_has_zones_and_counts():
    view = _build_view()
    assert view["property"] == "Test Property"
    assert view["zones"], "expected zones in the view"
    assert view["cleanable_count"] + view["exclusion_count"] == len(view["zones"])


def test_view_coords_normalized():
    view = _build_view()
    for z in view["zones"]:
        assert 0.0 <= z["x"] <= 1.0
        assert 0.0 <= z["y"] <= 1.0
        assert 0.0 < z["w"] <= 1.0
        assert 0.0 < z["h"] <= 1.0
        # tile must fit inside the canvas
        assert z["x"] + z["w"] <= 1.001
        assert z["y"] + z["h"] <= 1.001


def test_exclusion_zones_flagged_and_no_post():
    view = _build_view()
    excl = [z for z in view["zones"] if z["is_exclusion"]]
    assert excl, "expected at least one exclusion zone (HVAC/chimney)"
    for z in excl:
        assert z["gPost"] is None  # excluded zones are never cleaned


def test_solar_zone_present():
    view = _build_view()
    solar = [z for z in view["zones"] if z["solar"]]
    assert solar and solar[0]["surface_type"] == "solar_panel"
