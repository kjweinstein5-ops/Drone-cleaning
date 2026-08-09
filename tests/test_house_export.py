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
