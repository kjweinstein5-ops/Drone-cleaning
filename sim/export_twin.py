"""Run the drone-scan pipeline and emit the Twin Viewer JSON.

    python -m sim.export_twin            # print JSON
    python -m sim.export_twin --write    # also write samples/scan_twin.json

Proves the visor data comes from the pipeline, not a hand-typed mock.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from propwash.backend.geometry.source import SyntheticBuildingSource
from propwash.backend.fusion.scan_pipeline import run_scan_pipeline
from propwash.backend.fusion.twin_export import scanned_zones_to_view
from sim.scan_demo import synth_thermal_samples


def build_view() -> dict:
    source = SyntheticBuildingSource(property_id="sim_carlsbad_bldg_c")
    recon = source.load()
    samples = synth_thermal_samples(recon.faces)
    zones = run_scan_pipeline(source, samples)
    return scanned_zones_to_view(
        recon, zones,
        property_label="Carlsbad Commerce Center — Bldg C",
        address="2200 Faraday Ave, Carlsbad, CA",
    )


def main() -> None:
    view = build_view()
    text = json.dumps(view, indent=2)
    print(text)
    if "--write" in sys.argv:
        out = Path(__file__).resolve().parent.parent / "samples" / "scan_twin.json"
        out.write_text(text)
        print(f"\nwrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
