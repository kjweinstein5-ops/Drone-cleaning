# CLAUDE.md — PROPWASH

> Project context for Claude Code. Read this fully before writing or modifying code.
> This file is the source of truth for *what we are building and why*. Where it marks
> something **UNVERIFIED** or **OPEN**, do not treat it as settled — surface it, don't silently build on it.

---

## 1. What PROPWASH is

PROPWASH is a software-and-services company (in formation) building an **AI-orchestrated exterior building–cleaning platform**. The core product is not a drone — it's the **intelligence layer** that:

1. **Maps** a property with a sensing drone.
2. **Fuses** the sensor data into a per-surface model (what surface, what condition, where the grime/biofilm is).
3. **Prescribes** how to clean each zone (pressure, chemical mix, dwell, nozzle, standoff, flight path).
4. **Drives execution** on a cleaning drone (a Lucid Bots Sherpa) via the most automated path the hardware legally and contractually allows.
5. **Verifies** the result with a post-clean thermal re-scan and **re-queues** failed zones with adjusted parameters until they pass.

The defensible IP is the closed loop **Sense → Fuse → Plan → Execute → Verify → (re-queue)** and the per-surface prescription + verification models — *not* drone flight control, which the cleaning-drone vendor owns.

**Operator/founder:** Kevin. **Base market:** coastal San Diego (Carlsbad). **Year-1 model:** lean, single crew, residential + light commercial.

---

## 2. The single most important architectural rule

**AI agents never sit inside a flight-stabilization or safety loop.** Three tiers, do not collapse them:

| Tier | Owner | Responsibility | Rate | Determinism |
|------|-------|----------------|------|-------------|
| 0 | Cleaning drone flight controller (vendor) | Flight stabilization | 50–400 Hz | Hard real-time, never touched by us |
| 1 | On-aircraft / safety supervisor | Relative-nav, collision avoidance, geofence, pump/valve safety, abort | 10–30 Hz | Deterministic; can override any agent |
| 2 | PROPWASH orchestrator (our backend) | Zone sequencing, work-order dispatch, telemetry aggregation | ~1 Hz | Soft real-time |
| 3 | Claude agents | Planning, prescription, verification reasoning, learning | seconds | Advisory / supervisory |

If a code change would let a Tier-3 agent write a Tier-0 setpoint or suppress a Tier-1 safety check, **stop and flag it.**

---

## 3. The five agents

All are Claude-powered, run on PROPWASH servers (Tier 3), and emit decisions to a shared log.

1. **Mapping Agent** — ingests sensing-drone imagery, produces a georeferenced surface map.
2. **Predictive (Fusion) Agent** — fuses thermal + RGB (+ photogrammetric structure) into per-zone signatures: surface type, angle, grime/biofilm confidence, moisture.
3. **Supervisor Agent** — prescribes cleaning parameters per zone, sequences zones, generates work orders.
4. **Cleaning Agent** — translates a work order into the execution interface the Sherpa actually supports (see §7). Monitors execution telemetry.
5. **Post-Clean Agent** — triggers the verification re-scan, computes residual, decides PASS / re-queue, and feeds outcomes back to the learning model.

---

## 4. Hardware inventory

| Role | Device | Notes |
|------|--------|-------|
| Sensing / mapping | **Autel EVO II Dual 640T (V3)** | Radiometric thermal 640×512 + RGB. **See §5 sensor caveat.** |
| Cleaning execution | **Lucid Bots Sherpa** | Operator-piloted spray drone. Onboard chemical tank w/ variable mix. Controlled from ground via **SIYI MK15**. Requires **FAA Part 107**. |
| Ground detail (later) | **Lucid Lavo Bot** | Wheeled pressure-washing robot. |
| Ground station | Laptop (i7 / 32 GB) + LTE | Runs orchestrator or connects to cloud. |

---

## 5. ⚠️ CRITICAL SENSOR CAVEAT — resolve before building the fusion model

