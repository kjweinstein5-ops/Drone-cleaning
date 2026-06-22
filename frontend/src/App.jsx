import React, { useState, useEffect, useRef } from "react";

// PROPWASH operator app — per-zone clean execution + verification.
// Operator stays in command at all times (FAA Part 107, CLAUDE.md §10).
// Falls back to a built-in demo job packet when the backend isn't reachable,
// so the app runs standalone for training/dev.

const DEMO_JOB = {
  property: "Carlsbad Commerce Center — Bldg C",
  address: "2200 Faraday Ave, Carlsbad, CA",
  estMinutes: 95,
  zones: [
    { id: "SOL-ROOF", label: "Rooftop solar array", surface: "solar_panel",
      nozzle: "#4 — 25° narrow, 0.35mm", chemical: "DI water only (no detergent)",
      pressure: "1.8 bar", standoff: "0.8 m", dwell: 8, pattern: "E–W sweep", solar: true, willFail: false },
    { id: "STUCCO-N", label: "North façade — stucco", surface: "stucco",
      nozzle: "#3 — 40° fan, 0.6mm", chemical: "Standard degreaser (30%)",
      pressure: "4.0 bar", standoff: "1.0 m", dwell: 6, pattern: "N–S sweep", solar: false, willFail: true },
    { id: "RF-S", label: "Roof — south slope", surface: "composite_shingle",
      nozzle: "#2 — 40° fan, 0.5mm", chemical: "Eco degreaser (35%)",
      pressure: "5.5 bar", standoff: "1.2 m", dwell: 7, pattern: "N–S sweep", solar: false, willFail: false },
  ],
};

function ZoneCard({ zone, onConfirm }) {
  return (
    <div className="card">
      <h1>{zone.label}</h1>
      <div className="muted">{zone.id} · {zone.surface}</div>
      <div className={"safety " + (zone.solar ? "solar" : "std")}>
        {zone.solar
          ? "⚠ SOLAR — DI water only, hard pressure ceiling 2.0 bar. Detergent forbidden."
          : "Standard surface — stay within prescribed pressure."}
      </div>
      <ol className="checklist">
        <Step n={1} label="Fit nozzle" val={zone.nozzle} />
        <Step n={2} label="Load chemical" val={zone.chemical} />
        <Step n={3} label="Pressure" val={zone.pressure} />
        <Step n={4} label="Standoff distance" val={zone.standoff} />
        <Step n={5} label="Coverage pattern" val={zone.pattern} />
      </ol>
      <button className="btn primary" onClick={onConfirm}>Confirm ready &amp; begin</button>
      <p className="note">You remain in command. Abort the moment anything looks wrong.</p>
    </div>
  );
}

function Step({ n, label, val }) {
  return (
    <li>
      <span className="num">{n}</span>
      <div><div className="step-label">{label}</div><div className="step-val">{val}</div></div>
    </li>
  );
}

function Executing({ zone, onDone, onAbort }) {
  const [left, setLeft] = useState(zone.dwell);
  useEffect(() => {
    if (left <= 0) { onDone(); return; }
    const t = setTimeout(() => setLeft(left - 1), 1000);
    return () => clearTimeout(t);
  }, [left]);
  return (
    <div className="card">
      <h1>Cleaning · {zone.id}</h1>
      <div className="muted">Executing prescribed clean — monitor the overlay</div>
      <div className="overlay">live thermal + video overlay</div>
      <div className="dwell"><div className="big">{left}s</div><div className="muted">dwell remaining</div></div>
      <button className="btn abort" onClick={onAbort}>■ Abort / Override</button>
    </div>
  );
}

function Verifying({ onResult }) {
  useEffect(() => { const t = setTimeout(onResult, 1800); return () => clearTimeout(t); }, []);
  return (
    <div className="card">
      <h1>Verifying…</h1>
      <div className="muted">Post-clean thermal re-scan in progress</div>
      <div className="overlay">re-scanning zone</div>
    </div>
  );
}

function Verdict({ zone, pass, isLast, onNext, onRetry }) {
  return (
    <div className="card">
      <div className={"verdict " + (pass ? "pass" : "fail")}>
        <div className="icon">{pass ? "✓" : "↻"}</div>
        <h1>{pass ? "VERIFIED CLEAN" : "RE-QUEUE — retry with more pressure"}</h1>
        <div className="muted">{zone.id}</div>
      </div>
      <Metric label="Residual (proxy)" val={pass ? "0.06" : "0.41"} />
      <Metric label="Threshold" val="0.15" />
      {!pass && <Metric label="Adjustment" val="pressure +0.5 bar" />}
      {pass
        ? <button className="btn go" onClick={onNext}>{isLast ? "Finish job" : "Next zone →"}</button>
        : <button className="btn primary" onClick={onRetry}>Retry zone with new params</button>}
    </div>
  );
}

const Metric = ({ label, val }) => (
  <div className="metric"><span>{label}</span><b>{val}</b></div>
);

export default function App() {
  // Backend wiring point: swap DEMO_JOB for listJobs()/getJob() from ./api.js.
  const job = DEMO_JOB;
  const zones = job.zones;
  const [idx, setIdx] = useState(0);
  const [phase, setPhase] = useState("brief");
  const [statuses, setStatuses] = useState(zones.map(() => ""));
  const [pass, setPass] = useState(true);
  const retried = useRef({});

  const setStatus = (i, s) => setStatuses((p) => p.map((x, j) => (j === i ? s : x)));
  const zone = zones[idx];

  const onConfirm = () => { setStatus(idx, "active"); setPhase("exec"); };
  const onAbort = () => { setStatus(idx, ""); setPhase("brief"); };
  const onResult = () => { const f = zone.willFail && !retried.current[zone.id]; setPass(!f); setPhase("verdict"); };
  const onNext = () => {
    setStatus(idx, "done");
    if (idx + 1 >= zones.length) setPhase("done");
    else { setIdx(idx + 1); setPhase("brief"); }
  };
  const onRetry = () => { retried.current[zone.id] = true; setStatus(idx, "fail"); setPhase("exec"); };

  return (
    <div className="app">
      <div className="topbar">
        <span className="brand">PROPWASH</span>
        <span className="pilot">Pilot: K. Weinstein · Part 107 ✓</span>
      </div>
      <div className="job">
        <h2>{job.property}</h2>
        <div className="muted">{job.address}</div>
        <div className="muted">{zones.length} zones · est. {job.estMinutes} min</div>
        <div className="zones">
          {zones.map((z, i) => <span key={z.id} className={"chip " + (statuses[i] || "")}>{z.id}</span>)}
        </div>
      </div>
      <div className="pad">
        {phase === "brief" && <ZoneCard zone={zone} onConfirm={onConfirm} />}
        {phase === "exec" && <Executing zone={zone} onDone={() => setPhase("verify")} onAbort={onAbort} />}
        {phase === "verify" && <Verifying onResult={onResult} />}
        {phase === "verdict" && <Verdict zone={zone} pass={pass} isLast={idx + 1 >= zones.length} onNext={onNext} onRetry={onRetry} />}
        {phase === "done" && (
          <div className="card">
            <div className="verdict pass"><div className="icon">✓</div><h1>Job complete</h1></div>
            <div className="muted" style={{ textAlign: "center" }}>All zones verified clean. ROI report generating for the customer.</div>
          </div>
        )}
      </div>
      <p className="note center">Demo data. Operator stays in command (FAA Part 107).</p>
    </div>
  );
}
