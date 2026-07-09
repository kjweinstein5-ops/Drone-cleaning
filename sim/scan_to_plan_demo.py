"""End-to-end demo: drone scan → classified zones → cleaning plan.

Chains the scan pipeline into the PROPWASH plan stage: surface classification →
prescription (from the versioned table) → deterministic safety gate → work orders.
Exclusion zones are dropped; nothing unsafe is queued.

    python -m sim.scan_to_plan_demo
"""

from __future__ import annotations

from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.planning.scan_to_plan import plan_from_scan
from sim.scan_demo import synth_thermal_samples


def main() -> None:
    source = SyntheticBuildingSource(property_id="sim_carlsbad_bldg_c")
    recon = source.load()
    zones = run_scan_pipeline(source, synth_thermal_samples(recon.faces))
    plan = plan_from_scan(zones, job_id="job_20260706_001", property_id="sim_carlsbad_bldg_c")

    print("\nPROPWASH — scan → plan (synthetic building)\n")
    print(f"{'ZONE':<10}{'SURFACE':<18}{'PRESSURE':>9}{'CHEMICAL':>22}{'NOZZLE':>8}{'DWELL':>7}")
    print("-" * 76)
    for wo in plan.work_orders:
        p = wo.prescription
        print(
            f"{wo.zone.zone_id:<10}{wo.zone.surface_type.value:<18}"
            f"{p.pressure_bar:>7.1f} b{p.chemical.value:>22}"
            f"{p.nozzle_id:>8}{p.dwell_seconds:>6}s"
        )
    print("-" * 76)

    if plan.excluded:
        print("\n⛔ EXCLUDED (no work order):")
        for zid, reason in plan.excluded:
            print(f"   {zid:<10} {reason}")

    if plan.safety_rejected:
        print("\n🛑 SAFETY-REJECTED (human review):")
        for zid, rules in plan.safety_rejected:
            print(f"   {zid:<10} {rules}")

    print(f"\n{plan.summary}")
    print("Every queued work order passed the deterministic safety gate (CLAUDE.md §2).\n")


if __name__ == "__main__":
    main()
