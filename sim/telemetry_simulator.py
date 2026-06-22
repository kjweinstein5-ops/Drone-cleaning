"""Telemetry simulator — generates realistic mock sensor readings for dev/testing.

Simulates Autel EVO II 640T radiometric thermal + RGB outputs and
Sherpa pump telemetry without requiring real hardware.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ThermalFrame:
    """Simulated Autel 640T thermal frame."""
    timestamp: datetime
    width: int = 640
    height: int = 512
    min_temp_c: float = 18.0
    max_temp_c: float = 45.0
    mean_temp_c: float = 28.0
    zone_deltas: Dict[str, float] = field(default_factory=dict)


@dataclass
class PumpTelemetry:
    """Simulated Sherpa pump telemetry (Path A only — operator-read values)."""
    timestamp: datetime
    pressure_bar: float
    flow_lpm: float
    chemical_ratio: float
    nozzle_id: int
    operator_confirmed: bool = False


class TelemetrySimulator:
    """Generates mock telemetry streams for the full cleaning loop."""

    def __init__(self, noise_factor: float = 0.05) -> None:
        self._noise = noise_factor

    def _jitter(self, value: float) -> float:
        return value * (1.0 + random.uniform(-self._noise, self._noise))

    def pre_clean_thermal(self, zone_id: str, grime_confidence: float) -> ThermalFrame:
        """Simulate a pre-clean thermal frame; high grime → cooler zone (evaporation)."""
        base_temp = 32.0
        # Biofilm tends to retain moisture → slightly cooler under solar heating
        zone_delta = -3.5 * grime_confidence + random.uniform(-0.5, 0.5)
        return ThermalFrame(
            timestamp=datetime.utcnow(),
            mean_temp_c=self._jitter(base_temp),
            zone_deltas={zone_id: zone_delta},
        )

    def post_clean_thermal(
        self, zone_id: str, prescribed_confidence: float, success: bool = True
    ) -> ThermalFrame:
        """Simulate post-clean thermal; successful clean → zone warms (less moisture)."""
        residual = (prescribed_confidence * 0.08) if success else (prescribed_confidence * 0.75)
        residual = max(0.0, min(1.0, self._jitter(residual)))
        zone_delta = -1.5 * residual + random.uniform(-0.3, 0.3)
        return ThermalFrame(
            timestamp=datetime.utcnow(),
            mean_temp_c=self._jitter(34.0),
            zone_deltas={zone_id: zone_delta},
        )

    def pump_telemetry(self, prescribed_pressure_bar: float, nozzle_id: int) -> PumpTelemetry:
        """Simulate operator-executed pump readings (slight real-world variance)."""
        return PumpTelemetry(
            timestamp=datetime.utcnow(),
            pressure_bar=self._jitter(prescribed_pressure_bar),
            flow_lpm=self._jitter(4.5),
            chemical_ratio=self._jitter(0.30),
            nozzle_id=nozzle_id,
            operator_confirmed=True,
        )

    def execution_log(
        self,
        prescription_pressure: float,
        prescription_dwell: int,
        nozzle_id: int,
        success: bool = True,
    ) -> Dict[str, Any]:
        actual_pressure = self._jitter(prescription_pressure)
        actual_dwell = int(self._jitter(float(prescription_dwell)))
        return {
            "actual_pressure_bar": round(actual_pressure, 3),
            "prescribed_pressure_bar": prescription_pressure,
            "actual_dwell_seconds": actual_dwell,
            "prescribed_dwell_seconds": prescription_dwell,
            "nozzle_id": nozzle_id,
            "operator_confirmed": True,
            "deviation_pressure_pct": round(
                abs(actual_pressure - prescription_pressure) / prescription_pressure * 100, 1
            ),
        }
