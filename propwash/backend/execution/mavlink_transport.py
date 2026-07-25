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

from propwash.backend.execution.transport import (
    DispatchResult,
    ExecutionTransport,
)
from propwash.backend.models.work_order import WorkOrder

_FLAG = "PROPWASH_ENABLE_PATH_B"


class MavlinkPayloadTransport(ExecutionTransport):
    """Open-stack payload control via MAVSDK. Flagged off by default."""

    @property
    def name(self) -> str:
        return "MavlinkPayloadTransport (open stack — PX4/ArduPilot/Freefly)"

    @property
    def is_available(self) -> bool:
        return os.environ.get(_FLAG, "").lower() in ("1", "true", "yes")

    async def dispatch(self, work_order: WorkOrder) -> DispatchResult:
        if not self.is_available:
            raise RuntimeError(
                f"MAVLink transport is disabled. Set {_FLAG}=true only on an owned open "
                "airframe, with the safety layer gating setpoints and an FAA pathway for any "
                "flight automation. Operator stays in command. See CLAUDE.md §7."
            )
        # TODO(PROPWASH): implement MAVSDK payload control (pump/nozzle setpoints).
        # Flight remains operator-commanded; this drives the payload only.
        raise NotImplementedError(
            "MAVLink payload control not implemented — build against MAVSDK on owned "
            "hardware after FAA/liability review. See OPEN_PLATFORM_INTEGRATION.md."
        )

    async def get_status(self, job_id: str) -> WorkOrder:
        if not self.is_available:
            raise RuntimeError("MAVLink transport is disabled.")
        raise NotImplementedError("MAVLink payload control not implemented.")
