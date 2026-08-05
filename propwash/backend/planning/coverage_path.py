"""Stage 5 — coverage / flight-path generation (docs/3D_DATA_PIPELINE.md §5).

Turns each classified zone + its prescription into the flight path the nozzle
should follow: a standoff "shell" parallel to the surface, swept back-and-forth
(boustrophedon), spaced by the spray width, with keep-out volumes around every
exclusion zone.

⚠️ OUTPUT IS OPERATOR GUIDANCE, NOT AN AUTONOMOUS COMMAND STREAM (CLAUDE.md §7,
§10). The operator flies this overlay and stays in command (Part 107). The same
computed path can feed more automation later — behind a feature flag, on an
open platform, and only with the appropriate FAA pathway. See docs §9.

Pure-Python (no numpy/Open3D) so it runs in the simulator with no dependencies.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from propwash.backend.geometry.source import Face, ReconstructionOutput
from propwash.backend.models.prescription import Prescription
from propwash.backend.models.work_order import WorkOrder
from propwash.backend.fusion.scan_pipeline import _zone_key
from propwash.backend.planning.zone_ordering import order_key

Vec3 = Tuple[float, float, float]

_OVERLAP = 0.85          # sweep spacing = spray_width * this (15% overlap)
_KEEPOUT_MARGIN_M = 0.5  # safety margin added to exclusion keep-out radius
# Nominal nozzle traverse speed (m/s) — ASSUMPTION TO VALIDATE. Delicate surfaces
# go slower. Prescription `dwell_seconds` governs chemical contact in the execute
# step (soft-wash: apply → dwell → rinse), NOT the traverse rate here.
_TRAVERSE_MPS = {"solar_panel": 0.20, "window_glass": 0.20}
_TRAVERSE_MPS_DEFAULT = 0.35


# ── tiny vector ops ───────────────────────────────────────────────────────────
def _sub(a: Vec3, b: Vec3) -> Vec3: return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def _add(a: Vec3, b: Vec3) -> Vec3: return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def _scale(a: Vec3, s: float) -> Vec3: return (a[0]*s, a[1]*s, a[2]*s)
def _dot(a: Vec3, b: Vec3) -> float: return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def _norm(a: Vec3) -> float: return math.sqrt(_dot(a, a))
def _unit(a: Vec3) -> Vec3:
    n = _norm(a)
    return (0.0, 0.0, 1.0) if n == 0 else (a[0]/n, a[1]/n, a[2]/n)


@dataclass
class Waypoint:
    x: float
    y: float
    z: float
    spraying: bool = True   # False on repositioning legs between sweep lines


@dataclass
class KeepOut:
    """No-spray / no-fly volume around an exclusion zone (chimney, HVAC, person)."""
    zone_id: str
    center: Vec3
    radius_m: float
    reason: str = ""


@dataclass
class ZonePath:
    zone_id: str
    surface_type: str
    solar: bool
    standoff_m: float
    spray_width_m: float
    traverse_speed_mps: float
    approach_normal: Vec3            # outward surface normal (approach direction)
    waypoints: List[Waypoint] = field(default_factory=list)
    keepout_violations: int = 0
    # Treatment phase this pass belongs to (None = single-pass legacy plan).
    phase: Optional[str] = None
    phase_pressure_bar: Optional[float] = None
    phase_chemical: Optional[str] = None

    @property
    def label(self) -> str:
        return f"{self.zone_id}:{self.phase}" if self.phase else self.zone_id

    @property
    def path_length_m(self) -> float:
        total = 0.0
        for a, b in zip(self.waypoints, self.waypoints[1:]):
            total += _norm(_sub((b.x, b.y, b.z), (a.x, a.y, a.z)))
        return total

    @property
    def est_seconds(self) -> float:
        if self.traverse_speed_mps <= 0:
            return 0.0
        return self.path_length_m / self.traverse_speed_mps


@dataclass
class FlightPlan:
    property_id: str
    zone_paths: List[ZonePath] = field(default_factory=list)
    keep_outs: List[KeepOut] = field(default_factory=list)

    @property
    def total_waypoints(self) -> int:
        return sum(len(zp.waypoints) for zp in self.zone_paths)

    @property
    def total_keepout_violations(self) -> int:
        return sum(zp.keepout_violations for zp in self.zone_paths)

    @property
    def est_minutes(self) -> float:
        return sum(zp.est_seconds for zp in self.zone_paths) / 60.0


def _zone_plane(faces: List[Face], building_center: Vec3) -> Tuple[Vec3, Vec3]:
    """Return (centroid, outward normal) for a group of faces."""
    n = len(faces)
    centroid = _scale(
        (sum(f.centroid[0] for f in faces),
         sum(f.centroid[1] for f in faces),
         sum(f.centroid[2] for f in faces)), 1.0 / n)
    normal = _unit((sum(f.normal[0] for f in faces),
                    sum(f.normal[1] for f in faces),
                    sum(f.normal[2] for f in faces)))
    # Orient outward (away from the building center).
    if _dot(normal, _sub(centroid, building_center)) < 0:
        normal = _scale(normal, -1.0)
    return centroid, normal


def _local_frame(normal: Vec3) -> Tuple[Vec3, Vec3]:
    """Two axes spanning the plane perpendicular to `normal`."""
    up = (0.0, 0.0, 1.0)
    if abs(_dot(normal, up)) > 0.95:      # near-horizontal surface → use world X
        up = (1.0, 0.0, 0.0)
    u = _unit(_cross(normal, up))
    v = _unit(_cross(normal, u))
    return u, v


def _spray_width(prescription: Prescription) -> float:
    """Effective swath width from nozzle fan angle + standoff distance."""
    angle = prescription.nozzle_angle_deg or 40.0
    return max(0.15, 2.0 * prescription.standoff_m * math.tan(math.radians(angle / 2.0)))


def plan_zone_path(
    zone_id: str,
    surface_type: str,
    solar: bool,
    faces: List[Face],
    prescription: Prescription,
    building_center: Vec3,
    keep_outs: Optional[List[KeepOut]] = None,
) -> ZonePath:
    """Boustrophedon coverage path over one zone's standoff shell."""
    centroid, normal = _zone_plane(faces, building_center)
    u_axis, v_axis = _local_frame(normal)

    # Project all vertices into the (u, v) plane to get the zone extent.
    us: List[float] = []
    vs: List[float] = []
    for f in faces:
        for vtx in (f.v0, f.v1, f.v2):
            d = _sub(vtx, centroid)
            us.append(_dot(d, u_axis))
            vs.append(_dot(d, v_axis))
    umin, umax, vmin, vmax = min(us), max(us), min(vs), max(vs)

    spray_w = _spray_width(prescription)
    spacing = max(0.1, spray_w * _OVERLAP)
    traverse_speed = _TRAVERSE_MPS.get(surface_type, _TRAVERSE_MPS_DEFAULT)

    def to3d(uu: float, vv: float) -> Vec3:
        base = _add(centroid, _add(_scale(u_axis, uu), _scale(v_axis, vv)))
        return _add(base, _scale(normal, prescription.standoff_m))  # offset along normal

    # Sweep lines along u, stepping across v; alternate direction (boustrophedon).
    waypoints: List[Waypoint] = []
    lines = max(1, int(math.ceil((vmax - vmin) / spacing)))
    for i in range(lines + 1):
        vv = min(vmin + i * spacing, vmax)
        u_from, u_to = (umin, umax) if i % 2 == 0 else (umax, umin)
        p0, p1 = to3d(u_from, vv), to3d(u_to, vv)
        if waypoints:  # repositioning leg to the start of this sweep (not spraying)
            waypoints.append(Waypoint(p0[0], p0[1], p0[2], spraying=False))
        else:
            waypoints.append(Waypoint(p0[0], p0[1], p0[2], spraying=True))
        waypoints.append(Waypoint(p1[0], p1[1], p1[2], spraying=True))

    zp = ZonePath(
        zone_id=zone_id, surface_type=surface_type, solar=solar,
        standoff_m=prescription.standoff_m, spray_width_m=round(spray_w, 3),
        traverse_speed_mps=round(traverse_speed, 4), approach_normal=normal,
        waypoints=waypoints,
    )
    if keep_outs:
        zp.keepout_violations = sum(
            1 for w in waypoints if _violates_keepout((w.x, w.y, w.z), keep_outs)
        )
    return zp


