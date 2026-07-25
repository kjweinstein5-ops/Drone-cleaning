"""End-to-end demo: drone scan → classified zones → cleaning plan → FLIGHT PATH.

Extends scan_to_plan_demo with Stage 5: turns the safety-gated work orders into a
coverage flight path (standoff sweeps, ordered solar-first/top-down, with keep-out
volumes around exclusion zones).

    python -m sim.flight_plan_demo
"""

from __future__ import annotations

from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.planning.scan_to_plan import plan_from_scan
from propwash.backend.planning.coverage_path import build_flight_plan
from sim.scan_demo import synth_thermal_samples


def main() -> None:
    source = SyntheticBuildingSource(property_id="sim_carlsbad_bldg_c")
    recon = source.load()
    zones = run_scan_pipeline(source, synth_thermal_samples(recon.faces))
    plan = plan_from_scan(zones, job_id="job_20260706_001", property_id="sim_carlsbad_bldg_c")
    flight = build_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)

    print("\nPROPWASH — scan → plan → FLIGHT PATH (synthetic building)\n")
    print(f"{'#':>2} {'ZONE':<10}{'SURFACE':<16}{'STANDOFF':>9}{'SWATH':>8}{'WAYPTS':>8}{'LEN':>8}{'~TIME':>8}")
    print("-" * 74)
    for i, zp in enumerate(flight.zone_paths, 1):
        tag = " ☀" if zp.solar else ""
        print(f"{i:>2} {zp.zone_id:<10}{zp.surface_type:<16}{zp.standoff_m:>7.1f} m"
              f"{zp.spray_width_m:>7.2f}m{len(zp.waypoints):>8}{zp.path_length_m:>6.1f} m"
              f"{zp.est_seconds:>6.0f}s{tag}")
    print("-" * 74)

    print(f"\nOrder: solar-first, then top-down, gutters last (physics + safety).")
    print(f"Keep-out volumes (no-fly / no-spray):")
    for ko in flight.keep_outs:
        print(f"   ⛔ {ko.zone_id:<10} center≈({ko.center[0]:.1f},{ko.center[1]:.1f},{ko.center[2]:.1f}) "
              f"r={ko.radius_m} m — {ko.reason}")

    print(f"\n{len(flight.zone_paths)} zones · {flight.total_waypoints} waypoints · "
          f"~{flight.est_minutes:.1f} min · {flight.total_keepout_violations} keep-out violations")
    print("Output is OPERATOR GUIDANCE, not an autonomous command (CLAUDE.md §7/§10).\n")


if __name__ == "__main__":
    main()
