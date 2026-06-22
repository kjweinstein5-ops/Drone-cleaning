"""Deterministic safety checks — Tier 1 equivalent at the software level.

These checks are authoritative and CANNOT be overridden by any Tier-3 agent.
See CLAUDE.md §2: agents are advisory; safety layer is deterministic.

Hard pressure ceilings come from the surface treatment table. A FAIL here
must halt the work order, not silently adjust parameters.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List

from propwash.backend.models.prescription import ChemicalType, Prescription
from propwash.backend.models.zone import SurfaceType


_PRESCRIPTION_TABLE_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../prescriptions/surface_treatment_v1.json",
)

_SURFACE_TYPE_TO_TABLE_KEY = {
    SurfaceType.COMPOSITE_SHINGLE: "composite_shingle",
    SurfaceType.CLAY_TILE: "clay_tile",
    SurfaceType.CONCRETE_TILE: "concrete_tile",
    SurfaceType.SOLAR_PANEL: "solar_panel",
    SurfaceType.WINDOW_GLASS: "window_glass",
    SurfaceType.STUCCO: "stucco",
    SurfaceType.GUTTER_ALUMINUM: "gutter_aluminum",
}


def _load_surface_table() -> dict:
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), _PRESCRIPTION_TABLE_PATH[len(os.path.dirname(__file__)):]))
    # Resolve relative to this file's location
    path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../../../prescriptions/surface_treatment_v1.json")
    )
    with open(path) as f:
        return json.load(f)


@dataclass
class SafetyViolation:
    rule: str
    message: str
    fatal: bool = True


@dataclass
class SafetyCheckResult:
    passed: bool
    violations: List[SafetyViolation] = field(default_factory=list)


class SafetyChecker:
    """Stateless deterministic safety checker.

    Call check_prescription() before dispatching any work order.
    A fatal violation must prevent dispatch — not be logged and ignored.
    """

    def __init__(self) -> None:
        self._table = _load_surface_table()

    def check_prescription(self, prescription: Prescription, surface_type: SurfaceType) -> SafetyCheckResult:
        violations: List[SafetyViolation] = []

        table_key = _SURFACE_TYPE_TO_TABLE_KEY.get(surface_type)
        if table_key is None:
            violations.append(
                SafetyViolation(
                    rule="UNKNOWN_SURFACE",
                    message=f"Surface type '{surface_type}' has no safety profile — cannot dispatch.",
                    fatal=True,
                )
            )
            return SafetyCheckResult(passed=False, violations=violations)

        surface_config = self._table["surfaces"][table_key]
        hard_ceiling = surface_config["pressure_bar_hard_ceiling"]

        # Rule 1: Absolute pressure ceiling per surface
        if prescription.pressure_bar > hard_ceiling:
            violations.append(
                SafetyViolation(
                    rule="PRESSURE_EXCEEDS_HARD_CEILING",
                    message=(
                        f"Requested pressure {prescription.pressure_bar:.2f} bar exceeds "
                        f"hard ceiling {hard_ceiling:.2f} bar for {surface_type}."
                    ),
                    fatal=True,
                )
            )

        # Rule 2: Solar panels — DI water ONLY, enforced hard
        if surface_type == SurfaceType.SOLAR_PANEL:
            if prescription.chemical != ChemicalType.DI_WATER_ONLY:
                violations.append(
                    SafetyViolation(
                        rule="SOLAR_PANEL_NO_CHEMICAL",
                        message=(
                            f"Solar panels require DI_WATER_ONLY. "
                            f"Requested chemical '{prescription.chemical}' is forbidden — "
                            "detergent residue degrades panel output and may void warranty."
                        ),
                        fatal=True,
                    )
                )
            if prescription.pressure_bar > 2.0:
                violations.append(
                    SafetyViolation(
                        rule="SOLAR_PANEL_PRESSURE_CEILING",
                        message=(
                            f"Solar panel pressure ceiling is 2.0 bar. "
                            f"Requested {prescription.pressure_bar:.2f} bar — high pressure cracks cells."
                        ),
                        fatal=True,
                    )
                )

        # Rule 3: Chemical mix ratio sanity
        if prescription.chemical == ChemicalType.DI_WATER_ONLY and prescription.chemical_mix_ratio > 0.0:
            violations.append(
                SafetyViolation(
                    rule="DI_WATER_ONLY_NONZERO_RATIO",
                    message=(
                        f"Chemical is DI_WATER_ONLY but mix_ratio is {prescription.chemical_mix_ratio} "
                        "(must be 0.0)."
                    ),
                    fatal=True,
                )
            )

        # Rule 4: Safety margin must be positive
        if prescription.safety_margin_m <= 0.0:
            violations.append(
                SafetyViolation(
                    rule="ZERO_SAFETY_MARGIN",
                    message="safety_margin_m must be > 0.0.",
                    fatal=True,
                )
            )

        passed = not any(v.fatal for v in violations)
        return SafetyCheckResult(passed=passed, violations=violations)
