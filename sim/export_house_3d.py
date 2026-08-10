"""Run the full pipeline on the synthetic house and emit the 3D twin JSON.

    python -m sim.export_house_3d            # print JSON
    python -m sim.export_house_3d --write    # also write samples/house_3d.json

This is the data behind the interactive 3D artifact and the visor's Twin Viewer.
Every number in it — geometry, surface class, grime proxy, phase pressures, the
fleet schedule and the deconfliction verdict — comes from the pipeline. Nothing
here is hand-authored, which is the whole point: the demo is the system running.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

from propwash.backend.fusion.scan_pipeline import grime_layer, run_scan_pipeline
from propwash.backend.fusion.thermal_registration import register_thermal
from propwash.backend.geometry.source import SyntheticHouseSource
from propwash.backend.planning.coverage_path import (
    build_flight_plan,
    build_phased_flight_plan,
)
from propwash.backend.planning.deconfliction import ConflictMap, ZoneVolume
from propwash.backend.planning.scan_to_plan import plan_from_scan
from propwash.backend.planning.treatment_phases import build_phase_plan, schedule_phases
from sim.scan_demo import synth_thermal_samples

FLEET_SIZES = (1, 2, 3)

PROPERTY_LABEL = "Ocean Hills residence — single-family"
PROPERTY_ADDRESS = "3412 Seacrest Dr, Carlsbad, CA"

#: Human-readable names for the demo house's zones. Keys are zone_id prefixes;
#: purely presentational — nothing in the pipeline depends on them.
_ZONE_LABELS = {
    "RF-S": "Roof — south slope",
    "RF-N": "Roof — north slope",
    "GABLE-W": "Gable end — west",
    "GABLE-E": "Gable end — east",
    "WALL-S": "Façade — south (front)",
    "WALL-N": "Façade — north (rear)",
    "WALL-W": "Façade — west",
    "DOOR": "Front door",
    "WIN-S1": "Window — front left",
    "WIN-S2": "Window — front right",
    "WIN-W": "Window — west",
    "WIN-N": "Window — rear",
    "SOL-ROOF": "Rooftop solar array",
    "CHIMNEY": "Chimney",
    "HVAC": "HVAC condenser",
    "GAR-RF-S": "Garage roof — south slope",
    "GAR-RF-N": "Garage roof — north slope",
    "GAR-GABLE-E": "Garage gable end — east",
    "GAR-WALL-S": "Garage wall — south",
    "GAR-WALL-E": "Garage wall — east",
    "GAR-WALL-N": "Garage wall — north",
    "GAR-DOOR": "Garage door",
}


def build_view() -> dict:
    source = SyntheticHouseSource(property_id="sim_house_carlsbad")
    recon = source.load()
    samples = synth_thermal_samples(recon.faces)
    thermal = register_thermal(samples)
    layer = grime_layer(recon, thermal)          # per-face, the zoomable detail
    zones = run_scan_pipeline(source, samples)
    plan = plan_from_scan(zones, job_id="job_house_001", property_id="sim_house_carlsbad")

    by_zone = {z.zone_id: z for z in zones}
    presc = {wo.zone.zone_id: wo.prescription for wo in plan.work_orders}

    # ── per-face geometry carrying its OWN grime + temperature ───────────────
    # `g` is the face's value, not the zone mean, so zooming in resolves real
    # within-zone structure (eaves, wall bases, shaded elevations) instead of
    # magnifying a flat fill.
    faces = []
    spread: Dict[str, list] = {}
    for f in recon.faces:
        zid = f.face_id.rsplit("-", 1)[0]
        z = by_zone.get(zid)
        if z is None:
            continue
        fg = layer[f.face_id]
        reading = thermal.get(f.face_id)
        temp = (reading.temp_c if reading and reading.sample_count else z.temp_c)
        spread.setdefault(zid, []).append(fg.grime)
        faces.append({
            "zone": zid,
            "v": [[round(c, 3) for c in f.v0],
                  [round(c, 3) for c in f.v1],
                  [round(c, 3) for c in f.v2]],
            "g": fg.grime,
            "excl": z.is_exclusion,
            "solar": z.solar,
            "surf": z.surface_type,
            "temp": round(temp, 1),
        })

    # ── per-zone detail for the inspector panel ──────────────────────────────
    zone_view: Dict[str, dict] = {}
    for z in sorted(zones, key=lambda z: z.zone_id):
        p = presc.get(z.zone_id)
        zone_view[z.zone_id] = {
            "label": _ZONE_LABELS.get(z.zone_id, z.zone_id),
            "surf": z.surface_type,
            "g": round(z.grime_proxy, 3),
            "excl": z.is_exclusion,
            "solar": z.solar,
            "temp": round(z.temp_c, 1),
            "moisture": round(z.moisture_index, 3),
            "gMin": round(min(spread.get(z.zone_id, [z.grime_proxy])), 3),
            "gMax": round(max(spread.get(z.zone_id, [z.grime_proxy])), 3),
            "faces": z.face_count,
            "pitch": round(z.pitch_deg, 1),
            "conf": round(z.confidence, 2),
            "reason": z.reason,
            "p": round(p.pressure_bar, 2) if p else None,
            "chem": p.chemical.value if p else None,
            "nozzle": p.nozzle_id if p else None,
            "dwell": p.dwell_seconds if p else None,
            "standoff": p.standoff_m if p else None,
            "mix": p.chemical_mix_ratio if p else None,
        }

    # ── treatment passes per zone (pre-soak / chemical / rinse) ──────────────
    phased = build_phased_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    phases: Dict[str, List[dict]] = {}
    for zp in phased.zone_paths:
        if zp.phase is None:
            continue
        phases.setdefault(zp.zone_id, []).append({
            "ph": zp.phase,
            "p": round(zp.phase_pressure_bar, 2),
            "c": zp.phase_chemical,
        })

    # ── fleet schedule + spatial deconfliction ───────────────────────────────
    base = build_flight_plan(recon, plan.work_orders, exclusions=plan.excluded)
    plans = [
        build_phase_plan(zp.zone_id, presc[zp.zone_id], zp.est_seconds)
        for zp in base.zone_paths if zp.zone_id in presc
    ]
    volumes = [
        ZoneVolume.from_points(
            zp.zone_id,
            [(w.x, w.y, w.z) for w in zp.waypoints],
            zp.standoff_m,
        )
        for zp in base.zone_paths if zp.waypoints
    ]
    conflicts = ConflictMap(volumes)
    # Two schedules, deliberately: `schedule` is what this site can actually do
    # with spatial deconfliction enforced (Tier-1, non-negotiable); `ideal` is
    # the same work with the geometry constraint lifted. The gap between them is
    # the honest measure of what a compact property costs you.
    schedule = {
        str(n): round(schedule_phases(plans, n, conflicts).makespan_s / 60.0, 1)
        for n in FLEET_SIZES
    }
    schedule_ideal = {
        str(n): round(schedule_phases(plans, n).makespan_s / 60.0, 1)
        for n in FLEET_SIZES
    }

    return {
        "property": PROPERTY_LABEL,
        "address": PROPERTY_ADDRESS,
        "captured": recon.captured_at[:10],
        "faces": faces,
        "zones": zone_view,
        "phases": phases,
        "schedule": schedule,
        "scheduleIdeal": schedule_ideal,
        "maxConcurrent": conflicts.max_concurrent_aircraft(),
        "separations": conflicts.separation_report(),
        "counts": {
            "faces": len(faces),
            "zones": len(zone_view),
            "clean": len(plan.work_orders),
            "excl": len(plan.excluded),
            "passes": sum(len(v) for v in phases.values()),
        },
    }


def main() -> None:
    view = build_view()
    text = json.dumps(view)
    if "--write" in sys.argv:
        out = Path(__file__).resolve().parent.parent / "samples" / "house_3d.json"
        out.write_text(text)
        print(f"wrote {out}  {view['counts']}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
