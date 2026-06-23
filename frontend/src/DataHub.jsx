import React, { useState } from "react";

// ── All demo data in one place ────────────────────────────────────────────────
const DEMO_DATA = {
  summary: {
    total_jobs: 3,
    total_zones_cleaned: 9,
    avg_first_pass_rate: 0.72,
    data_points_collected: 1847,
    active_properties: 1,
    revenue_ytd: 28400,
    roi_delivered_ytd: 141200,   // customer solar energy recovery value
  },
  zones: [
    {
      zone_id: "SOL-ROOF", label: "Rooftop solar array", surface: "Solar Panel",
      grime_pre: 0.71, grime_post: 0.04, temp_c: 42.3, pressure_p: 1.8, pressure_a: 1.79,
      verdict: "PASS", weeks_to_resoil: 8.2, last_cleaned: "2026-06-20", solar: true,
      history: [0.71, 0.68, 0.74],   // grime proxy at start of each past job
    },
    {
      zone_id: "STUCCO-N", label: "North façade — stucco", surface: "Stucco",
      grime_pre: 0.83, grime_post: 0.09, temp_c: 31.5, pressure_p: 4.0, pressure_a: 3.97,
      verdict: "PASS", weeks_to_resoil: 11.4, last_cleaned: "2026-06-20", solar: false,
      history: [0.83, 0.77, 0.81],
    },
    {
      zone_id: "RF-S", label: "Roof — south slope", surface: "Composite Shingle",
      grime_pre: 0.62, grime_post: 0.06, temp_c: 55.8, pressure_p: 5.5, pressure_a: 5.52,
      verdict: "PASS", weeks_to_resoil: 14.1, last_cleaned: "2026-06-20", solar: false,
      history: [0.62, 0.58, 0.66],
    },
  ],
  job_history: [
    { date: "2026-06-20", job_id: "job_20260620_001", zones: 3, passed: 3, failed: 0, fpr: 0.67, duration_min: 95 },
    { date: "2026-03-12", job_id: "job_20260312_001", zones: 3, passed: 3, failed: 1, fpr: 0.50, duration_min: 118 },
    { date: "2025-12-04", job_id: "job_20251204_001", zones: 3, passed: 3, failed: 0, fpr: 1.00, duration_min: 88 },
  ],
  alerts: [
    { type: "HUMAN_DETECTED", zone: "RF-S",    time: "2026-06-20 09:32", resolved: true,  detail: "Thermal blob detected — operator confirmed clear, resumed." },
    { type: "RE_QUEUE",       zone: "STUCCO-N",time: "2026-06-20 10:14", resolved: true,  detail: "First pass FAIL (residual 0.41). Retried at +0.5 bar → PASS." },
    { type: "HUMAN_DETECTED", zone: "RF-S",    time: "2026-03-12 08:55", resolved: true,  detail: "Thermal blob — maintenance worker confirmed off-zone, resumed." },
    { type: "RE_QUEUE",       zone: "STUCCO-N",time: "2026-03-12 10:02", resolved: true,  detail: "First pass FAIL. Retried → PASS." },
  ],
  telemetry: [
    // { zone, job, prescribed, actual }
    { zone: "SOL-ROOF",  job: "2026-06-20", prescribed: 1.80, actual: 1.79 },
    { zone: "STUCCO-N",  job: "2026-06-20", prescribed: 4.00, actual: 3.97 },
    { zone: "RF-S",      job: "2026-06-20", prescribed: 5.50, actual: 5.52 },
    { zone: "SOL-ROOF",  job: "2026-03-12", prescribed: 1.80, actual: 1.81 },
    { zone: "STUCCO-N",  job: "2026-03-12", prescribed: 4.50, actual: 4.48 },
    { zone: "RF-S",      job: "2026-03-12", prescribed: 5.50, actual: 5.49 },
    { zone: "SOL-ROOF",  job: "2025-12-04", prescribed: 1.80, actual: 1.80 },
    { zone: "STUCCO-N",  job: "2025-12-04", prescribed: 4.00, actual: 3.99 },
    { zone: "RF-S",      job: "2025-12-04", prescribed: 5.50, actual: 5.51 },
  ],
};

const TABS = ["Overview", "Zones", "Jobs", "Pressure", "Alerts"];

