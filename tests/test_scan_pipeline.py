"""Tests for the drone-scan pipeline: geometry → thermal → segmentation.

Covers the safety-critical behaviours: conservative fusion (ambiguous → most
pressure-sensitive), exclusion detection (HVAC, protrusions), and the thermal
registration aggregation (view-angle weighting + reflection rejection).
"""

from __future__ import annotations

import math

from propwash.backend.geometry.source import Face, SyntheticBuildingSource
from propwash.backend.fusion.thermal_registration import (
    ThermalSample,
    register_face,
)
from propwash.backend.segmentation.geometry_rules import classify_by_geometry
from propwash.backend.segmentation.surface_classifier import HeuristicColorClassifier
from propwash.backend.segmentation.fusion_decision import fuse_face
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.models.zone import SurfaceType
from sim.scan_demo import synth_thermal_samples


# ── Thermal registration ──────────────────────────────────────────────────────

def test_view_angle_weighting_favours_head_on():
    # Head-on sample (cool) should pull the mean below a grazing hot sample.
    samples = [
        ThermalSample(temp_c=20.0, view_angle_deg=0.0),   # trusted
        ThermalSample(temp_c=60.0, view_angle_deg=85.0),  # barely weighted
    ]
    reading = register_face("F", samples)
    assert reading.temp_c < 40.0  # closer to the head-on 20 than the midpoint 40


def test_high_variance_flags_reflection():
    samples = [
        ThermalSample(temp_c=22.0, view_angle_deg=10.0),
        ThermalSample(temp_c=41.0, view_angle_deg=20.0),
        ThermalSample(temp_c=28.0, view_angle_deg=30.0),
    ]
    reading = register_face("GLASS", samples)
    assert reading.reflection_suspect is True


def test_no_samples_marks_uncertain():
    reading = register_face("F", [])
    assert reading.sample_count == 0
    assert reading.reflection_suspect is True
    assert math.isnan(reading.temp_c)


# ── Geometry rules ────────────────────────────────────────────────────────────

def test_vertical_face_allows_wall_window_not_roof():
    wall = Face("W", (0, 0, 0), (2, 0, 0), (2, 0, 3))  # vertical
    geo = classify_by_geometry(wall)
    assert geo.is_vertical
    assert SurfaceType.STUCCO in geo.allowed
    assert SurfaceType.WINDOW_GLASS in geo.allowed
    assert SurfaceType.COMPOSITE_SHINGLE not in geo.allowed


def test_pitched_roof_allows_solar():
    roof = Face("R", (0, 0, 3), (4, 0, 3), (4, 2, 4.2))  # ~31° pitch
    geo = classify_by_geometry(roof)
    assert not geo.is_vertical
    assert SurfaceType.SOLAR_PANEL in geo.allowed


# ── Conservative fusion ───────────────────────────────────────────────────────

def test_ambiguous_solar_or_shingle_resolves_to_solar():
    # A dark roof face that RGB thinks could be solar OR shingle must resolve to
    # solar (the most pressure-sensitive) — safety over coverage.
    face = Face("X", (0, 0, 3), (4, 0, 3), (4, 2, 4.2), rgb_hint=(22, 24, 30))
    geo = classify_by_geometry(face)
    rgb = HeuristicColorClassifier().classify(face)
    decision = fuse_face(face, rgb, geo, thermal=None)
    assert decision.surface_type == SurfaceType.SOLAR_PANEL
    assert not decision.is_exclusion


def test_protrusion_is_excluded():
    # Vertical face whose base sits above the roofline → chimney/vent, no spray.
    chimney = Face("C", (7, 4, 6), (8, 4, 6), (8, 4, 7.5), rgb_hint=(120, 90, 80))
    geo = classify_by_geometry(chimney)
    rgb = HeuristicColorClassifier().classify(chimney)
    decision = fuse_face(chimney, rgb, geo, thermal=None)
    assert decision.is_exclusion


# ── End-to-end ────────────────────────────────────────────────────────────────

def test_full_pipeline_on_synthetic_building():
    source = SyntheticBuildingSource()
    recon = source.load()
    samples = synth_thermal_samples(recon.faces)
    zones = run_scan_pipeline(source, samples)

    by_id = {z.zone_id: z for z in zones}

    # Solar array identified and flagged.
    assert by_id["SOL-ROOF"].surface_type == "solar_panel"
    assert by_id["SOL-ROOF"].solar is True

    # HVAC (dark + warm + uniform + flat) excluded, NOT mistaken for solar.
    assert by_id["HVAC"].is_exclusion is True

    # Chimney protrusion excluded.
    assert by_id["CHIMNEY"].is_exclusion is True

    # Walls are stucco; windows are glass.
    assert by_id["WALL-S"].surface_type == "stucco"
    assert by_id["WIN-S1"].surface_type == "window_glass"

    # At least the four walls + windows + roof + solar are cleanable.
    cleanable = [z for z in zones if not z.is_exclusion]
    assert len(cleanable) >= 8


def test_grime_is_proxy_bounded():
    source = SyntheticBuildingSource()
    recon = source.load()
    samples = synth_thermal_samples(recon.faces)
    zones = run_scan_pipeline(source, samples)
    for z in zones:
        assert 0.0 <= z.grime_proxy <= 1.0
        assert 0.0 <= z.moisture_index <= 1.0


# ── differential moisture proxy ───────────────────────────────────────────────

def test_moisture_is_read_against_the_zone_baseline_not_room_temperature():
    """A sun-loaded roof is 50-60°C; an absolute anchor saturates and goes blind.

    What indicates damp is a patch reading cooler than the surface AROUND it, so
    a 6°C depression must register as wet whether the zone sits at 30°C or 55°C.
    """
    from propwash.backend.fusion.scan_pipeline import _grime_proxy
    from propwash.backend.fusion.thermal_registration import ThermalFaceReading
    from propwash.backend.geometry.source import Face

    face = Face("F-0", (0, 0, 0), (1, 0, 0), (1, 1, 0), rgb_hint=(140, 140, 140))

    def moisture(temp, baseline):
        reading = ThermalFaceReading(
            face_id="F-0", temp_c=temp, stdev_c=0.5,
            temp_min_c=temp - 1, temp_max_c=temp + 1,
            sample_count=3, reflection_suspect=False,
        )
        return _grime_proxy(reading, face, baseline)[1]

    hot_dry = moisture(55.0, 55.0)
    hot_damp = moisture(49.0, 55.0)
    cool_dry = moisture(30.0, 30.0)
    cool_damp = moisture(24.0, 30.0)

    assert hot_dry == cool_dry == 0.0            # no depression = no signal
    assert hot_damp > 0.5 and cool_damp > 0.5    # same depression, same reading
    assert hot_damp == cool_damp


def test_absolute_fallback_still_applies_without_a_baseline():
    from propwash.backend.fusion.scan_pipeline import _grime_proxy
    from propwash.backend.fusion.thermal_registration import ThermalFaceReading
    from propwash.backend.geometry.source import Face

    face = Face("F-0", (0, 0, 0), (1, 0, 0), (1, 1, 0), rgb_hint=(140, 140, 140))
    reading = ThermalFaceReading(face_id="F-0", temp_c=20.0, stdev_c=0.5,
                                 temp_min_c=19.0, temp_max_c=21.0,
                                 sample_count=3, reflection_suspect=False)
    assert _grime_proxy(reading, face, None)[1] > 0.5
