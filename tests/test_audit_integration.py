"""Audit log wired into the live pipeline — the evidence trail is real.

These tests prove the compliance record is produced by the actual pipeline, not
assembled by hand: safety rejections, exclusions, and mission builds all land in
a verifiable hash chain (docs/WAIVER_107_35.md §3.5).
"""

from __future__ import annotations

import pytest

from propwash.backend.execution.mavlink_mission import GeoPoint
from propwash.backend.execution.mavlink_transport import MavlinkPayloadTransport
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.planning.coverage_path import build_flight_plan
from propwash.backend.planning.scan_to_plan import plan_from_scan
from propwash.backend.safety.audit_log import AuditLog, EventType
from sim.scan_demo import synth_thermal_samples

DATUM = GeoPoint(lat=33.1281, lon=-117.3506, alt_m=30.0)


def _scan():
    source = SyntheticBuildingSource()
    recon = source.load()
    return source, recon, run_scan_pipeline(source, synth_thermal_samples(recon.faces))


def test_plan_records_exclusions_to_the_chain():
    _, _, zones = _scan()
    audit = AuditLog()
    plan_from_scan(zones, job_id="job_1", property_id="prop_1", audit=audit)

    excluded = [e for e in audit.entries if e.event_type is EventType.KEEPOUT_BREACH]
    zone_ids = {e.zone_id for e in excluded}
    assert {"HVAC", "CHIMNEY"} <= zone_ids
    assert audit.verify_integrity().valid is True


def test_plan_records_a_summary_event():
    _, _, zones = _scan()
    audit = AuditLog()
    result = plan_from_scan(zones, job_id="job_1", property_id="prop_1", audit=audit)

    summary = [e for e in audit.entries if e.event_type is EventType.MISSION_DISPATCHED]
    assert len(summary) == 1
    assert summary[0].data["queued"] == len(result.work_orders)


def test_safety_rejection_is_recorded_with_evidence():
    """An unsafe prescription must leave a permanent, detailed record."""
    from propwash.backend.planning.prescriber import TablePrescriber
    from propwash.backend.models.zone import SurfaceType

    class OverPressurePrescriber(TablePrescriber):
        def prescribe(self, signature):
            p = super().prescribe(signature)
            if signature.surface_type == SurfaceType.SOLAR_PANEL:
                return p.model_copy(update={"pressure_bar": 6.0})  # >> 2.0 ceiling
            return p

    _, _, zones = _scan()
    audit = AuditLog()
    result = plan_from_scan(
        zones, job_id="job_bad", property_id="prop_1",
        prescriber=OverPressurePrescriber(), audit=audit,
    )

    assert any(zid == "SOL-ROOF" for zid, _ in result.safety_rejected)
    violations = [e for e in audit.entries if e.event_type is EventType.SAFETY_VIOLATION]
    assert violations, "safety rejection must be recorded"
    rec = violations[0]
    assert rec.zone_id == "SOL-ROOF"
    assert rec.data["requested_pressure_bar"] == 6.0
    assert rec.is_safety_critical is True
    assert audit.verify_integrity().valid is True


def test_mission_build_records_and_blocks_are_evidenced():
    source, recon, zones = _scan()
    audit = AuditLog()
    plan = plan_from_scan(zones, job_id="job_1", property_id="prop_1", audit=audit)
    flight = build_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    presc = {wo.zone.zone_id: wo.prescription for wo in plan.work_orders}
    surfaces = {wo.zone.zone_id: wo.zone.surface_type for wo in plan.work_orders}

    t = MavlinkPayloadTransport()
    mission = t.build_mission(flight, presc, surfaces, DATUM, audit=audit, job_id="job_1")
    built = [
        e for e in audit.entries
        if e.event_type is EventType.MISSION_DISPATCHED and "Mission built" in e.detail
    ]
    assert built and built[0].data["items"] == len(mission.items)

    # Now block it and confirm the block is recorded too.
    presc["SOL-ROOF"] = presc["SOL-ROOF"].model_copy(update={"pressure_bar": 6.0})
    with pytest.raises(RuntimeError, match="SAFETY BLOCK"):
        t.build_mission(flight, presc, surfaces, DATUM, audit=audit, job_id="job_1")

    blocks = [e for e in audit.entries if e.data.get("stage") == "mission_build"]
    assert blocks, "a blocked mission build must be recorded"
    assert audit.verify_integrity().valid is True


def test_full_run_produces_a_verifiable_compliance_export():
    """End-to-end: the export is what goes in the waiver package."""
    source, recon, zones = _scan()
    audit = AuditLog()
    plan = plan_from_scan(zones, job_id="job_1", property_id="prop_1", audit=audit)
    flight = build_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    presc = {wo.zone.zone_id: wo.prescription for wo in plan.work_orders}
    surfaces = {wo.zone.zone_id: wo.zone.surface_type for wo in plan.work_orders}
    MavlinkPayloadTransport().build_mission(
        flight, presc, surfaces, DATUM, audit=audit, job_id="job_1"
    )

    export = audit.compliance_export(job_id="job_1")
    assert export["integrity_valid"] is True
    assert export["entry_count"] > 0
    assert export["safety_event_count"] >= 2      # the two exclusion zones
    assert export["chain_head"]


def test_audit_is_optional_pipeline_works_without_it():
    _, _, zones = _scan()
    result = plan_from_scan(zones, job_id="job_1", property_id="prop_1")  # no audit
    assert result.work_orders
