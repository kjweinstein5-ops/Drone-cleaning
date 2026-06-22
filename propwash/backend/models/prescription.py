from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChemicalType(str, Enum):
    ECO_DEGREASER = "eco_degreaser"
    STANDARD_DEGREASER = "standard_degreaser"
    DEGREASER_SOLVENT_BLEND = "degreaser_solvent_blend"
    AMMONIA_FREE = "ammonia_free"
    DI_WATER_ONLY = "di_water_only"  # solar panels — no detergent


class CoveragePattern(str, Enum):
    SWEEP_NS = "sweep_ns"       # north-south sweep passes
    SWEEP_EW = "sweep_ew"       # east-west sweep passes
    SPIRAL_IN = "spiral_in"
    SPOT = "spot"               # targeted spot treatment


class Prescription(BaseModel):
    """Per-zone cleaning prescription — output of the Supervisor agent.

    Values come from the versioned surface treatment table (prescriptions/),
    never hard-coded here. The safety layer enforces hard ceilings (§9).
    """

    zone_id: str

    # Pressure
    pressure_bar: float = Field(..., gt=0.0, le=10.0)

    # Chemical
    chemical: ChemicalType
    chemical_mix_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Chemical solution fraction (0 = pure DI water, 1 = pure chemical)",
    )

    # Timing
    dwell_seconds: int = Field(..., gt=0)

    # Nozzle
    nozzle_id: int = Field(..., ge=1, description="Physical nozzle slot ID on the Sherpa")
    nozzle_angle_deg: Optional[float] = Field(None, ge=0.0, le=90.0)
    nozzle_orifice_mm: Optional[float] = Field(None, gt=0.0)

    # Geometry
    standoff_m: float = Field(..., gt=0.0, description="Distance from nozzle to surface (metres)")
    coverage_pattern: CoveragePattern = CoveragePattern.SWEEP_NS
    safety_margin_m: float = Field(0.15, gt=0.0, description="Keep-away margin from edges/obstacles")

    # Re-queue escalation — how much to bump pressure on a FAIL
    requeue_on_fail_pressure_delta: float = Field(
        0.5,
        ge=0.0,
        description="Pressure increment (bar) applied on re-queue after FAIL",
    )
