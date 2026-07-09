"""Convert drone-scan pipeline output into the visor's Twin Viewer format.

Bridges scan_pipeline (ScannedZone) → the JSON the visor renders. The plan-view
tile layout is derived from the actual mesh geometry (XY bounds of each zone's
faces), so the visor reflects the real scan, not a hand-placed mock.
"""

from __future__ import annotations

from typing import Dict, List

from propwash.backend.geometry.source import ReconstructionOutput
from propwash.backend.fusion.scan_pipeline import ScannedZone, _zone_key

# Cleanable zones drop to this residual grime after a verified clean (demo toggle).
_POST_CLEAN_RESIDUAL = 0.05
_MIN_TILE = 0.08  # normalized min tile size so thin walls stay visible


def scanned_zones_to_view(
    recon: ReconstructionOutput,
    zones: List[ScannedZone],
    property_label: str,
    address: str = "",
) -> dict:
    """Build the Twin Viewer payload from pipeline output + geometry."""
    faces_by_zone: Dict[str, list] = {}
    for f in recon.faces:
        faces_by_zone.setdefault(_zone_key(f.face_id), []).append(f)

    xs = [f.centroid[0] for f in recon.faces]
    ys = [f.centroid[1] for f in recon.faces]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = (max_x - min_x) or 1.0
    span_y = (max_y - min_y) or 1.0

    view_zones = []
    for z in zones:
        faces = faces_by_zone.get(z.zone_id, [])
        cxs = [f.centroid[0] for f in faces] or [min_x]
        cys = [f.centroid[1] for f in faces] or [min_y]
        x0 = (min(cxs) - min_x) / span_x
        x1 = (max(cxs) - min_x) / span_x
        y0 = (min(cys) - min_y) / span_y
        y1 = (max(cys) - min_y) / span_y
        w = max(_MIN_TILE, x1 - x0)
        h = max(_MIN_TILE, y1 - y0)

        grime_post = None if z.is_exclusion else _POST_CLEAN_RESIDUAL

        view_zones.append({
            "zone_id": z.zone_id,
            "surface_type": z.surface_type,
            "is_exclusion": z.is_exclusion,
            "solar": z.solar,
            "gPre": z.grime_proxy,
            "gPost": grime_post,
            "temp": None if z.temp_c != z.temp_c else z.temp_c,  # NaN → None
            "moisture": z.moisture_index,
            "pitch": z.pitch_deg,
            "confidence": z.confidence,
            "reason": z.reason,
            # normalized plan-view rect (0..1)
            "x": round(min(x0, 1 - w), 3),
            "y": round(min(y0, 1 - h), 3),
            "w": round(min(w, 1.0), 3),
            "h": round(min(h, 1.0), 3),
        })

    cleanable = [z for z in view_zones if not z["is_exclusion"]]
    return {
        "property": property_label,
        "address": address,
        "captured": recon.captured_at[:10],
        "source": "drone-scan pipeline",
        "cleanable_count": len(cleanable),
        "exclusion_count": len(view_zones) - len(cleanable),
        "zones": view_zones,
    }