Earlier planning assumed **multispectral / NIR biofilm detection** (e.g., a Sentera 6X on a Freefly Astro). The current hardware choice is the **Autel EVO II 640T, which is thermal + RGB only — it has no multispectral/NIR bands.**

Consequences the fusion layer must respect:

- You **cannot** claim true multispectral biofilm spectral detection with the Autel alone. With Autel you have: (a) **thermal** → moisture / evaporative-cooling differentials where biofilm tends to live, and (b) **RGB computer vision** → visible staining, streaking, surface classification.
- Biofilm presence is therefore **inferred** from thermal + visible cues, not measured spectrally. Treat "biofilm confidence" as a **proxy score**, and label it as such in the data model.
- **OPEN DECISION:** either (A) accept thermal+RGB inference for Year 1, or (B) add a dedicated multispectral sensor if direct biofilm detection is a real product/IP requirement. Do not write code or patent language that asserts multispectral detection while only the Autel is in the loop.

---

## 6. Data flow (loose-sync — the two drones never talk to each other)

```
Autel survey flight  ──▶ thermal + RGB imagery
        │
        ▼
Photogrammetry (OpenDroneMap / Pix4D / DroneDeploy)  ──▶ structure-from-motion point cloud, surface angles
        │
        ▼
Mapping + Fusion agents  ──▶ per-zone signatures (surface, angle, grime/biofilm proxy, moisture)
        │
        ▼
Supervisor agent  ──▶ per-zone PRESCRIPTION ──▶ WORK ORDER
        │
        ▼
Cleaning agent ──▶ execution interface (see §7) ──▶ Sherpa + operator clean the zone
        │
        ▼
Post-Clean agent ──▶ Autel re-scan ──▶ residual computed
        │
   ┌────┴─────┐
 PASS        FAIL ──▶ adjust params, re-queue zone (loop)
```

The **clean plan is the sync point.** No real-time link between Autel and Sherpa is required.

---

## 7. ⚠️ Lucid integration — three paths, by honesty of dependency

