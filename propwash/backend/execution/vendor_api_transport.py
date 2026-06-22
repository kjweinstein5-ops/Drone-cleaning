"""Path B — Vendor control API (BEST CASE; UNVERIFIED it exists).

DO NOT ACTIVATE until Lucid confirms a pump/pressure or MAVLink endpoint.
Gated behind PROPWASH_ENABLE_PATH_B=true feature flag.

See CLAUDE.md §7 Path B. If flag is not set, dispatch() raises RuntimeError.
"""

from __future__ import annotations

import os

from propwash.backend.execution.transport import (
    DispatchResult,
    DispatchStatus,
    ExecutionTransport,
)
from propwash.backend.models.work_order import WorkOrder

_FLAG = "PROPWASH_ENABLE_PATH_B"


class VendorApiTransport(ExecutionTransport):
    """Path B — direct pump/pressure setpoints via a Lucid API (unverified)."""

    @property
    def name(self) -> str:
        return "VendorApiTransport (Path B — UNVERIFIED)"

    @property
    def is_available(self) -> bool:
        return os.environ.get(_FLAG, "").lower() in ("1", "true", "yes")

    async def dispatch(self, work_order: WorkOrder) -> DispatchResult:
        if not self.is_available:
            raise RuntimeError(
                f"Path B is disabled. Set {_FLAG}=true only after Lucid confirms "
                "a public pump/pressure or MAVLink API exists. See CLAUDE.md §7."
            )
        # TODO(PROPWASH): Implement once Lucid API endpoint is confirmed.
        raise NotImplementedError("Path B not yet implemented — awaiting Lucid API confirmation.")

    async def get_status(self, job_id: str) -> WorkOrder:
        if not self.is_available:
            raise RuntimeError(f"Path B is disabled. Set {_FLAG}=true to enable.")
        raise NotImplementedError("Path B not yet implemented.")
