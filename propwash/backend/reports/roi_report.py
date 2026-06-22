"""Customer ROI report generator — PROPWASH's sales + retention engine.

Turns a completed job (pre-clean zone signatures + post-clean verification) into a
before/after report a customer can act on. For solar zones it estimates recovered
output and dollar value from the measured soiling reduction.

HONESTY CONSTRAINTS (CLAUDE.md §5):
- grime_confidence / residual_confidence are THERMAL+RGB PROXY scores, not spectral
  measurements. The report labels them as estimates and prints its assumptions.
- The soiling→output model is a documented heuristic, calibrated from field data over
  time (§9). Do not present estimates as guaranteed measurements.

No third-party templating dependency — emits a self-contained HTML string.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

from propwash.backend.models.verification import Verdict
from propwash.backend.models.zone import SurfaceType


# Soiling-loss model parameters — STARTING ASSUMPTIONS, calibrate from field data (§9).
# Maps a grime proxy of 1.0 to this fractional output loss for solar at heavy soiling.
SOLAR_MAX_SOILING_LOSS = 0.20  # 20% at worst-case soiling (conservative upper bound)


@dataclass
class SolarROIInput:
    """Per-solar-zone inputs needed to estimate recovered output and value."""

    system_kw: float                      # nameplate capacity of the array for this zone
    annual_kwh_per_kw: float = 1600.0     # San Diego ~1600 kWh/kW/yr (high-insolation default)
    electricity_price_per_kwh: float = 0.30  # $/kWh (CA commercial-ish default)
    months_until_resoil: int = 6          # benefit horizon before next clean


@dataclass
class ZoneResult:
    """A single zone's before/after outcome for the report."""

    zone_id: str
    label: str
    surface_type: SurfaceType
    pre_grime_confidence: float           # proxy, 0..1
    post_residual_confidence: float       # proxy, 0..1
    verdict: Verdict
    solar: Optional[SolarROIInput] = None

    @property
    def soiling_removed_pct(self) -> float:
        """Reduction in the grime proxy, as a percentage (display metric)."""
        return max(0.0, (self.pre_grime_confidence - self.post_residual_confidence)) * 100.0

    def estimated_recovered_kwh(self) -> float:
        """Estimated kWh recovered over the benefit horizon (solar zones only).

        Output loss is modeled as proportional to the soiling proxy. Recovered loss
        fraction = (pre - post) * SOLAR_MAX_SOILING_LOSS. This is an ESTIMATE (§5).
        """
        if self.surface_type != SurfaceType.SOLAR_PANEL or self.solar is None:
            return 0.0
        recovered_loss_fraction = max(
            0.0, (self.pre_grime_confidence - self.post_residual_confidence)
        ) * SOLAR_MAX_SOILING_LOSS
        annual_kwh = self.solar.system_kw * self.solar.annual_kwh_per_kw
        horizon_fraction = self.solar.months_until_resoil / 12.0
        return annual_kwh * recovered_loss_fraction * horizon_fraction

    def estimated_recovered_value(self) -> float:
        if self.solar is None:
            return 0.0
        return self.estimated_recovered_kwh() * self.solar.electricity_price_per_kwh


@dataclass
class ROIReport:
    """A complete customer-facing job report."""

    property_name: str
    property_address: str
    job_id: str
    job_date: date
    zones: List[ZoneResult] = field(default_factory=list)

    def total_recovered_kwh(self) -> float:
        return sum(z.estimated_recovered_kwh() for z in self.zones)

    def total_recovered_value(self) -> float:
        return sum(z.estimated_recovered_value() for z in self.zones)

    def zones_passed(self) -> int:
        return sum(1 for z in self.zones if z.verdict == Verdict.PASS)


def _verdict_badge(verdict: Verdict) -> str:
    color = "#1a9e54" if verdict == Verdict.PASS else "#c0392b"
    text = "VERIFIED CLEAN" if verdict == Verdict.PASS else "RE-QUEUED"
    return f'<span style="background:{color};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">{text}</span>'


