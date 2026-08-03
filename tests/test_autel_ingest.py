"""Tests for Autel scout ingest — frame pairing and co-registered poses."""

from __future__ import annotations

import pytest

from propwash.backend.geometry.autel_ingest import (
    Boresight,
    CameraPose,
    Frame,
    build_survey_capture,
    pair_frames,
)


def _pose(lat=33.128, lon=-117.350, alt=40.0, yaw=90.0, pitch=-45.0):
    return CameraPose(lat=lat, lon=lon, alt_m=alt, yaw_deg=yaw, pitch_deg=pitch)


def _frame(t, sensor, path=None, pose=None):
    return Frame(
        path=path or f"{sensor}_{t}.jpg",
        timestamp=t,
        sensor=sensor,
        pose=pose or _pose(),
    )


def _simultaneous_flight(n=5, jitter=0.02):
    """Both sensors trigger together — the real 4T V2 behaviour."""
    frames = []
    for i in range(n):
        t = 100.0 + i
        frames.append(_frame(t, "rgb"))
        frames.append(_frame(t + jitter, "thermal"))
    return frames


# ── pairing ───────────────────────────────────────────────────────────────────

def test_simultaneous_frames_all_pair():
    pairs, unpaired = pair_frames(_simultaneous_flight(5))
    assert len(pairs) == 5
    assert unpaired == []
    assert all(p.dt_s < 0.05 for p in pairs)


def test_pairs_match_the_nearest_thermal_frame():
    pairs, _ = pair_frames(_simultaneous_flight(3))
    for p in pairs:
        assert p.thermal.timestamp == pytest.approx(p.rgb.timestamp + 0.02)


def test_frame_outside_window_is_left_unpaired_not_forced():
    # A wrong pairing would corrupt the thermal overlay — better to drop it.
    frames = _simultaneous_flight(2)
    frames.append(_frame(500.0, "thermal"))       # orphan, far away in time
    pairs, unpaired = pair_frames(frames)
    assert len(pairs) == 2
    assert len(unpaired) == 1
    assert unpaired[0].timestamp == 500.0


def test_a_thermal_frame_is_never_used_twice():
    frames = [
        _frame(100.0, "rgb"),
        _frame(100.05, "rgb"),      # two RGB close together
        _frame(100.02, "thermal"),  # only one thermal
    ]
    pairs, unpaired = pair_frames(frames)
    assert len(pairs) == 1
    assert len(unpaired) == 1
    assert unpaired[0].sensor == "rgb"


def test_no_thermal_frames_yields_no_pairs():
    pairs, unpaired = pair_frames([_frame(1.0, "rgb"), _frame(2.0, "rgb")])
    assert pairs == []
    assert len(unpaired) == 2


# ── co-registration (the 4T V2 advantage) ─────────────────────────────────────

def test_paired_capture_shares_the_rgb_pose():
    pairs, _ = pair_frames(_simultaneous_flight(1))
    p = pairs[0]
    assert p.pose == p.rgb.pose


def test_thermal_pose_is_rgb_pose_plus_fixed_boresight():
    pairs, _ = pair_frames(_simultaneous_flight(1))
    bs = Boresight(dz_m=0.03, dyaw_deg=0.5, dpitch_deg=-0.2)
    tp = pairs[0].thermal_pose(bs)
    rp = pairs[0].rgb.pose

    # Same position (one gimbal) — only the constant offset differs.
    assert tp.lat == rp.lat and tp.lon == rp.lon
    assert tp.alt_m == pytest.approx(rp.alt_m + 0.03)
    assert tp.yaw_deg == pytest.approx(rp.yaw_deg + 0.5)
    assert tp.pitch_deg == pytest.approx(rp.pitch_deg - 0.2)


def test_zero_boresight_means_identical_poses():
    pairs, _ = pair_frames(_simultaneous_flight(1))
    assert pairs[0].thermal_pose(Boresight()) == pairs[0].rgb.pose


# ── survey capture ────────────────────────────────────────────────────────────

def test_survey_capture_splits_rgb_and_thermal_paths():
    cap = build_survey_capture(
        _simultaneous_flight(4), property_id="prop_1", captured_at="2026-07-06"
    )
    assert len(cap.rgb_paths) == 4
    assert len(cap.thermal_paths) == 4
    # Photogrammetry gets RGB only — thermal can't feature-match.
    assert all(p.startswith("rgb_") for p in cap.rgb_paths)
    assert all(p.startswith("thermal_") for p in cap.thermal_paths)


def test_pair_rate_reports_capture_quality():
    frames = _simultaneous_flight(4)
    frames.append(_frame(900.0, "thermal"))       # one orphan
    cap = build_survey_capture(frames, "prop_1", "2026-07-06")
    assert cap.pair_rate == pytest.approx(8 / 9)


def test_perfect_flight_has_full_pair_rate():
    cap = build_survey_capture(_simultaneous_flight(6), "prop_1", "2026-07-06")
    assert cap.pair_rate == 1.0
