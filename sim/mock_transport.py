"""Mock ExecutionTransport for development without hardware.

Simulates the full Path A flow: dispatch → executing → verifying → done/reflagged.
Mirrors the state machine from the existing React simulation.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Callable, Dict, Optional

from propwash.backend.execution.transport import (
    DispatchResult,
    DispatchStatus,
    ExecutionTransport,
)
from propwash.backend.models.work_order import WorkOrder, WorkOrderStatus

logger = logging.getLogger(__name__)


class MockTransport(ExecutionTransport):
    """In-process mock transport that auto-progresses work order status."""

    def __init__(
        self,
        execution_duration_s: float = 2.0,
        fail_zone_ids: Optional[list[str]] = None,
        on_status_change: Optional[Callable[[str, WorkOrderStatus], None]] = None,
    ) -> None:
        self._store: Dict[str, WorkOrder] = {}
        self._execution_duration_s = execution_duration_s
        self._fail_zone_ids = set(fail_zone_ids or [])
        self._on_status_change = on_status_change

    @property
    def name(self) -> str:
        return "MockTransport (sim)"

    async def dispatch(self, work_order: WorkOrder) -> DispatchResult:
        ref = f"SIM-{uuid.uuid4().hex[:6].upper()}"
        self._store[work_order.job_id] = work_order.model_copy(
            update={"status": WorkOrderStatus.ASSIGNED, "updated_at": datetime.utcnow()}
        )
        self._notify(work_order.job_id, WorkOrderStatus.ASSIGNED)
        logger.info("[SIM] Dispatched %s → %s", work_order.job_id, ref)

        # Kick off simulated execution in the background
        asyncio.create_task(self._simulate(work_order.job_id))
        return DispatchResult(status=DispatchStatus.ACCEPTED, transport_ref=ref)

    async def get_status(self, job_id: str) -> WorkOrder:
        if job_id not in self._store:
            raise KeyError(f"[SIM] Unknown job_id: {job_id}")
        return self._store[job_id]

    async def mark_executing(self, job_id: str) -> WorkOrder:
        return await self._set_status(job_id, WorkOrderStatus.EXECUTING)

    async def mark_verifying(self, job_id: str, execution_log: dict | None = None) -> WorkOrder:
        wo = self._store[job_id]
        updated = wo.model_copy(
            update={
                "status": WorkOrderStatus.VERIFYING,
                "updated_at": datetime.utcnow(),
                "execution_log": execution_log,
            }
        )
        self._store[job_id] = updated
        self._notify(job_id, WorkOrderStatus.VERIFYING)
        return updated

    async def mark_done(self, job_id: str) -> WorkOrder:
        return await self._set_status(job_id, WorkOrderStatus.DONE)

    async def mark_reflagged(self, job_id: str) -> WorkOrder:
        return await self._set_status(job_id, WorkOrderStatus.REFLAGGED)

    async def _set_status(self, job_id: str, status: WorkOrderStatus) -> WorkOrder:
        wo = self._store[job_id]
        updated = wo.model_copy(update={"status": status, "updated_at": datetime.utcnow()})
        self._store[job_id] = updated
        self._notify(job_id, status)
        return updated

    async def _simulate(self, job_id: str) -> None:
        await asyncio.sleep(0.5)
        await self._set_status(job_id, WorkOrderStatus.EXECUTING)
        await asyncio.sleep(self._execution_duration_s)
        await self._set_status(job_id, WorkOrderStatus.VERIFYING)
        logger.info("[SIM] %s ready for verification", job_id)

    def _notify(self, job_id: str, status: WorkOrderStatus) -> None:
        if self._on_status_change:
            self._on_status_change(job_id, status)
        logger.debug("[SIM] %s → %s", job_id, status)
