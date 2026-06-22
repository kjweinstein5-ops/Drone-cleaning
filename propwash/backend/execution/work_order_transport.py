"""Path A — Work-order integration (BUILD THIS FIRST; lowest risk).

PROPWASH emits a structured work order. The Sherpa operator (or Lucid
Refresh) executes it. PROPWASH reads back status and verifies.
No direct hardware control. See CLAUDE.md §7 Path A.

TODO(PROPWASH): Confirm with Lucid what Lucid Refresh's API exposes
(read job data? push work orders?). Until confirmed, this transport
stores work orders locally and returns status from an in-memory dict.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Dict

from propwash.backend.execution.transport import (
    DispatchResult,
    DispatchStatus,
    ExecutionTransport,
)
from propwash.backend.models.work_order import WorkOrder, WorkOrderStatus

logger = logging.getLogger(__name__)


class WorkOrderTransport(ExecutionTransport):
    """Path A — persists work orders locally; operator reads them via the dashboard."""

    def __init__(self) -> None:
        # In-memory store until DB integration is wired (see propwash/backend/db/)
        self._store: Dict[str, WorkOrder] = {}

    @property
    def name(self) -> str:
        return "WorkOrderTransport (Path A)"

    async def dispatch(self, work_order: WorkOrder) -> DispatchResult:
        transport_ref = f"WO-{uuid.uuid4().hex[:8].upper()}"
        updated = work_order.model_copy(
            update={
                "status": WorkOrderStatus.ASSIGNED,
                "updated_at": datetime.utcnow(),
            }
        )
        self._store[work_order.job_id] = updated
        logger.info(
            "WorkOrderTransport dispatched job_id=%s zone=%s ref=%s",
            work_order.job_id,
            work_order.zone.zone_id,
            transport_ref,
        )
        return DispatchResult(
            status=DispatchStatus.ACCEPTED,
            transport_ref=transport_ref,
            message="Work order queued for operator. Awaiting confirmation.",
        )

    async def get_status(self, job_id: str) -> WorkOrder:
        if job_id not in self._store:
            raise KeyError(f"Unknown job_id: {job_id}")
        return self._store[job_id]

    async def mark_executing(self, job_id: str) -> WorkOrder:
        wo = await self.get_status(job_id)
        updated = wo.model_copy(
            update={"status": WorkOrderStatus.EXECUTING, "updated_at": datetime.utcnow()}
        )
        self._store[job_id] = updated
        return updated

    async def mark_verifying(self, job_id: str, execution_log: dict | None = None) -> WorkOrder:
        wo = await self.get_status(job_id)
        updated = wo.model_copy(
            update={
                "status": WorkOrderStatus.VERIFYING,
                "updated_at": datetime.utcnow(),
                "execution_log": execution_log,
            }
        )
        self._store[job_id] = updated
        return updated

    async def mark_done(self, job_id: str) -> WorkOrder:
        wo = await self.get_status(job_id)
        updated = wo.model_copy(
            update={"status": WorkOrderStatus.DONE, "updated_at": datetime.utcnow()}
        )
        self._store[job_id] = updated
        return updated

    async def mark_reflagged(self, job_id: str) -> WorkOrder:
        wo = await self.get_status(job_id)
        updated = wo.model_copy(
            update={"status": WorkOrderStatus.REFLAGGED, "updated_at": datetime.utcnow()}
        )
        self._store[job_id] = updated
        return updated
