from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from propwash.backend.models.prescription import Prescription
from propwash.backend.models.zone import ZoneSignature


class WorkOrderStatus(str, Enum):
    QUEUED = "queued"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    DONE = "done"
    REFLAGGED = "reflagged"   # failed verification, needs re-queue


class WorkOrder(BaseModel):
    """Path A work order — handed to the Lucid Sherpa operator (or Lucid Refresh).

    No direct hardware control. PROPWASH emits this; the operator executes it;
    PROPWASH reads back status and verifies. See CLAUDE.md §7 Path A.
    """

    job_id: str = Field(..., description="Unique job identifier, e.g. 'job_20260622_001'")
    zone: ZoneSignature
    prescription: Prescription
    verify_thermal_post: bool = Field(
        True, description="Whether to trigger a post-clean Autel re-scan for this zone"
    )
    status: WorkOrderStatus = WorkOrderStatus.QUEUED
    attempt: int = Field(1, ge=1, description="Attempt number (increments on re-queue)")
    operator_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Execution telemetry received back from the operator / Lucid Refresh
    execution_log: Optional[Dict[str, Any]] = Field(
        None, description="Actual execution telemetry for deviation tracking"
    )

    def next_attempt(self, pressure_delta: float) -> "WorkOrder":
        """Return a new WorkOrder with pressure bumped for a re-queue after FAIL."""
        new_prescription = self.prescription.model_copy(
            update={
                "pressure_bar": min(
                    self.prescription.pressure_bar + pressure_delta,
                    # TODO(PROPWASH): load hard ceiling from surface table, not magic number
                    10.0,
                )
            }
        )
        return self.model_copy(
            update={
                "prescription": new_prescription,
                "status": WorkOrderStatus.QUEUED,
                "attempt": self.attempt + 1,
                "updated_at": datetime.utcnow(),
                "execution_log": None,
            }
        )
