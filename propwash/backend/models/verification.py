from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class VerificationResult(BaseModel):
    """Output of the Post-Clean agent after Autel thermal re-scan.

    residual_confidence is also a PROXY score (same thermal+RGB basis as
    grime_confidence in ZoneSignature — see CLAUDE.md §5).
    """

    zone_id: str
    job_id: str
    attempt: int = Field(1, ge=1)

    residual_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Post-clean grime/biofilm proxy score. Compare against threshold to "
            "determine PASS/FAIL. Same thermal+RGB basis as pre-clean score."
        ),
    )
    threshold: float = Field(
        0.15,
        ge=0.0,
        le=1.0,
        description="Maximum acceptable residual_confidence for a PASS verdict",
    )
    verdict: Verdict

    # On FAIL: what parameter adjustment was applied for the re-queue
    delta_applied: Optional[Dict[str, Any]] = Field(
        None,
        description="Parameter delta applied on re-queue, e.g. {'pressure_bar': 1.2}",
    )

    # Deviation between what was prescribed vs what was actually executed
    execution_vs_prescription: Optional[Dict[str, Any]] = Field(
        None,
        description="Deviation log for the learning model (prescribed vs actual)",
    )

    verified_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def evaluate(
        cls,
        zone_id: str,
        job_id: str,
        attempt: int,
        residual_confidence: float,
        threshold: float = 0.15,
        execution_vs_prescription: Optional[Dict[str, Any]] = None,
    ) -> "VerificationResult":
        verdict = Verdict.PASS if residual_confidence <= threshold else Verdict.FAIL
        return cls(
            zone_id=zone_id,
            job_id=job_id,
            attempt=attempt,
            residual_confidence=residual_confidence,
            threshold=threshold,
            verdict=verdict,
            execution_vs_prescription=execution_vs_prescription,
        )
