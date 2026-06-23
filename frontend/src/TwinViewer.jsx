import React, { useState } from "react";

// ── Demo twin data (mirrors /twins/prop_carlsbad_bldg_c) ─────────────────────
const DEMO_TWIN = {
  property_id: "prop_carlsbad_bldg_c",
  property_label: "Carlsbad Commerce Center — Bldg C",
  address: "2200 Faraday Ave, Carlsbad, CA",
  captured_at: "2026-06-20T09:14Z",
  total_jobs: 3,
  avg_first_pass_rate: 0.72,
  zones: [
    {
      zone_id: "SOL-ROOF", label: "Rooftop solar array", surface_type: "Solar Panel",
      pitch_deg: 18, temp_celsius_mean: 42.3, temp_celsius_min: 38.1, temp_celsius_max: 51.7,
      grime_proxy_pre: 0.71, grime_proxy_post: 0.04, moisture_index: 0.12,
      human_clear: true, pressure_prescribed_bar: 1.8, pressure_actual_bar: 1.79,
      verdict: "PASS", solar: true,
      // Grid layout: col, row, colspan, rowspan (in a 3×2 unit grid)
      col: 0, row: 0, cs: 2, rs: 1,
    },
    {
      zone_id: "RF-S", label: "Roof — south slope", surface_type: "Composite Shingle",
      pitch_deg: 38, temp_celsius_mean: 55.8, temp_celsius_min: 49.3, temp_celsius_max: 63.1,
      grime_proxy_pre: 0.62, grime_proxy_post: 0.06, moisture_index: 0.28,
      human_clear: true, pressure_prescribed_bar: 5.5, pressure_actual_bar: 5.52,
      verdict: "PASS", solar: false,
      col: 0, row: 1, cs: 2, rs: 1,
    },
    {
      zone_id: "STUCCO-N", label: "North façade — stucco", surface_type: "Stucco",
      pitch_deg: 90, temp_celsius_mean: 31.5, temp_celsius_min: 28.9, temp_celsius_max: 34.2,
      grime_proxy_pre: 0.83, grime_proxy_post: 0.09, moisture_index: 0.61,
      human_clear: true, pressure_prescribed_bar: 4.0, pressure_actual_bar: 3.97,
      verdict: "PASS", solar: false,
      col: 2, row: 0, cs: 1, rs: 2,
    },
  ],
  soiling_rates: [
    { zone_id: "SOL-ROOF",  weeks_to_threshold: 8.2,  confidence: 0.78 },
    { zone_id: "STUCCO-N",  weeks_to_threshold: 11.4, confidence: 0.65 },
    { zone_id: "RF-S",      weeks_to_threshold: 14.1, confidence: 0.71 },
  ],
};

// ── Thermal colour ramp: 0.0 (clean, cool blue) → 1.0 (dirty, hot red) ──────
const RAMP = [
  [0.00, [13,  71, 161]],
  [0.25, [2,  136, 209]],
  [0.50, [46, 160,  67]],
  [0.65, [251,192,  45]],
  [0.80, [244, 81,  30]],
  [1.00, [183, 28,  28]],
];

function thermalColor(v) {
  const clamped = Math.max(0, Math.min(1, v));
  for (let i = 1; i < RAMP.length; i++) {
    if (clamped <= RAMP[i][0]) {
      const t = (clamped - RAMP[i-1][0]) / (RAMP[i][0] - RAMP[i-1][0]);
      const [r0,g0,b0] = RAMP[i-1][1], [r1,g1,b1] = RAMP[i][1];
      return `rgb(${Math.round(r0+(r1-r0)*t)},${Math.round(g0+(g1-g0)*t)},${Math.round(b0+(b1-b0)*t)})`;
    }
  }
  return "rgb(183,28,28)";
}

function soilingColor(weeks) {
  if (weeks < 8)  return "#c0392b";  // red — due soon
  if (weeks < 12) return "#e67e22";  // orange
  return "#1a9e54";                   // green — plenty of time
}

const CELL = 90; // px per grid unit