def _violates_keepout(point: Vec3, keep_outs: List[KeepOut]) -> bool:
    return any(_norm(_sub(point, ko.center)) < ko.radius_m for ko in keep_outs)


def _keepout_from_faces(zone_id: str, faces: List[Face], reason: str) -> KeepOut:
    n = len(faces)
    center = _scale((sum(f.centroid[0] for f in faces),
                     sum(f.centroid[1] for f in faces),
                     sum(f.centroid[2] for f in faces)), 1.0 / n)
    radius = 0.0
    for f in faces:
        for vtx in (f.v0, f.v1, f.v2):
            radius = max(radius, _norm(_sub(vtx, center)))
    return KeepOut(zone_id=zone_id, center=center, radius_m=round(radius + _KEEPOUT_MARGIN_M, 3), reason=reason)


def build_flight_plan(
    recon: ReconstructionOutput,
    work_orders: List[WorkOrder],
    exclusions: Optional[List[Tuple[str, str]]] = None,
) -> FlightPlan:
    """Build the full ordered flight plan from scan geometry + safety-gated work orders.

    `work_orders` come from plan_from_scan (cleanable, safety-passed). `exclusions`
    are (zone_id, reason) pairs whose faces become keep-out volumes.
    """
    faces_by_zone: Dict[str, List[Face]] = {}
    for f in recon.faces:
        faces_by_zone.setdefault(_zone_key(f.face_id), []).append(f)

    building_center = _scale(
        (sum(f.centroid[0] for f in recon.faces),
         sum(f.centroid[1] for f in recon.faces),
         sum(f.centroid[2] for f in recon.faces)), 1.0 / len(recon.faces))

    # Keep-out volumes from exclusion zones (feeds the safety check).
    keep_outs: List[KeepOut] = []
    for zid, reason in (exclusions or []):
        if zid in faces_by_zone:
            keep_outs.append(_keepout_from_faces(zid, faces_by_zone[zid], reason))

    # Order the work orders (solar-first, top-down, gutters last).
    def wo_sort(wo: WorkOrder):
        faces = faces_by_zone.get(wo.zone.zone_id, [])
        mean_h = sum(f.height_m for f in faces) / len(faces) if faces else 0.0
        return order_key(wo.zone.surface_type, mean_h)

    ordered = sorted(work_orders, key=wo_sort)

    zone_paths: List[ZonePath] = []
    for wo in ordered:
        faces = faces_by_zone.get(wo.zone.zone_id)
        if not faces:
            continue
        zone_paths.append(plan_zone_path(
            zone_id=wo.zone.zone_id,
            surface_type=wo.zone.surface_type.value,
            solar=(wo.zone.surface_type.value == "solar_panel"),
            faces=faces,
            prescription=wo.prescription,
            building_center=building_center,
            keep_outs=keep_outs,
        ))

    return FlightPlan(property_id=recon.property_id, zone_paths=zone_paths, keep_outs=keep_outs)


