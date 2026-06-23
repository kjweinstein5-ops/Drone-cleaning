"""ARCHOICE typed data models (Pydantic).

These mirror the loop in the business plan: Diagnose -> Plan -> Choose.
Keep them honest: confidence/severity are model outputs, not guarantees, and
safety-critical diagnoses must route to a licensed pro (see Diagnosis.requires_pro).
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    none = "none"
    minor = "minor"
    moderate = "moderate"
    severe = "severe"


class Diagnosis(BaseModel):
    """Output of the Diagnose step."""
    object_name: str = Field(..., description="What the thing is, e.g. 'bathtub-wall caulk line'")
    problem: str = Field(..., description="What's wrong with it")
    severity: Severity
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence, 0..1")
    requires_pro: bool = Field(
        ..., description="True for electrical/gas/structural/roofing or low-confidence -> route to licensed pro"
    )
    reasoning: str = Field("", description="Short why, for explainability/trust")


class PlanStep(BaseModel):
    order: int
    instruction: str


class Material(BaseModel):
    name: str
    quantity: str = Field(..., description="Human-readable qty, e.g. '1 tube' or '~0.4 L'")


class Plan(BaseModel):
    """Output of the Plan step."""
    title: str
    steps: list[PlanStep]
    tools: list[str]
    materials: list[Material]
    est_minutes: int
    est_cost_usd: float
    difficulty: int = Field(..., ge=1, le=5, description="1 (easy) .. 5 (expert)")


class ProductSlot(BaseModel):
    """A labeled recommendation slot (see advertising-spec.md)."""
    slot: str = Field(..., description="best_fit | sponsored | budget")
    name: str
    price_usd: float
    why: str
    sponsored: bool = False


class Recommendation(BaseModel):
    need: str = Field(..., description="What this set is recommending for, e.g. 'sealant'")
    slots: list[ProductSlot]


class DiagnoseResponse(BaseModel):
    diagnosis: Diagnosis
    stub: bool = Field(False, description="True if returned by the offline stub (no Claude API key set)")


class PlanResponse(BaseModel):
    plan: Plan
    recommendations: list[Recommendation]
    stub: bool = False