export default function TwinViewer() {
  const [mode, setMode]         = useState("pre");   // pre | post
  const [selected, setSelected] = useState(null);
  const twin = DEMO_TWIN;

  const soilingMap = Object.fromEntries(
    twin.soiling_rates.map(s => [s.zone_id, s])
  );

  return (
    <div className="twin-root">
      {/* ── Header ── */}
      <div className="twin-header">
        <div>
          <div className="twin-title">{twin.property_label}</div>
          <div className="muted" style={{ fontSize: 12 }}>{twin.address} · Captured {twin.captured_at.slice(0,10)}</div>
        </div>
        <div className="mode-toggle">
          <button
            className={"mode-btn" + (mode === "pre"  ? " active" : "")}
            onClick={() => setMode("pre")}>Pre-clean</button>
          <button
            className={"mode-btn" + (mode === "post" ? " active" : "")}
            onClick={() => setMode("post")}>Post-clean</button>
        </div>
      </div>

      {/* ── Twin canvas + detail ── */}
      <div className="twin-body">

        {/* 3-D perspective roof plan */}
        <div className="twin-stage-wrap">
          <div className="twin-stage">
            <div className="twin-grid" style={{ position: "relative", width: 3 * CELL, height: 2 * CELL }}>
              {twin.zones.map(z => {
                const value = mode === "pre" ? z.grime_proxy_pre : (z.grime_proxy_post ?? z.grime_proxy_pre);
                const bg    = thermalColor(value);
                const isSelected = selected?.zone_id === z.zone_id;
                return (
                  <div
                    key={z.zone_id}
                    onClick={() => setSelected(isSelected ? null : z)}
                    style={{
                      position: "absolute",
                      left:   z.col * CELL,
                      top:    z.row * CELL,
                      width:  z.cs  * CELL - 4,
                      height: z.rs  * CELL - 4,
                      background: bg,
                      borderRadius: 6,
                      border: isSelected ? "3px solid #fff" : "2px solid rgba(255,255,255,.25)",
                      cursor: "pointer",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "#fff",
                      fontWeight: 700,
                      fontSize: 11,
                      textShadow: "0 1px 3px rgba(0,0,0,.6)",
                      transition: "border .15s",
                      userSelect: "none",
                    }}>
                    <div style={{ fontSize: 9, opacity: .85 }}>{z.zone_id}</div>
                    <div style={{ fontSize: 16, fontVariantNumeric: "tabular-nums" }}>
                      {(value * 100).toFixed(0)}%
                    </div>
                    {z.solar && <div style={{ fontSize: 8, opacity: .8 }}>☀ SOLAR</div>}
                    {!z.human_clear && <div style={{ fontSize: 10 }}>⚠ HUMAN</div>}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Colour scale legend */}
          <div className="twin-legend">
            <div className="legend-bar" />
            <div className="legend-labels">
              <span>Clean</span>
              <span>Dirty</span>
            </div>
            <div className="muted" style={{ fontSize: 10, marginTop: 4 }}>Grime proxy (thermal+RGB)</div>
          </div>
        </div>

        {/* Zone detail panel */}
        {selected ? (
          <ZoneDetail zone={selected} mode={mode} soiling={soilingMap[selected.zone_id]} />
        ) : (
          <div className="twin-hint">
            <span style={{ fontSize: 28 }}>☝</span>
            <div>Tap a zone to inspect</div>
          </div>
        )}
      </div>

      {/* ── Zone summary strip ── */}
      <div className="twin-strip">
        {twin.zones.map(z => {
          const val = mode === "pre" ? z.grime_proxy_pre : (z.grime_proxy_post ?? z.grime_proxy_pre);
          const s = soilingMap[z.zone_id];
          return (
            <div
              key={z.zone_id}
              className={"twin-chip" + (selected?.zone_id === z.zone_id ? " selected" : "")}
              onClick={() => setSelected(selected?.zone_id === z.zone_id ? null : z)}>
              <div className="twin-chip-dot" style={{ background: thermalColor(val) }} />
              <div>
                <div style={{ fontWeight: 700, fontSize: 12 }}>{z.zone_id}</div>
                <div style={{ fontSize: 10, color: "#7a8794" }}>{z.surface_type}</div>
                {s && <div style={{ fontSize: 10, color: soilingColor(s.weeks_to_threshold) }}>
                  ↻ in ~{s.weeks_to_threshold}w
                </div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ZoneDetail({ zone, mode, soiling }) {
  const pre  = zone.grime_proxy_pre;
  const post = zone.grime_proxy_post;
  const val  = mode === "pre" ? pre : (post ?? pre);

  return (
    <div className="twin-detail">
      <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 2 }}>{zone.label}</div>
      <div className="muted" style={{ fontSize: 12, marginBottom: 12 }}>{zone.zone_id} · {zone.surface_type} · {zone.pitch_deg}° pitch</div>

      {/* Thermal bar */}
      <div className="detail-label">Grime proxy — {mode === "pre" ? "pre" : "post"}-clean</div>
      <div className="thermal-bar-wrap">
        <div className="thermal-bar-track">
          <div className="thermal-bar-fill" style={{
            width: `${val * 100}%`,
            background: thermalColor(val),
          }} />
          <div className="thermal-bar-threshold" title="Verification threshold 0.15" />
        </div>
        <span className="thermal-val">{(val * 100).toFixed(0)}%</span>
      </div>
      {pre && post != null && (
        <div style={{ fontSize: 11, color: "#1a9e54", marginBottom: 10 }}>
          ↓ {((pre - post) * 100).toFixed(0)} pts improvement after cleaning
        </div>
      )}

      <TwinMetric label="Surface temp" val={`${zone.temp_celsius_mean.toFixed(1)} °C`} />
      <TwinMetric label="Temp range" val={`${zone.temp_celsius_min}–${zone.temp_celsius_max} °C`} />
      <TwinMetric label="Moisture index" val={(zone.moisture_index * 100).toFixed(0) + "%"} />
      <TwinMetric label="Pressure prescribed" val={zone.pressure_prescribed_bar != null ? `${zone.pressure_prescribed_bar} bar` : "—"} />
      <TwinMetric label="Pressure actual" val={zone.pressure_actual_bar != null ? `${zone.pressure_actual_bar} bar` : "—"} />
      <TwinMetric label="Verdict" val={zone.verdict ?? "—"} accent={zone.verdict === "PASS" ? "green" : zone.verdict === "FAIL" ? "red" : undefined} />
      <TwinMetric label="Human clear" val={zone.human_clear ? "✓ Cleared" : "⚠ NOT CLEARED"} accent={zone.human_clear ? "green" : "red"} />

      {soiling && (
        <div className="soiling-box" style={{ borderColor: soilingColor(soiling.weeks_to_threshold) }}>
          <div className="detail-label">Predicted re-soil</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: soilingColor(soiling.weeks_to_threshold) }}>
            ~{soiling.weeks_to_threshold} weeks
          </div>
          <div className="muted" style={{ fontSize: 11 }}>
            Confidence {(soiling.confidence * 100).toFixed(0)}% · {soiling.based_on_visits ?? 3} visits
          </div>
        </div>
      )}
    </div>
  );
}

const TwinMetric = ({ label, val, accent }) => (
  <div className="twin-metric">
    <span>{label}</span>
    <b style={accent === "green" ? { color: "#1a9e54" } : accent === "red" ? { color: "#c0392b" } : {}}>
      {val}
    </b>
  </div>
);