This is the highest-risk assumption in the project. **Verified facts** (from Lucid's public materials): the Sherpa is **operator-piloted from the ground via a SIYI MK15**, commercial use **requires FAA Part 107**, Lucid keeps autonomy **in-house** (they acquired the autonomy company Avianna), and **Lucid Refresh** bundles fleet-management + job-intelligence software. **No public developer control/pump API has been confirmed.**

Build the system so the execution interface is a **swappable adapter** behind one interface. Implement Path A first; do not hard-code assumptions from B/C.

- **Path A — Work-order integration (BUILD THIS FIRST; lowest risk).**
  PROPWASH emits a structured work order; the Sherpa operator (or Lucid's own autonomy) executes it; PROPWASH reads job status and verifies. No control of Lucid hardware. Always legal, always works, vendor-friendly. **OPEN:** confirm with Lucid what Lucid Refresh's API exposes (read job data? push work orders?).

- **Path B — Vendor control API (BEST CASE; UNVERIFIED it exists).**
  If Lucid exposes a pump/pressure or MAVLink endpoint, the Cleaning agent sends pressure/dwell setpoints directly. **Do not assume this exists.** Gate all code behind a capability check + feature flag.

- **Path C — Companion-computer retrofit (LAST RESORT; constrained).**
  A companion computer driving pump/valve/servo on owned hardware. **Only pursue with Lucid's cooperation, on hardware you own, and after warranty + FAA + liability review.** Do **not** build anything whose premise is concealing autonomous operation from the manufacturer or circumventing Part 107 — that is out of scope and not an acceptable design goal. Operator-assist must keep the operator genuinely in command, and any increase in flight automation requires the appropriate FAA pathway/waiver.

**Principle:** PROPWASH integrates *transparently* with the vendor and *within* aviation regulations. Prefer partnership and proper waivers over clever circumvention.

---

## 8. Core data schemas (implement as typed models — Pydantic)

```jsonc
// Zone signature (output of Fusion agent)
{
  "zone_id": "RF-S",
  "label": "Roof — south slope",
  "surface_type": "composite_shingle",   // enum
  "pitch_deg": 38,
  "grime_confidence": 0.92,               // PROXY score (see §5), 0..1
  "moisture_index": 0.7,                  // from thermal, 0..1
  "geometry_ref": "...",                  // polygon / point-cloud region ref
  "source": ["thermal", "rgb", "sfm"]
}

// Prescription (output of Supervisor agent)
{
  "zone_id": "RF-S",
  "pressure_bar": 5.5,
  "chemical": "eco_degreaser",            // enum
  "chemical_mix_ratio": 0.35,             // solution:DI
  "dwell_seconds": 30,
  "nozzle_id": 3,
  "standoff_m": 1.2,
  "coverage_pattern": "sweep_ns",
  "safety_margin_m": 0.15,
  "requeue_on_fail_pressure_delta": 1.2
}

// Work order (Path A — what we hand to Lucid/operator)
{
  "job_id": "job_20260622_001",
  "zone": { /* prescription, flattened */ },
  "verify_thermal_post": true,
  "status": "queued"  // queued|assigned|executing|verifying|done|reflagged
}

// Verification result (output of Post-Clean agent)
{
  "zone_id": "RF-S",
  "residual_confidence": 0.07,
  "threshold": 0.15,
  "verdict": "PASS",                      // PASS|FAIL
  "delta_applied": null,                  // e.g., {"pressure_bar": +1.2} on FAIL
  "execution_vs_prescription": { /* deviation log for learning */ }
}
```

---

## 9. Surface treatment matrix — STARTING ASSUMPTIONS, calibrate from real jobs

These are **initial defaults to be tuned**, not validated constants. Store them as data (a versioned table), never hard-coded in logic. Over-pressure destroys surfaces — keep conservative defaults and let verification + field data raise them.

| Surface | Pressure (bar) | Chemical | Dwell (s) | Nozzle |
|---|---|---|---|---|
| Composite shingle | 5.0–6.5 | eco/standard degreaser | 30–40 | 40° fan, 0.5 mm |
| Clay/concrete tile | 4.5–6.0 | standard | 30–40 | 40° fan |
| Solar panel (tempered glass) | 1.5–2.0 | **DI water only** (no detergent) | 18–22 | 25° narrow, 0.35 mm |
| Window glass | 2.0–2.4 | ammonia-free | 15–20 | 20° jet |
| Stucco | 3.5–4.5 | standard degreaser | 25–35 | 40° fan, 0.6 mm |
| Gutter (aluminum) | 6.0–7.0 | degreaser + solvent | 35–45 | 45° fan, 0.7 mm |

Solar = lowest pressure + DI only (detergent residue cuts panel output; high pressure cracks cells). This is the most failure-sensitive surface — enforce a hard pressure ceiling for it in the safety layer.

---

## 10. Operator model (Year-1 reality)

Operator stays **in command** (Part 107). PROPWASH minimizes the *skill* required, not the *authority*:

- Pre-job: receives a job packet (zones, addresses, est. time), confirms ready.
- Per-zone: app says which nozzle to fit + when to begin; operator confirms; executes the prescribed clean while monitoring video + thermal overlay; can override at any time.
- Post-zone: app shows PASS / retry-with-new-params.

Target: a trained-but-non-expert operator after short training. **Do not** design a flow that hides automation from the operator or the regulator.

---

## 11. IP & trademark strategy (founder intent — not legal advice; engage an attorney/agent)

- **Trade secret (kept in-house, never published):** fusion/grime-scoring model, the calibrated surface/pressure table built from customer data, the learning model that adjusts prescriptions from execution-vs-result deltas, verification threshold tuning.
- **Provisional patent** on the *method* (sense→fuse→prescribe→execute→verify→re-queue, incl. verification-driven parameter adjustment). Provisional is low-cost and gives ~12 months + "patent pending"; **verify current USPTO fees** and use an attorney for claims. A provisional is a priority placeholder, **not** enforceable protection by itself.
- **Utility patent** conversion once the method is proven in the field.
- **Trademark** the brand **PROPWASH** (you trademark brand identifiers, *not* "the idea"). Likely classes: software/SaaS (42), cleaning/maintenance services (37), possibly goods (e.g., 7/9/12) depending on what you sell. Confirm classes with counsel.
- **Copyright** registers automatically on the codebase; formal registration strengthens enforcement.

Do not write patent/marketing copy that claims capabilities the shipped system doesn't have (esp. multispectral detection per §5, or "fully autonomous" per §7).

---

## 12. Recommended tech stack

- **Backend:** Python 3.11+, **FastAPI** (async, WebSocket telemetry), **Pydantic** models.
- **Data:** **PostgreSQL** (properties, zones, jobs, prescriptions, verification, audit log) + **PostGIS** for geometry. **Redis** for live state / job queue.
- **Imagery/geo:** OpenDroneMap (or Pix4D/DroneDeploy) for SfM; store orthomosaics in object storage (S3 or equivalent).
- **Agents:** Anthropic API; agents are stateless services that read/write the DB + queue. Keep prompts and tool schemas versioned in-repo.
- **Frontend:** **React** operator/ops dashboard (the existing PROPWASH dashboard). WebSocket for live telemetry.
- **Execution adapter:** one `ExecutionTransport` interface with implementations `WorkOrderTransport` (Path A), `VendorApiTransport` (Path B, flagged off), `CompanionTransport` (Path C, flagged off).

---

## 13. Suggested repo layout

```
propwash/
  backend/
    app/                 # FastAPI app, routers, websockets
    models/              # Pydantic + DB models (zone, prescription, workorder, verify)
    agents/              # mapping, fusion, supervisor, cleaning, postclean (+ prompts/)
    fusion/              # thermal+rgb+sfm pipeline
    execution/           # ExecutionTransport interface + adapters (A/B/C)
    safety/              # deterministic checks (pressure ceilings, geofence rules)
    db/                  # migrations, PostGIS
  frontend/              # React dashboard
  prescriptions/         # versioned surface/pressure tables (data, not code)
  sim/                   # mock transport + telemetry simulator for dev w/o hardware
  docs/                  # this file, schemas, Lucid integration questions
```

---

## 14. Build roadmap

1. **Schemas + DB** (§8) and the **surface table as data** (§9).
2. **Simulator** (`sim/`) — mock execution + telemetry so the full loop runs with no hardware. (A working React simulation of this loop already exists; mirror its state machine.)
3. **Fusion pipeline** (thermal+RGB+SfM) → zone signatures, with the §5 caveat encoded.
4. **Supervisor** prescription + **work-order (Path A)** dispatch.
5. **Post-Clean** verification + re-queue loop.
6. **Dashboard** wired to live WebSocket telemetry.
7. Only after Lucid answers §7: implement Path B/C behind flags.

---

## 15. ⚠️ DO-NOT-ASSUME / OPEN QUESTIONS (read before building)

1. **Lucid exposes no confirmed control or pump API.** Path A only until confirmed. (§7)
2. **Autel = thermal + RGB, NOT multispectral.** "Biofilm" is a proxy score. (§5)
3. **Surface/pressure numbers are unvalidated defaults.** Calibrate from field data; enforce ceilings (esp. solar). (§9)
4. **No covert automation / no circumventing Part 107.** Operator stays in command; more flight automation needs an FAA pathway. (§7, §10)
5. **Financial targets (jobs/week, margins, revenue) are goals to validate, not facts.** Don't encode them as business logic.
6. **Provisional patent ≠ protection; you can't trademark an idea.** Keep claims honest and consult counsel. (§11)
7. **The safety layer is deterministic and authoritative.** Agents advise; they never override safety. (§2)

When in doubt, implement the conservative path and leave a `# TODO(PROPWASH): needs Kevin/Lucid/attorney decision` marker rather than guessing.