def _zone_row(z: ZoneResult) -> str:
    is_solar = z.surface_type == SurfaceType.SOLAR_PANEL and z.solar is not None
    recovered = (
        f"{z.estimated_recovered_kwh():,.0f} kWh / ${z.estimated_recovered_value():,.0f}"
        if is_solar
        else "—"
    )
    return f"""
      <tr>
        <td><strong>{html.escape(z.label)}</strong><br><span class="muted">{html.escape(z.zone_id)}</span></td>
        <td>{html.escape(z.surface_type.value)}</td>
        <td>{z.pre_grime_confidence:.2f}</td>
        <td>{z.post_residual_confidence:.2f}</td>
        <td><strong>{z.soiling_removed_pct:.0f}%</strong></td>
        <td>{recovered}</td>
        <td>{_verdict_badge(z.verdict)}</td>
      </tr>"""


def generate_html_report(report: ROIReport) -> str:
    """Render a self-contained HTML ROI report (no external assets)."""
    rows = "".join(_zone_row(z) for z in report.zones)
    has_solar = any(
        z.surface_type == SurfaceType.SOLAR_PANEL and z.solar is not None for z in report.zones
    )

    solar_summary = ""
    if has_solar:
        solar_summary = f"""
      <div class="hero">
        <div class="hero-num">${report.total_recovered_value():,.0f}</div>
        <div class="hero-label">estimated recovered value over benefit horizon</div>
        <div class="hero-sub">{report.total_recovered_kwh():,.0f} kWh of estimated output restored</div>
      </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PROPWASH ROI Report — {html.escape(report.property_name)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         color:#1c2733; margin:0; background:#f4f6f8; }}
  .wrap {{ max-width:780px; margin:0 auto; padding:32px 20px; }}
  .brand {{ font-weight:800; letter-spacing:1px; color:#0b6cc4; font-size:20px; }}
  .card {{ background:#fff; border-radius:14px; padding:24px; margin:18px 0;
          box-shadow:0 1px 4px rgba(0,0,0,.08); }}
  h1 {{ font-size:22px; margin:4px 0 2px; }}
  .muted {{ color:#7a8794; font-size:13px; }}
  table {{ width:100%; border-collapse:collapse; margin-top:10px; font-size:14px; }}
  th, td {{ text-align:left; padding:10px 8px; border-bottom:1px solid #eef1f4; vertical-align:top; }}
  th {{ color:#7a8794; font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.5px; }}
  .hero {{ background:linear-gradient(135deg,#0b6cc4,#1a9e54); color:#fff; border-radius:14px;
          padding:28px; text-align:center; }}
  .hero-num {{ font-size:42px; font-weight:800; }}
  .hero-label {{ font-size:14px; opacity:.95; }}
  .hero-sub {{ font-size:13px; opacity:.85; margin-top:6px; }}
  .disclaimer {{ font-size:11px; color:#9aa5b1; line-height:1.5; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="brand">PROPWASH</div>
  <div class="card">
    <h1>{html.escape(report.property_name)}</h1>
    <div class="muted">{html.escape(report.property_address)}</div>
    <div class="muted">Job {html.escape(report.job_id)} &middot; {report.job_date.isoformat()} &middot;
        {report.zones_passed()}/{len(report.zones)} zones verified clean</div>
  </div>
  {solar_summary}
  <div class="card">
    <h1>Before &amp; after — by zone</h1>
    <table>
      <thead><tr>
        <th>Zone</th><th>Surface</th><th>Pre (soiling)</th><th>Post (residual)</th>
        <th>Removed</th><th>Est. recovery</th><th>Status</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <div class="card">
    <p class="disclaimer">
      <strong>How to read this report.</strong> "Soiling" and "residual" are condition scores
      derived from thermal and visible (RGB) imagery captured by our sensing drone — they are
      <em>estimates inferred from heat and visual cues, not laboratory spectral measurements</em>.
      Solar output-recovery figures are <em>estimates</em> based on a soiling-to-output model
      (max modeled loss {SOLAR_MAX_SOILING_LOSS:.0%} at worst-case soiling) and your system size,
      local insolation, electricity price, and re-soiling horizon. Actual production varies with
      weather, shading, equipment, and tariff. Figures are calibrated from field data over time and
      will be refined on repeat visits. This report is a service summary, not a guarantee of output.
    </p>
  </div>
</div>
</body>
</html>"""
