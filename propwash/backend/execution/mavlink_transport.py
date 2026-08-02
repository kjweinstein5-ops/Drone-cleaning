"""Path B/C (open stack) — MAVLink/MAVSDK payload transport.

The open-platform sibling of DjiPayloadTransport: speaks the vendor-neutral
MAVLink protocol (via MAVSDK) to a payload on an open airframe (PX4 / ArduPilot /
Freefly Astro). This is how PROPWASH runs its own control tech on an OPEN drone
instead of being locked out by a closed one (docs/decisions/OPEN_PLATFORM_INTEGRATION.md).

Gated behind PROPWASH_ENABLE_PATH_B (or _C for owned-airframe retrofit). Same hard
rules as every execution path (CLAUDE.md §7, §10):
  - the operator stays in command; MAVSDK commands the PAYLOAD (pressure/nozzle),
    NOT autonomous flight — that needs an FAA pathway/waiver;
  - the Tier-1 safety layer validates every setpoint BEFORE dispatch;
  - no covert automation, no Part 107 circumvention.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Dict, Optional

from propwash.backend.execution.transport import (
    DispatchResult,
    ExecutionTransport,
)
from propwash.backend.execution.mavlink_mission import (
    GeoPoint,
    MavlinkMission,
    translate_flight_plan,
)
from propwash.backend.models.prescription import Prescription
from propwash.backend.models.work_order import WorkOrder
from propwash.backend.models.zone import SurfaceType
from propwash.backend.safety.audit_log import AuditLog, EventType
from propwash.backend.safety.checks import SafetyChecker

if TYPE_CHECKING:  # avoid a runtime import cycle
    from propwash.backend.planning.coverage_path import FlightPlan

_FLAG = "PROPWASH_ENABLE_PATH_B"


class MavlinkPayloadTransport(ExecutionTransport):
    """Open-stack payload control via MAVSDK. Flagged off by default."""

    @property
    def name(self) -> str:
        return "MavlinkPayloadTransport (open stack — PX4/ArduPilot/Freefly)"

    @property
    def is_available(self) -> bool:
        return os.environ.get(_FLAG, "").lower() in ("1", "true", "yes")

    def build_mission(
        self,
        plan: "FlightPlan",
        prescriptions: Dict[str, Prescription],
        surface_types: Dict[str, SurfaceType],
        datum: GeoPoint,
        safety: Optional[SafetyChecker] = None,
        audit: Optional[AuditLog] = None,
        job_id: str = "",
    ) -> MavlinkMission:
        """Translate a FlightPlan into a MAVLink mission — safety-gated.

        Runs the deterministic Tier-1 safety check on EVERY prescription before any
        actuator setpoint is emitted (CLAUDE.md §2). This is pure translation and is
        allowed with the feature flag off, so missions can be reviewed on the ground
        before any hardware is connected.
        """
        safety = safety or SafetyChecker()

        for zone_id, presc in prescriptions.items():
            surface = surface_types.get(zone_id)
            if surface is None:
                raise ValueError(f"No surface type for zone '{zone_id}' — cannot safety-check")
            result = safety.check_prescription(presc, surface)
            if not result.passed:
                rules = "; ".join(v.rule for v in result.violations)
                if audit is not None:
                    audit.record(
                        EventType.SAFETY_VIOLATION, job_id=job_id, zone_id=zone_id,
                        detail=f"Mission build blocked by safety layer: {rules}",
                        data={
                            "surface_type": surface.value,
                            "requested_pressure_bar": presc.pressure_bar,
                            "stage": "mission_build",
                        },
                    )
                raise RuntimeError(
                    f"SAFETY BLOCK zone={zone_id}: {rules}. No mission emitted."
                )

        ceilings = {
            s.value: safety.hard_ceiling_bar(s)
            for s in {surface_types[z] for z in prescriptions if z in surface_types}
        }
        mission = translate_flight_plan(plan, prescriptions, ceilings, datum)
        if audit is not None:
            audit.record(
                EventType.MISSION_DISPATCHED, job_id=job_id,
                detail=(
                    f"Mission built and safety-validated — {len(mission.items)} items, "
                    f"{len(mission.geofence_exclusions)} keep-out volumes"
                ),
                data={
                    "items": len(mission.items),
                    "spray_items": mission.spray_items,
                    "geofence_exclusions": len(mission.geofence_exclusions),
                    "zones": sorted(prescriptions.keys()),
                },
            )
        return mission

    async def dispatch(self, work_order: WorkOrder) -> DispatchResult:
        if not self.is_available:
            raise RuntimeError(
                f"MAVLink transport is disabled. Set {_FLAG}=true only on an owned open "
                "airframe, with the safety layer gating setpoints and an FAA pathway for any "
                "flight automation. Operator stays in command. See CLAUDE.md §7."
            )
        # TODO(PROPWASH): MAVSDK connection seam. Translation is implemented in
        # build_mission(); this uploads it and streams ActuatorServos setpoints.
        #   from mavsdk import System
        #   drone = System(); await drone.connect(system_address=self.address)
        #   await drone.mission_raw.upload_mission(items)
        #   await drone.action.set_actuator(channel, value)
        # Flight remains operator-commanded; this drives the PAYLOAD only.
        raise NotImplementedError(
            "MAVSDK connection not implemented — build against MAVSDK-Python on owned "
            "hardware after FAA/liability review. Mission translation is available via "
            "build_mission(). See docs/FLIGHT_SOFTWARE_STACK.md."
        )

    async def get_status(self, job_id: str) -> WorkOrder:
        if not self.is_available:
            raise RuntimeError("MAVLink transport is disabled.")
        raise NotImplementedError("MAVLink telemetry read not implemented.")
