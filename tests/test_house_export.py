"""The synthetic house and the twin export that drives the visor + 3D artifact.

The house is the demo structure everything visual is built on, so these tests
guard the two things that silently break it: a mesh that isn't closed, and an
export whose numbers drift from the pipeline that produced them.
"""

from __future__ import annotations

import pytest

from propwash.backend.geometry.source import SyntheticHouseSource
from propwash.backend.models.zone import SurfaceType
from sim.export_house_3d import build_view


@pytest.fixture(scope="module")
def view() -> dict:
    return build_view()


# ── geometry ──────────────────────────────────────────────────────────────────

def test_every_face_id_carries_a_zone_suffix():
    """`_zone_key` strips after the last '-', so a bare prefix merges zones."""
    for f in SyntheticHouseSource().load().faces:
        prefix, _, suffix = f.face_id.rpartition("-")
        assert prefix and suffix.isdigit(), f.face_id


def test_gable_ends_stay_separate_zones(view):
    """GABLE-W and GABLE-E must not collapse into a single 'GABLE'."""
    assert {"GABLE-W", "GABLE-E"} <= set(view["zones"])
    assert "GABLE" not in view["zones"]


def test_the_garage_is_a_closed_volume(view):
    """A missing gable end leaves a hole you can see straight through."""
    for wall in ("GAR-WALL-S", "GAR-WALL-E", "GAR-WALL-N", "GAR-GABLE-E"):
        assert wall in view["zones"], wall


def test_no_face_sits_below_ground():
    assert all(v[2] >= 0.0 for f in SyntheticHouseSource().load().faces
               for v in (f.v0, f.v1, f.v2))


# ── classification ────────────────────────────────────────────────────────────

def test_the_hvac_condenser_is_excluded_not_mistaken_for_solar(view):
    """Dark flat equipment reads panel-like in RGB; thermal has to catch it."""
    hvac = view["zones"]["HVAC"]
    assert hvac["excl"] is True
    assert hvac["surf"] != SurfaceType.SOLAR_PANEL.value


def test_the_chimney_is_excluded(view):
    assert view["zones"]["CHIMNEY"]["excl"] is True


def test_solar_is_water_only_under_the_ceiling_in_every_phase(view):
    solar = view["zones"]["SOL-ROOF"]
    assert solar["solar"] is True
    assert solar["chem"] == "di_water_only"
    for step in view["phases"]["SOL-ROOF"]:
        assert step["c"] == "di_water_only"
        assert step["p"] <= 2.0


def test_pre_soak_and_rinse_are_water_only_everywhere(view):
    for zone, steps in view["phases"].items():
        for s in steps:
            if s["ph"] in ("pre_soak", "rinse"):
                assert s["c"] == "di_water_only", zone


# ── export shape ──────────────────────────────────────────────────────────────

def test_counts_match_the_payload(view):
    c = view["counts"]
    assert c["faces"] == len(view["faces"])
    assert c["zones"] == len(view["zones"])
    assert c["passes"] == sum(len(v) for v in view["phases"].values())
    assert c["clean"] + c["excl"] == c["zones"]


def test_only_cleanable_zones_carry_a_prescription(view):
    for zid, z in view["zones"].items():
        assert (z["p"] is None) == z["excl"], zid
        assert (zid in view["phases"]) != z["excl"], zid


def test_deconfliction_never_reports_a_gain_it_cannot_deliver(view):
    """The honest half of the fleet story: `schedule` respects geometry.

    With max concurrency of 1 the deconflicted schedule must be flat, even
    though the geometry-free `scheduleIdeal` shows what pipelining could reach.
    """
    real, ideal = view["schedule"], view["scheduleIdeal"]
    assert set(real) == set(ideal)
    assert all(real[n] >= ideal[n] for n in real)
    if view["maxConcurrent"] == 1:
        assert len(set(real.values())) == 1
        assert ideal["2"] < ideal["1"]      # the potential is real, just unreachable here


def test_every_zone_has_a_human_label(view):
    for zid, z in view["zones"].items():
        assert z["label"] and z["label"] != zid, zid


# ── per-face grime layer (what zoom resolves) ─────────────────────────────────

def test_faces_carry_their_own_grime_not_the_zone_mean(view):
    """If every face got the zone average, zooming in would reveal nothing."""
    by_zone: dict[str, set] = {}
    for f in view["faces"]:
        by_zone.setdefault(f["zone"], set()).add(f["g"])
    varied = [z for z, vals in by_zone.items() if len(vals) > 1]
    assert varied, "no zone has within-zone grime variation"
    # The big surfaces are exactly the ones an operator would zoom into.
    assert {"RF-S", "RF-N", "WALL-S"} <= set(varied)


def test_zone_mean_sits_inside_its_own_face_range(view):
    for zid, z in view["zones"].items():
        assert z["gMin"] <= z["g"] <= z["gMax"] + 1e-9, zid


def test_soiling_concentrates_low_on_a_wall(view):
    """Runoff pools at the base, so the bottom of a wall must read dirtier."""
    faces = [f for f in view["faces"] if f["zone"] == "WALL-S"]
    low = [f for f in faces if max(v[2] for v in f["v"]) <= 1.0]
    high = [f for f in faces if min(v[2] for v in f["v"]) >= 2.0]
    assert low and high
    assert sum(f["g"] for f in low) / len(low) > sum(f["g"] for f in high) / len(high)


def test_both_triangles_of_a_patch_agree(view):
    """A quad's two triangles share a footprint; disagreeing is mesh noise.

    Sampling per triangle centroid instead of the shared patch centre produces a
    checkerboard that reads as structure but is purely an artefact of how the
    surface was tessellated.
    """
    from propwash.backend.geometry.source import SyntheticHouseSource

    faces = SyntheticHouseSource().load().faces
    by_sample: dict = {}
    for f in faces:
        if f.sample_point is None:
            continue
        by_sample.setdefault((f.face_id.rsplit("-", 1)[0], f.sample_point), []).append(f)
    pairs = [v for v in by_sample.values() if len(v) == 2]
    assert pairs, "expected tessellated cells to share a sample point"
    for a, b in pairs:
        assert a.sample_at == b.sample_at


def test_the_solar_array_does_not_overlap_the_roof(view):
    """A reconstruction returns the panel surface, not the shingle beneath it.

    Overlapping them also makes the depth sort ambiguous, which shows up as
    roof triangles punching through the array.
    """
    panel = [f for f in view["faces"] if f["zone"] == "SOL-ROOF"]
    roof = [f for f in view["faces"] if f["zone"] == "RF-S"]
    assert panel and roof

    def bounds(fs):
        xs = [v[0] for f in fs for v in f["v"]]
        ys = [v[1] for f in fs for v in f["v"]]
        return min(xs), max(xs), min(ys), max(ys)

    px0, px1, py0, py1 = bounds(panel)
    for f in roof:
        cx = sum(v[0] for v in f["v"]) / 3
        cy = sum(v[1] for v in f["v"]) / 3
        assert not (px0 < cx < px1 and py0 < cy < py1), f["v"]
