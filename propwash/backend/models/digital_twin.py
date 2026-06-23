"""Digital twin Pydantic models — thermographic 3D building model.

A DigitalTwin is built from a SfM mesh + registered Autel thermal frames.
It is the persistent per-property data asset, updated after every job.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class ZoneThermalReading(BaseModel):
    zone_id: str
    label: str
    surface_type: str
    pitch_deg: float = Field(..., ge=0.0, le=90.0)
    temp_celsius_mean: float
    temp_celsius_min: float
    temp_celsius_max: float
    # PROXY scores — thermal+RGB inference, not spectral (CLAUDE.md §5)
    grime_proxy_pre: float = Field(..., ge=0.0, le=1.0)
    grime_proxy_post: Optional[float] = Field(None, ge=0.0, le=1.0)
    moisture_index: float = Field(..., ge=0.0, le=1.0)
    human_clear: bool = False
    human_clear_at: Optional[datetime] = None
    pressure_prescribed_bar: Optional[float] = None
    pressure_actual_bar: Optional[float] = None
    verdict: Optional[str] = None   # PASS / FAIL / None
    solar: bool = False


class JobHistoryEntry(BaseModel):
    job_id: str
    cleaned_at: str           # ISO date string for JSON serialisation
    zones_passed: int
    zones_failed: int
    first_pass_rate: float = Field(..., ge=0.0, le=1.0)


class SoilingRateEstimate(BaseModel):
    zone_id: str
    weeks_to_threshold: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    based_on_visits: int


class AlertEntry(BaseModel):
    alert_type: str           # HUMAN_DETECTED / RE_QUEUE / SAFETY_VIOLATION
    zone_id: str
    occurred_at: str          # ISO datetime string
    resolved: bool = False
    detail: str = ""


class DigitalTwin(BaseModel):
    """Thermographic digital twin for a property.

    Built from SfM mesh + registered thermal frames. Updated after every job.
    mesh_ref and orthomosaic_ref are object-storage paths (S3-compatible).
    """

    property_id: str
    property_label: str
    address: str = ""
    captured_at: str
    mesh_ref: Optional[str] = None
    orthomosaic_ref: Optional[str] = None
    zones: List[ZoneThermalReading] = Field(default_factory=list)
    job_history: List[JobHistoryEntry] = Field(default_factory=list)
    soiling_rates: List[SoilingRateEstimate] = Field(default_factory=list)
    alerts: List[AlertEntry] = Field(default_factory=list)
    total_jobs: int = 0
    avg_first_pass_rate: Optional[float] = None
