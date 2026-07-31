"""FlightPlan → MAVLink mission items + ActuatorServos setpoints.

This is the translation layer that lets PROPWASH's planning output drive an OPEN
airframe (PX4 / ArduPilot / Freefly) — the concrete answer to Q2 and Q6 of the
Integration Qualification Questionnaire (docs/FLIGHT_SOFTWARE_STACK.md §2).

    ZonePath.waypoints        →  mission items (lat/lon/alt + cruise speed)
    Waypoint.spraying         →  ActuatorServos: pump ON/OFF at that item
    Prescription.pressure_bar →  ActuatorServos: PSM regulator setpoint
    Prescription.nozzle_id    →  ActuatorServos: IHM turret position

Pure Python — no MAVSDK dependency — so the translation is unit-testable with no
hardware. The MAVSDK connection itself is a thin documented seam in
`mavlink_transport.py`.

SAFETY (CLAUDE.md §2): every pressure setpoint is clamped to the per-surface hard
ceiling, and a request ABOVE the ceiling raises — it is never silently reduced and
never emitted. The PSM firmware ceiling remains the final independent guarantee
(docs/DYNAMIC_PRESSURE_HARDWARE.md §4).

NOTE: emitting a mission does NOT authorize autonomous flight. Missions are
operator-supervised; Offboard/autonomous flight requires the appropriate FAA
pathway (CLAUDE.md §7, §10, docs/FLIGHT_SOFTWARE_STACK.md §4).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from propwash.backend.models.prescription import Prescription
from propwash.backend.planning.coverage_path import FlightPlan, ZonePath

_EARTH_R = 6_378_137.0  # WGS84 equatorial radius (m)

# PX4 ActuatorServos channel assignments (configurable per airframe).
PUMP_CHANNEL = 1      # on/off
PRESSURE_CHANNEL = 2  # PSM electronic regulator setpoint
NOZZLE_CHANNEL = 3    # IHM turret position

# ActuatorServos values are normalized to [-1.0, 1.0] in PX4.
_ACT_MIN, _ACT_MAX = -1.0, 1.0
_MAX_NOZZLE_SLOTS = 4  # IHM turret slots


@dataclass
class GeoPoint:
    lat: float
    lon: float
    alt_m: float  # AMSL or relative, per mission frame


@dataclass
class ActuatorCommand:
    """One normalized actuator setpoint, with the human-readable reason."""

    channel: int
    value: float          # normalized [-1, 1] for PX4 ActuatorServos
    purpose: str          # "pump" | "pressure" | "nozzle"
    engineering_value: str = ""   # e.g. "4.0 bar", "slot 3", "on"


@dataclass
class MissionItem:
    """One waypoint in the emitted mission, plus any actuator changes at it."""

    seq: int
    zone_id: str
    point: GeoPoint
    cruise_speed_mps: float
    spraying: bool
    actuators: List[ActuatorCommand] = field(default_factory=list)


@dataclass
class MavlinkMission:
    property_id: str
    datum: GeoPoint                      # local-frame origin
    items: List[MissionItem] = field(default_factory=list)
    geofence_exclusions: List[dict] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def spray_items(self) -> int:
        return sum(1 for i in self.items if i.spraying)


class PressureCeilingExceeded(ValueError):
    """Raised when a requested pressure exceeds the surface's hard ceiling."""


# ── normalization helpers ─────────────────────────────────────────────────────

def normalize_pressure(pressure_bar: float, ceiling_bar: float) -> float:
    """Map pressure [0, ceiling] → ActuatorServos [-1, 1].

    Raises PressureCeilingExceeded if above the ceiling — the safety layer must
    catch this before dispatch; we never silently clamp an unsafe request.
    """
    if ceiling_bar <= 0:
        raise ValueError("ceiling_bar must be > 0")
    if pressure_bar > ceiling_bar + 1e-9:
        raise PressureCeilingExceeded(
            f"Requested {pressure_bar:.2f} bar exceeds hard ceiling {ceiling_bar:.2f} bar"
        )
    frac = max(0.0, pressure_bar / ceiling_bar)
    return _ACT_MIN + frac * (_ACT_MAX - _ACT_MIN)


def normalize_nozzle(nozzle_id: int, slots: int = _MAX_NOZZLE_SLOTS) -> float:
    """Map a discrete IHM turret slot (1..slots) → [-1, 1]."""
    if slots < 1:
        raise ValueError("slots must be >= 1")
    idx = max(1, min(slots, nozzle_id))
    if slots == 1:
        return _ACT_MIN
    frac = (idx - 1) / (slots - 1)
    return _ACT_MIN + frac * (_ACT_MAX - _ACT_MIN)


