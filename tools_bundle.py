"""Concatenate every PROPWASH document into one pasteable file.

    python tools_bundle.py            # -> PROPWASH_COMPLETE.md

Everything in docs/ plus CLAUDE.md and the prescription table, in reading order,
with a table of contents. Regenerate after any doc changes rather than editing
the bundle by hand — it is output, not source.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "PROPWASH_COMPLETE.md"
OUT_ESSENTIALS = ROOT / "PROPWASH_ESSENTIALS.md"

#: The six documents that carry the argument. Everything else is supporting detail.
#: Exists because the full bundle is ~72k words — too long to paste into a chat window.
ESSENTIALS = [
    "CLAUDE.md",
    "docs/GO_NO_GO.md",
    "docs/COMPETITIVE_LANDSCAPE.md",
    "docs/decisions/VERDICT_AND_PRICES.md",
    "docs/decisions/PAYLOAD_BUILD_SPEC.md",
    "docs/FIELD_OPERATIONS.md",
]

# Reading order: context first, then why, then what to buy, then how it works, then ops.
ORDER = [
    ("PROJECT CONTEXT", ["CLAUDE.md"]),
    ("STRATEGY — is this worth doing", [
        "docs/GO_NO_GO.md",
        "docs/COMPETITIVE_LANDSCAPE.md",
        "docs/BUSINESS_PLAN.md",
        "docs/SCALING_TO_10M.md",
        "docs/BRAND_NAMING.md",
    ]),
    ("HARDWARE — what to buy", [
        "docs/decisions/PAYLOAD_BUILD_SPEC.md",
        "docs/decisions/VERDICT_AND_PRICES.md",
        "docs/decisions/FLEET_ARCHITECTURE.md",
        "docs/decisions/PLATFORM_VENDOR_CHOICE.md",
        "docs/decisions/INTEGRABLE_PLATFORM.md",
        "docs/decisions/AIRFRAME_CONTENDERS.md",
        "docs/decisions/PURPOSE_BUILT_SCAN.md",
        "docs/decisions/CLEANING_DRONE_PLATFORM.md",
        "docs/decisions/OPEN_PLATFORM_INTEGRATION.md",
        "docs/decisions/DJI_TWO_DRONE_ARCHITECTURE.md",
        "docs/decisions/SENSOR_PLATFORM_SHORTLIST.md",
        "docs/decisions/SPECTRAL_SENSING_DECISION.md",
        "docs/decisions/BUILD_SPEC.md",
        "docs/decisions/CLEANING_METHODS.md",
        "docs/decisions/COMPUTE_INFRASTRUCTURE.md",
    ]),
    ("TECHNICAL — how the loop works", [
        "docs/3D_DATA_PIPELINE.md",
        "docs/THERMAL_LAYERING_PIPELINE.md",
        "docs/THERMOGRAPHIC_DIGITAL_TWIN.md",
        "docs/DYNAMIC_PRESSURE_HARDWARE.md",
        "docs/FLIGHT_SOFTWARE_STACK.md",
        "docs/COMMUNICATION_AND_AUTONOMY.md",
    ]),
    ("OPERATIONS & REGULATORY", [
        "docs/FIELD_OPERATIONS.md",
        "docs/LAUNCH_PLAYBOOK.md",
        "docs/REGULATORY_STRATEGY.md",
        "docs/WAIVER_107_35.md",
    ]),
    ("BUSINESS — IP and vendors", [
        "docs/IP_PROTECTION.md",
        "docs/VENDOR_OUTREACH.md",
        "docs/LUCID_OUTREACH.md",
    ]),
]


def _demote(md: str) -> str:
    """Push every heading down one level so bundle sections stay above them.

    Fenced code blocks are skipped — a '#' comment inside one is not a heading.
    """
    out, fenced = [], False
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("#"):
            line = "#" + line
        out.append(line)
    return "\n".join(out)


def main() -> None:
    parts, toc, missing = [], [], []
    for section, paths in ORDER:
        toc.append(f"\n### {section}\n")
        for rel in paths:
            p = ROOT / rel
            if not p.exists():
                missing.append(rel)
                continue
            body = p.read_text()
            title = next((l.lstrip("# ").strip() for l in body.splitlines()
                          if l.startswith("# ")), Path(rel).stem)
            anchor = rel.replace("/", "").replace(".md", "").replace("_", "").lower()
            toc.append(f"- [{title}](#{anchor}) · `{rel}`")
            parts.append(f'\n\n<a id="{anchor}"></a>\n\n---\n\n'
                         f"# {title}\n\n> **Source file:** `{rel}`\n\n{_demote(body)}")

    presc = ROOT / "prescriptions/surface_treatment_v1.json"
    if presc.exists():
        toc.append("\n### DATA\n- [Surface treatment table](#surfacetable) · "
                   "`prescriptions/surface_treatment_v1.json`")
        parts.append('\n\n<a id="surfacetable"></a>\n\n---\n\n# Surface treatment table\n\n'
                     "> **Source file:** `prescriptions/surface_treatment_v1.json`\n>\n"
                     "> Versioned data, not code (CLAUDE.md §9). These are **starting "
                     "assumptions to calibrate**, not validated constants.\n\n"
                     "```json\n" + json.dumps(json.loads(presc.read_text()), indent=2) + "\n```")

    header = f"""# PROPWASH — complete project documentation

> AI-orchestrated exterior building cleaning · Carlsbad, CA
> Generated {dt.date.today().isoformat()} from the `Drone-cleaning` repository.
>
> **This file is generated.** Edit the source files listed under each section and re-run
> `python tools_bundle.py`; edits made here are lost on the next build.

**Read this first:** every price is public list and subject to quote — nothing here is a bid.
Pressure, dwell and chemical figures are **uncalibrated starting assumptions**, not validated
constants. Items marked ⚠️ **UNVERIFIED** or **OPEN** are exactly that. Nothing in this document
is legal, aviation-regulatory, insurance or financial advice.

---

## Contents
{chr(10).join(toc)}
"""
    OUT.write_text(header + "".join(parts) + "\n")
    _report(OUT, len(parts))

    ess = [f"# PROPWASH — the essentials\n\n"
           f"> Generated {dt.date.today().isoformat()}. The six documents that carry the "
           f"argument, for pasting where the full bundle is too long.\n>\n"
           f"> Full version: `PROPWASH_COMPLETE.md` (35 documents).\n"]
    for rel in ESSENTIALS:
        body = (ROOT / rel).read_text()
        title = next((l.lstrip("# ").strip() for l in body.splitlines()
                      if l.startswith("# ")), Path(rel).stem)
        ess.append(f"\n\n---\n\n# {title}\n\n> **Source file:** `{rel}`\n\n{_demote(body)}")
    OUT_ESSENTIALS.write_text("".join(ess) + "\n")
    _report(OUT_ESSENTIALS, len(ESSENTIALS))

    if missing:
        print("missing (skipped):", ", ".join(missing))


def _report(path: Path, count: int) -> None:
    text = path.read_text()
    print(f"{path.name}: {count} documents · {len(text.splitlines()):,} lines · "
          f"~{len(text.split()):,} words · {path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
