"""Path C — Companion-computer retrofit (LAST RESORT; constrained).

NEVER build this without:
  - Lucid's explicit cooperation on hardware you own
  - FAA pathway / waiver for increased flight automation
  - Warranty + liability legal review

Gated behind PROPWASH_ENABLE_PATH_C=true feature flag.

See CLAUDE.md §7 Path C. The operator must remain genuinely in command.
Any covert automation or Part 107 circumvention is explicitly out of scope.
"""

from __future__ import annotations

import os

from propwash.backend.execution.transport import (
    DispatchResult,
    ExecutionTransport,
)
from propwash.backend.models.work_order import WorkOrder

_FLAG = "PROPWASH_ENABLE_PATH_C"


class CompanionTransport(ExecutionTransport):
    """Path C — companion computer driving pump/valve/servo on owned hardware."""

    @property
    def name(self) -> str:
        return "CompanionTransport (Path C — LAST RESORT)"

    @property
    def is_available(self) -> bool:
        return os.environ.get(_FLAG, "").lower() in ("1", "true", "yes")

    async def dispatch(self, work_order: WorkOrder) -> DispatchResult:
        if not self.is_available:
            raise RuntimeError(
                f"Path C is disabled. Set {_FLAG}=true only after obtaining Lucid "
                "cooperation, legal clearance, and FAA pathway/waiver. See CLAUDE.md §7."
            )
        # TODO(PROPWASH): Implement only with Lucid cooperation + FAA waiver.
        raise NotImplementedError(
            "Path C not implemented — requires Lucid cooperation, FAA pathway, and legal review."
        )

    async def get_status(self, job_id: str) -> WorkOrder:
        if not self.is_available:
            raise RuntimeError(f"Path C is disabled.")
        raise NotImplementedError("Path C not implemented.")