def build_phased_flight_plan(
    recon: ReconstructionOutput,
    work_orders: List[WorkOrder],
    exclusions: Optional[List[Tuple[str, str]]] = None,
) -> FlightPlan:
    """Flight plan with one coverage pass PER TREATMENT PHASE.

    Real cleaning is pre-soak → chemical → dwell → rinse
    (docs/planning/treatment_phases.py). Each *active* phase gets its own pass
    over the same geometry at that phase's pressure and chemistry:

        PRE_SOAK  water only, gentlest  — wets the surface, protects substrate
        CHEMICAL  prescribed detergent  — applies the mix
        DWELL     (no pass — no aircraft needed)
        RINSE     water only            — washes down

    Passes are emitted in phase order within each zone, and zones remain ordered
    solar-first / top-down. Safety: pre-soak and rinse are water-only by
    construction, and every phase pressure is <= the prescribed cleaning
    pressure, so a phased plan can never exceed what the safety layer approved.
    """
    from propwash.backend.planning.treatment_phases import (
        ACTIVE_PHASES,
        build_phase_plan,
    )

    base = build_flight_plan(recon, work_orders, exclusions)
    presc_by_zone = {wo.zone.zone_id: wo.prescription for wo in work_orders}

    phased: List[ZonePath] = []
    for zp in base.zone_paths:
        presc = presc_by_zone.get(zp.zone_id)
        if presc is None:
            phased.append(zp)
            continue

        steps = {
            s.phase: s
            for s in build_phase_plan(zp.zone_id, presc, zp.est_seconds)
            if s.phase in ACTIVE_PHASES
        }
        for phase in ACTIVE_PHASES:
            step = steps.get(phase)
            if step is None:
                continue
            phased.append(ZonePath(
                zone_id=zp.zone_id,
                surface_type=zp.surface_type,
                solar=zp.solar,
                standoff_m=zp.standoff_m,
                spray_width_m=zp.spray_width_m,
                traverse_speed_mps=zp.traverse_speed_mps,
                approach_normal=zp.approach_normal,
                waypoints=list(zp.waypoints),
                keepout_violations=zp.keepout_violations,
                phase=phase.value,
                phase_pressure_bar=step.pressure_bar,
                phase_chemical=step.chemical.value,
            ))

    return FlightPlan(
        property_id=recon.property_id, zone_paths=phased, keep_outs=base.keep_outs
    )
