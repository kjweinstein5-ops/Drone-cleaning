"""ExecutionTransport — swappable adapter interface.

All three Lucid integration paths (A/B/C) implement this interface.
See CLAUDE.md §7. Only Path A (WorkOrderTransport) is active by default.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from propwash.backend.models.work_order import WorkOrder


class DispatchStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"
    UNKNOWN = "unknown"


@dataclass
class DispatchResult:
    status: DispatchStatus
    transport_ref: Optional[str] = None   # external ID / URL returned by the transport
    message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class ExecutionTransport(ABC):
    """Abstract base for all execution paths (A, B, C).

    Agents call dispatch(); they never interact with Lucid hardware directly.
    Safety checks must be performed BEFORE calling dispatch().
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable transport name, e.g. 'WorkOrderTransport (Path A)'."""

    @property
    def is_available(self) -> bool:
        """Return False if this transport is behind a disabled feature flag."""
        return True

    @abstractmethod
    async def dispatch(self, work_order: WorkOrder) -> DispatchResult:
        """Send the work order to the execution layer."""

    @abstractmethod
    async def get_status(self, job_id: str) -> WorkOrder:
        """Retrieve current status of a dispatched work order."""
