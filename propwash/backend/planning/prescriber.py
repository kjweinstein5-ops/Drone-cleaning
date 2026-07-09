"""Deterministic prescriber — surface type → cleaning prescription.

Reads the versioned surface treatment table (prescriptions/) and emits a baseline
Prescription per zone. Deterministic and runnable with no LLM/API, so the full
scan → plan chain works in the simulator. The Supervisor agent (Tier 3) refines
these advisorily; the table + safety layer remain authoritative (CLAUDE.md §9).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from propwash.backend.models.prescription import (
    ChemicalType,
    CoveragePattern,
    Prescription,
)
from propwash.backend.models.zone import (
    DataSource,
    SurfaceType,
    ZoneSignature,
)
from propwash.backend.fusion.scan_pipeline import ScannedZone

_SURFACE_TABLE_PATH = (
    Path(__file__).parent.parent.parent.parent / "prescriptions" / "surface_treatment_v1.json"
)

# Physical nozzle slot per surface (maps to the operator's nozzle kit / future IHM).
_SURFACE_NOZZLE = {
    SurfaceType.SOLAR_PANEL: 4,
    SurfaceType.WINDOW_GLASS: 5,
    SurfaceType.STUCCO: 3,
    SurfaceType.COMPOSITE_SHINGLE: 2,
    SurfaceType.CLAY_TILE: 2,
    SurfaceType.CONCRETE_TILE: 2,
    SurfaceType.GUTTER_ALUMINUM: 6,
}

_SURFACE_LABELS = {
    "SOL-ROOF": "Rooftop solar array",
    "RF-S": "Roof — south slope",
    "RF-N": "Roof — north slope",
    "WALL-S": "Façade — south",
    "WALL-N": "Façade — north",
    "WALL-E": "Façade — east",
    "WALL-W": "Façade — west",
    "WIN-S1": "Window — south 1",
    "WIN-S2": "Window — south 2",
}


def scanned_zone_to_signature(
    z: ScannedZone, property_id: str, job_id: str
) -> ZoneSignature:
    """Convert a cleanable ScannedZone into the ZoneSignature the plan consumes.

    Caller must not pass exclusion zones — those never become signatures.
    """
    if z.is_exclusion:
        raise ValueError(f"Exclusion zone {z.zone_id} cannot become a ZoneSignature")

    return ZoneSignature(
        zone_id=z.zone_id,
        label=_SURFACE_LABELS.get(z.zone_id, z.zone_id),
        surface_type=SurfaceType(z.surface_type),
        pitch_deg=z.pitch_deg,
        grime_confidence=z.grime_proxy,   # PROXY — thermal+RGB, not spectral (§5)
        moisture_index=z.moisture_index,
        source=[DataSource.THERMAL, DataSource.RGB, DataSource.SFM],
        property_id=property_id,
        job_id=job_id,
    )


class TablePrescriber:
    """Baseline prescriber sourced from the versioned surface table."""

    def __init__(self, table: Optional[Dict[str, Any]] = None) -> None:
        self._table = table or self._load_table()

    @staticmethod
    def _load_table() -> Dict[str, Any]:
        with open(_SURFACE_TABLE_PATH) as f:
            return json.load(f)

    def prescribe(self, signature: ZoneSignature) -> Prescription:
        key = signature.surface_type.value
        cfg = self._table["surfaces"].get(key)
        if cfg is None:
            raise ValueError(f"No surface-table entry for '{key}' — cannot prescribe")

        return Prescription(
            zone_id=signature.zone_id,
            pressure_bar=cfg["pressure_bar_default"],
            chemical=ChemicalType(cfg["chemical"]),
            chemical_mix_ratio=cfg["chemical_mix_ratio_default"],
            dwell_seconds=cfg["dwell_seconds_default"],
            nozzle_id=_SURFACE_NOZZLE.get(signature.surface_type, 1),
            nozzle_angle_deg=cfg.get("nozzle_angle_deg"),
            nozzle_orifice_mm=cfg.get("nozzle_orifice_mm"),
            standoff_m=cfg["standoff_m_default"],
            coverage_pattern=CoveragePattern.SWEEP_NS,
            safety_margin_m=0.15,
            requeue_on_fail_pressure_delta=0.5,
        )