export default function DataHub() {
  const [tab, setTab] = useState("Overview");
  const d = DEMO_DATA;

  return (
    <div className="hub-root">
      <div className="hub-header">
        <div className="hub-title">Data Hub</div>
        <div className="muted" style={{ fontSize: 12 }}>Carlsbad Commerce Center · All visits · Live demo data</div>
      </div>

      {/* ── Tab bar ── */}
      <div className="hub-tabs">
        {TABS.map(t => (
          <button
            key={t}
            className={"hub-tab" + (tab === t ? " active" : "")}
            onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>

      <div className="hub-content">
        {tab === "Overview"  && <Overview d={d} />}
        {tab === "Zones"     && <ZonesTab d={d} />}
        {tab === "Jobs"      && <JobsTab d={d} />}
        {tab === "Pressure"  && <PressureTab d={d} />}
        {tab === "Alerts"    && <AlertsTab d={d} />}
      </div>
    </div>
  );
}

// ── Overview ──────────────────────────────────────────────────────────────────
function Overview({ d }) {
  const s = d.summary;
  return (
    <div>
      <div className="stat-grid">
        <StatCard label="Total jobs" val={s.total_jobs} unit="" color="#0b6cc4" />
        <StatCard label="Zones cleaned" val={s.total_zones_cleaned} unit="" color="#0b6cc4" />
        <StatCard label="Avg first-pass rate" val={(s.avg_first_pass_rate*100).toFixed(0)} unit="%" color="#1a9e54" />
        <StatCard label="Data points" val={s.data_points_collected.toLocaleString()} unit="" color="#7a3fc0" />
        <StatCard label="Revenue YTD" val={"$" + s.revenue_ytd.toLocaleString()} unit="" color="#0b6cc4" />
        <StatCard label="Customer ROI delivered" val={"$" + s.roi_delivered_ytd.toLocaleString()} unit="" color="#1a9e54" />
      </div>

      <SectionTitle>First-pass rate trend</SectionTitle>
      <MiniChart
        points={d.job_history.map(j => j.fpr * 100)}
        labels={d.job_history.map(j => j.date.slice(5))}
        color="#0b6cc4"
        unit="%"
        yMax={100}
      />

      <SectionTitle>Predicted re-soil schedule</SectionTitle>
      {d.zones.map(z => (
        <div key={z.zone_id} className="resoil-row">
          <div>
            <div style={{ fontWeight: 700, fontSize: 13 }}>{z.zone_id}</div>
            <div className="muted" style={{ fontSize: 11 }}>{z.surface}</div>
          </div>
          <div className="resoil-bar-wrap">
            <div className="resoil-bar-track">
              <div className="resoil-bar-fill" style={{
                width: `${Math.min(100, (z.weeks_to_resoil / 16) * 100)}%`,
                background: z.weeks_to_resoil < 8 ? "#c0392b" : z.weeks_to_resoil < 12 ? "#e67e22" : "#1a9e54",
              }} />
            </div>
          </div>
          <div style={{
            fontWeight: 700, fontSize: 13, minWidth: 52, textAlign: "right",
            color: z.weeks_to_resoil < 8 ? "#c0392b" : z.weeks_to_resoil < 12 ? "#e67e22" : "#1a9e54",
          }}>~{z.weeks_to_resoil}w</div>
        </div>
      ))}
    </div>
  );
}

// ── Zones ─────────────────────────────────────────────────────────────────────
function ZonesTab({ d }) {
  return (
    <div>
      {d.zones.map(z => (
        <div key={z.zone_id} className="hub-zone-card">
          <div className="hub-zone-header">
            <div>
              <span style={{ fontWeight: 800 }}>{z.zone_id}</span>
              {z.solar && <span className="badge solar">SOLAR</span>}
              <div className="muted" style={{ fontSize: 12 }}>{z.label}</div>
            </div>
            <span className={"badge " + (z.verdict === "PASS" ? "pass" : "fail")}>
              {z.verdict}
            </span>
          </div>

          <SectionTitle>Grime proxy history</SectionTitle>
          <MiniChart
            points={z.history.map(v => v * 100)}
            labels={d.job_history.map(j => j.date.slice(5))}
            color="#e67e22"
            unit="%"
            yMax={100}
          />
          <div className="hub-row"><span>Pre-clean (latest)</span><b>{(z.grime_pre * 100).toFixed(0)}%</b></div>
          <div className="hub-row"><span>Post-clean (latest)</span><b style={{ color: "#1a9e54" }}>{(z.grime_post * 100).toFixed(0)}%</b></div>
          <div className="hub-row"><span>Surface temp</span><b>{z.temp_c} °C</b></div>
          <div className="hub-row"><span>Last cleaned</span><b>{z.last_cleaned}</b></div>
          <div className="hub-row"><span>Predicted re-soil</span>
            <b style={{ color: z.weeks_to_resoil < 8 ? "#c0392b" : z.weeks_to_resoil < 12 ? "#e67e22" : "#1a9e54" }}>
              ~{z.weeks_to_resoil} weeks
            </b>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Jobs ──────────────────────────────────────────────────────────────────────
function JobsTab({ d }) {
  return (
    <div>
      <div className="hub-table-wrap">
        <table className="hub-table">
          <thead>
            <tr>
              <th>Date</th><th>Zones</th><th>Passed</th><th>Failed</th><th>FPR</th><th>Duration</th>
            </tr>
          </thead>
          <tbody>
            {d.job_history.map(j => (
              <tr key={j.job_id}>
                <td>{j.date}</td>
                <td>{j.zones}</td>
                <td style={{ color: "#1a9e54", fontWeight: 700 }}>{j.passed}</td>
                <td style={{ color: j.failed > 0 ? "#c0392b" : "#1a9e54", fontWeight: 700 }}>{j.failed}</td>
                <td>
                  <span style={{ fontWeight: 700, color: j.fpr >= 0.8 ? "#1a9e54" : j.fpr >= 0.5 ? "#e67e22" : "#c0392b" }}>
                    {(j.fpr * 100).toFixed(0)}%
                  </span>
                </td>
                <td>{j.duration_min} min</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="note" style={{ paddingTop: 12 }}>
        FPR = first-pass rate. Lower FPR means more re-queues — drives calibration model to adjust prescriptions.
      </div>
    </div>
  );
}

// ── Pressure telemetry ─────────────────────────────────────────────────────────
function PressureTab({ d }) {
  const byZone = {};
  d.telemetry.forEach(t => {
    if (!byZone[t.zone]) byZone[t.zone] = [];
    byZone[t.zone].push(t);
  });

  return (
    <div>
      <div className="note" style={{ marginBottom: 12 }}>
        Prescribed vs. actual nozzle pressure (PSM telemetry). Deviation &gt; ±0.2 bar triggers a calibration flag.
      </div>
      {Object.entries(byZone).map(([zone, rows]) => (
        <div key={zone} className="hub-zone-card">
          <div style={{ fontWeight: 800, marginBottom: 8 }}>{zone}</div>
          <div className="hub-table-wrap">
            <table className="hub-table">
              <thead>
                <tr><th>Job date</th><th>Prescribed (bar)</th><th>Actual (bar)</th><th>Delta</th></tr>
              </thead>
              <tbody>
                {rows.map((r, i) => {
                  const delta = r.actual - r.prescribed;
                  return (
                    <tr key={i}>
                      <td>{r.job}</td>
                      <td>{r.prescribed.toFixed(2)}</td>
                      <td>{r.actual.toFixed(2)}</td>
                      <td style={{ color: Math.abs(delta) > 0.2 ? "#c0392b" : "#1a9e54", fontWeight: 700 }}>
                        {delta >= 0 ? "+" : ""}{delta.toFixed(2)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Alerts ─────────────────────────────────────────────────────────────────────
function AlertsTab({ d }) {
  return (
    <div>
      {d.alerts.map((a, i) => (
        <div key={i} className={"alert-row " + (a.type === "HUMAN_DETECTED" ? "human" : "requeue")}>
          <div className="alert-icon">
            {a.type === "HUMAN_DETECTED" ? "⚠" : "↻"}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 13 }}>
              {a.type === "HUMAN_DETECTED" ? "Human presence detected" : "Re-queue triggered"}
              <span className="muted" style={{ fontWeight: 400, marginLeft: 8 }}>{a.zone} · {a.time}</span>
            </div>
            <div className="muted" style={{ fontSize: 12, marginTop: 2 }}>{a.detail}</div>
          </div>
          <span className={"badge " + (a.resolved ? "pass" : "fail")}>{a.resolved ? "Resolved" : "Open"}</span>
        </div>
      ))}
    </div>
  );
}

// ── Shared primitives ─────────────────────────────────────────────────────────
function StatCard({ label, val, unit, color }) {
  return (
    <div className="stat-card">
      <div className="stat-val" style={{ color }}>{val}<span className="stat-unit">{unit}</span></div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function SectionTitle({ children }) {
  return <div className="section-title">{children}</div>;
}

function MiniChart({ points, labels, color, unit, yMax = 100 }) {
  const W = 260, H = 72, pad = 8;
  const n = points.length;
  if (n < 2) return null;
  const xs = points.map((_, i) => pad + (i / (n - 1)) * (W - pad * 2));
  const ys = points.map(v => H - pad - ((v / yMax) * (H - pad * 2)));
  const path = xs.map((x, i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)},${ys[i].toFixed(1)}`).join(" ");
  const area = path + ` L${xs[n-1].toFixed(1)},${H} L${xs[0].toFixed(1)},${H} Z`;

  return (
    <div className="mini-chart-wrap">
      <svg width={W} height={H} style={{ overflow: "visible" }}>
        <path d={area} fill={color} fillOpacity={0.12} />
        <path d={path} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" />
        {xs.map((x, i) => (
          <g key={i}>
            <circle cx={x} cy={ys[i]} r={3} fill={color} />
            <text x={x} y={H - 1} textAnchor="middle" fontSize={9} fill="#7a8794">{labels[i]}</text>
            <text x={x} y={ys[i] - 6} textAnchor="middle" fontSize={9} fill={color} fontWeight="700">
              {points[i].toFixed(0)}{unit}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
