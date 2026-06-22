from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SurfaceType(str, Enum):
    COMPOSITE_SHINGLE = "composite_shingle"
    CLAY_TILE = "clay_tile"
    CONCRETE_TILE = "concrete_tile"
    SOLAR_PANEL = "solar_panel"
    WINDOW_GLASS = "window_glass"
    STUCCO = "stucco"
    GUTTER_ALUMINUM = "gutter_aluminum"
    UNKNOWN = "unknown"


class DataSource(str, Enum):
    THERMAL = "thermal"
    RGB = "rgb"
    SFM = "sfm"


class ZoneSignature(BaseModel):
    """Output of the Fusion agent — per-zone surface + condition signature.

    IMPORTANT (§5): grime_confidence is a PROXY score derived from thermal +
    RGB cues only (Autel EVO II 640T has no multispectral/NIR bands).
    Do not represent this as spectral biofilm detection.
    """

    zone_id: str = Field(..., description="Unique zone identifier, e.g. 'RF-S'")
    label: str = Field(..., description="Human-readable zone label, e.g. 'Roof — south slope'")
    surface_type: SurfaceType
    pitch_deg: float = Field(..., ge=0.0, le=90.0, description="Surface pitch in degrees")

    # Biofilm proxy — thermal + visible inference only, NOT spectral measurement
    grime_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Biofilm/grime proxy score (0–1). Inferred from thermal evaporative-cooling "
            "differentials and RGB visible staining. NOT a spectral measurement — Autel "
            "640T is thermal+RGB only. See CLAUDE.md §5."
        ),
    )
    moisture_index: float = Field(
        ..., ge=0.0, le=1.0, description="Moisture indicator from thermal delta (0–1)"
    )

    geometry_ref: Optional[str] = Field(
        None, description="Polygon or point-cloud region reference (e.g., WKT or S3 URI)"
    )
    source: List[DataSource] = Field(
        default_factory=list,
        description="Sensor sources that contributed to this zone signature",
    )
    property_id: Optional[str] = None
    job_id: Optional[str] = None

    @field_validator("source")
    @classmethod
    def source_must_not_claim_multispectral(cls, v: List[DataSource]) -> List[DataSource]:
        # Guard: no multispectral source can be declared (hardware doesn't support it)
        allowed = {DataSource.THERMAL, DataSource.RGB, DataSource.SFM}
        for s in v:
            if s not in allowed:
                raise ValueError(f"Unsupported data source '{s}' — Autel 640T is thermal+RGB only")
        return v