def pump_value(on: bool) -> float:
    return _ACT_MAX if on else _ACT_MIN


# ── coordinate conversion ─────────────────────────────────────────────────────

def local_to_geo(x_m: float, y_m: float, z_m: float, datum: GeoPoint) -> GeoPoint:
    """Local ENU metres → WGS84, equirectangular approximation.

    Accurate to well under a metre at building scale (< ~1 km from the datum),
    which is the regime we operate in.
    """
    dlat = (y_m / _EARTH_R) * (180.0 / math.pi)
    dlon = (x_m / (_EARTH_R * math.cos(math.radians(datum.lat)))) * (180.0 / math.pi)
    return GeoPoint(
        lat=datum.lat + dlat,
        lon=datum.lon + dlon,
        alt_m=datum.alt_m + z_m,
    )


# ── the translator ────────────────────────────────────────────────────────────

def translate_flight_plan(
    plan: FlightPlan,
    prescriptions: Dict[str, Prescription],
    ceilings_bar: Dict[str, float],
    datum: GeoPoint,
) -> MavlinkMission:
    """Translate a FlightPlan into a MAVLink mission with actuator setpoints.

    `prescriptions` and `ceilings_bar` are keyed by zone_id / surface_type
    respectively. Raises PressureCeilingExceeded if any zone's prescription is
    above its surface's hard ceiling.
    """
    mission = MavlinkMission(property_id=plan.property_id, datum=datum)
    mission.notes.append(
        "Operator-supervised mission. Emitting this does NOT authorize autonomous "
        "flight (CLAUDE.md §7/§10)."
    )
    seq = 0

    for zp in plan.zone_paths:
        presc = prescriptions.get(zp.zone_id)
        if presc is None:
            continue
        ceiling = ceilings_bar.get(zp.surface_type)
        if ceiling is None:
            raise ValueError(f"No hard ceiling known for surface '{zp.surface_type}'")

        # Safety: normalize (and validate) once per zone.
        p_val = normalize_pressure(presc.pressure_bar, ceiling)
        n_val = normalize_nozzle(presc.nozzle_id)

        prev_spraying: Optional[bool] = None
        for wi, wp in enumerate(zp.waypoints):
            acts: List[ActuatorCommand] = []

            # At the first waypoint of a zone: set nozzle + pressure before spraying.
            if wi == 0:
                acts.append(ActuatorCommand(
                    NOZZLE_CHANNEL, n_val, "nozzle", f"slot {presc.nozzle_id}"))
                acts.append(ActuatorCommand(
                    PRESSURE_CHANNEL, p_val, "pressure", f"{presc.pressure_bar:.2f} bar"))

            # Pump toggles only when the spray state changes (fewer commands).
            if prev_spraying is None or wp.spraying != prev_spraying:
                acts.append(ActuatorCommand(
                    PUMP_CHANNEL, pump_value(wp.spraying), "pump",
                    "on" if wp.spraying else "off"))
            prev_spraying = wp.spraying

            mission.items.append(MissionItem(
                seq=seq,
                zone_id=zp.zone_id,
                point=local_to_geo(wp.x, wp.y, wp.z, datum),
                cruise_speed_mps=zp.traverse_speed_mps,
                spraying=wp.spraying,
                actuators=acts,
            ))
            seq += 1

        # Pump off at the end of every zone (fail-safe hygiene).
        if zp.waypoints:
            last = zp.waypoints[-1]
            mission.items.append(MissionItem(
                seq=seq,
                zone_id=zp.zone_id,
                point=local_to_geo(last.x, last.y, last.z, datum),
                cruise_speed_mps=zp.traverse_speed_mps,
                spraying=False,
                actuators=[ActuatorCommand(PUMP_CHANNEL, pump_value(False), "pump", "off")],
            ))
            seq += 1

    # Exclusion zones → geofence exclusion volumes.
    for ko in plan.keep_outs:
        c = local_to_geo(ko.center[0], ko.center[1], ko.center[2], datum)
        mission.geofence_exclusions.append({
            "zone_id": ko.zone_id,
            "lat": c.lat, "lon": c.lon, "alt_m": c.alt_m,
            "radius_m": ko.radius_m,
            "reason": ko.reason,
        })

    return mission
