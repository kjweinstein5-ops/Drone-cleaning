"""Pre-built simulation scenario: full Sense→Fuse→Plan→Execute→Verify loop without hardware.

Run with: python -m sim.scenario
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import List

from propwash.backend.models.prescription import ChemicalType, CoveragePattern, Prescription
from propwash.backend.models.verification import VerificationResult, Verdict
from propwash.backend.models.work_order import WorkOrder, WorkOrderStatus
from propwash.backend.models.zone import DataSource, SurfaceType, ZoneSignature
from propwash.backend.safety.checks import SafetyChecker
from sim.mock_transport import MockTransport
from sim.telemetry_simulator import TelemetrySimulator

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s — %(message)s")
logger = logging.getLogger("sim.scenario")


class SimScenario:
    """Full-loop simulation using hardcoded zones (no LLM calls needed for dev)."""

    DEMO_ZONES: List[ZoneSignature] = [
        ZoneSignature(
            zone_id="RF-S",
            label="Roof — south slope (composite shingle)",
            surface_type=SurfaceType.COMPOSITE_SHINGLE,
            pitch_deg=32,
            grime_confidence=0.87,
            moisture_index=0.65,
            source=[DataSource.THERMAL, DataSource.RGB, DataSource.SFM],
            property_id="PROP-001",
            job_id="job_demo_001",
        ),
        ZoneSignature(
            zone_id="SOL-W",
            label="Solar array — west roof",
            surface_type=SurfaceType.SOLAR_PANEL,
            pitch_deg=18,
            grime_confidence=0.55,
            moisture_index=0.20,
            source=[DataSource.THERMAL, DataSource.RGB],
            property_id="PROP-001",
            job_id="job_demo_001",
        ),
        ZoneSignature(
            zone_id="STUCCO-N",
            label="North facade — stucco",
            surface_type=SurfaceType.STUCCO,
            pitch_deg=90,
            grime_confidence=0.72,
            moisture_index=0.45,
            source=[DataSource.THERMAL, DataSource.RGB],
            property_id="PROP-001",
            job_id="job_demo_001",
        ),
    ]

    DEMO_PRESCRIPTIONS = {
        "RF-S": Prescription(
            zone_id="RF-S",
            pressure_bar=5.5,
            chemical=ChemicalType.ECO_DEGREASER,
            chemical_mix_ratio=0.35,
            dwell_seconds=35,
            nozzle_id=2,
            nozzle_angle_deg=40,
            nozzle_orifice_mm=0.5,
            standoff_m=1.2,
            coverage_pattern=CoveragePattern.SWEEP_NS,
        ),
        "SOL-W": Prescription(
            zone_id="SOL-W",
            pressure_bar=1.8,
            chemical=ChemicalType.DI_WATER_ONLY,
            chemical_mix_ratio=0.0,
            dwell_seconds=20,
            nozzle_id=4,
            nozzle_angle_deg=25,
            nozzle_orifice_mm=0.35,
            standoff_m=0.8,
            coverage_pattern=CoveragePattern.SWEEP_EW,
        ),
        "STUCCO-N": Prescription(
            zone_id="STUCCO-N",
            pressure_bar=4.0,
            chemical=ChemicalType.STANDARD_DEGREASER,
            chemical_mix_ratio=0.30,
            dwell_seconds=30,
            nozzle_id=3,
            nozzle_angle_deg=40,
            nozzle_orifice_mm=0.6,
            standoff_m=1.0,
            coverage_pattern=CoveragePattern.SWEEP_NS,
        ),
    }

    def __init__(self, fail_zones: list[str] | None = None) -> None:
        self._transport = MockTransport(
            execution_duration_s=1.5,
            fail_zone_ids=fail_zones or [],
            on_status_change=lambda job_id, status: logger.info(
                "  [transport] %s → %s", job_id, status.value
            ),
        )
        self._sim = TelemetrySimulator()
        self._safety = SafetyChecker()

    async def run(self) -> None:
        logger.info("=" * 60)
        logger.info("PROPWASH sim — full loop (no hardware required)")
        logger.info("Property: PROP-001 | Job: job_demo_001")
        logger.info("=" * 60)

        date_str = datetime.utcnow().strftime("%Y%m%d")
        work_orders: List[WorkOrder] = []

        # Build + safety-check work orders
        for i, zone in enumerate(self.DEMO_ZONES):
            prescription = self.DEMO_PRESCRIPTIONS[zone.zone_id]
            safety = self._safety.check_prescription(prescription, zone.surface_type)
            if not safety.passed:
                for v in safety.violations:
                    logger.error("SAFETY BLOCK zone=%s: %s", zone.zone_id, v.message)
                continue

            wo = WorkOrder(
                job_id=f"job_{date_str}_{i+1:03d}",
                zone=zone,
                prescription=prescription,
                verify_thermal_post=True,
            )
            work_orders.append(wo)
            logger.info(
                "Queued %s | %s | %.1f bar | %s",
                wo.job_id, zone.zone_id, prescription.pressure_bar, prescription.chemical,
            )

        logger.info("-" * 60)

        # Execute + verify each zone
        for wo in work_orders:
            logger.info("\n>>> Executing zone: %s (%s)", wo.zone.zone_id, wo.zone.label)

            # Dispatch
            await self._transport.dispatch(wo)
            await asyncio.sleep(2.0)  # wait for mock execution

            # Simulated execution telemetry
            exec_log = self._sim.execution_log(
                wo.prescription.pressure_bar,
                wo.prescription.dwell_seconds,
                wo.prescription.nozzle_id,
                success=wo.zone.zone_id not in self._transport._fail_zone_ids,
            )
            logger.info("  Execution telemetry: %s", json.dumps(exec_log, indent=2))

            # Post-clean verification
            success = wo.zone.zone_id not in self._transport._fail_zone_ids
            post_thermal = self._sim.post_clean_thermal(
                wo.zone.zone_id, wo.zone.grime_confidence, success=success
            )
            residual = max(0.0, wo.zone.grime_confidence * (0.08 if success else 0.75))

            result = VerificationResult.evaluate(
                zone_id=wo.zone.zone_id,
                job_id=wo.job_id,
                attempt=wo.attempt,
                residual_confidence=residual,
                threshold=0.15,
                execution_vs_prescription=exec_log,
            )

            verdict_icon = "✓ PASS" if result.verdict == Verdict.PASS else "✗ FAIL"
            logger.info(
                "  Verification: %s | residual=%.3f | threshold=%.2f",
                verdict_icon, result.residual_confidence, result.threshold,
            )

            if result.verdict == Verdict.FAIL:
                logger.warning("  → Zone %s flagged for re-queue", wo.zone.zone_id)

        logger.info("\n" + "=" * 60)
        logger.info("Simulation complete.")


async def run_demo_scenario() -> None:
    scenario = SimScenario(fail_zones=["STUCCO-N"])
    await scenario.run()


if __name__ == "__main__":
    asyncio.run(run_demo_scenario())
