# PROPWASH — complete project documentation

> AI-orchestrated exterior building cleaning · Carlsbad, CA
> Generated 2026-09-05 from the `Drone-cleaning` repository.
>
> **This file is generated.** Edit the source files listed under each section and re-run
> `python tools_bundle.py`; edits made here are lost on the next build.

**Read this first:** every price is public list and subject to quote — nothing here is a bid.
Pressure, dwell and chemical figures are **uncalibrated starting assumptions**, not validated
constants. Items marked ⚠️ **UNVERIFIED** or **OPEN** are exactly that. Nothing in this document
is legal, aviation-regulatory, insurance or financial advice.

---

## Contents

### PROJECT CONTEXT

- [CLAUDE.md — PROPWASH](#claude) · `CLAUDE.md`

### STRATEGY — is this worth doing

- [Is this worth pursuing? — a deliberately skeptical read](#docsgonogo) · `docs/GO_NO_GO.md`
- [Competitive Landscape — California & the Southwest](#docscompetitivelandscape) · `docs/COMPETITIVE_LANDSCAPE.md`
- [PROPWASH — Path to $10M/year](#docsbusinessplan) · `docs/BUSINESS_PLAN.md`
- [PROPWASH — Full Report: What It Takes for YOUR OWN Company to Reach $10M / Year](#docsscalingto10m) · `docs/SCALING_TO_10M.md`
- [Brand Naming — Exploration Shortlist](#docsbrandnaming) · `docs/BRAND_NAMING.md`

### HARDWARE — what to buy

- [Payload Build Spec — the complete wash kit](#docsdecisionspayloadbuildspec) · `docs/decisions/PAYLOAD_BUILD_SPEC.md`
- [⭐ VERDICT — the two aircraft, the system, and what it costs](#docsdecisionsverdictandprices) · `docs/decisions/VERDICT_AND_PRICES.md`
- [Fleet Architecture — every aircraft and system, for all needs](#docsdecisionsfleetarchitecture) · `docs/decisions/FLEET_ARCHITECTURE.md`
- [Decision — which drone company, and how our stack gets inside it](#docsdecisionsplatformvendorchoice) · `docs/decisions/PLATFORM_VENDOR_CHOICE.md`
- [Decision — an airframe we can actually integrate into (non-Lucid)](#docsdecisionsintegrableplatform) · `docs/decisions/INTEGRABLE_PLATFORM.md`
- [Airframe contenders — the full screened field](#docsdecisionsairframecontenders) · `docs/decisions/AIRFRAME_CONTENDERS.md`
- [Deep dive — every purpose-built cleaning drone, and why none of them fit](#docsdecisionspurposebuiltscan) · `docs/decisions/PURPOSE_BUILT_SCAN.md`
- [Decision Note — Cleaning Drone Platform](#docsdecisionscleaningdroneplatform) · `docs/decisions/CLEANING_DRONE_PLATFORM.md`
- [Decision Note — Open-Platform Integration (the "openness spectrum")](#docsdecisionsopenplatformintegration) · `docs/decisions/OPEN_PLATFORM_INTEGRATION.md`
- [Decision Note — All-DJI Two-Drone Architecture](#docsdecisionsdjitwodronearchitecture) · `docs/decisions/DJI_TWO_DRONE_ARCHITECTURE.md`
- [Decision Note — Sensor Platform Shortlist](#docsdecisionssensorplatformshortlist) · `docs/decisions/SENSOR_PLATFORM_SHORTLIST.md`
- [Decision Note — Spectral Sensing for Mold / Dirt / Biofilm Analysis](#docsdecisionsspectralsensingdecision) · `docs/decisions/SPECTRAL_SENSING_DECISION.md`
- [DEFINITIVE — the drone, the add-ons, and why](#docsdecisionsbuildspec) · `docs/decisions/BUILD_SPEC.md`
- [Cleaning methods beyond spraying — and what "Raptor" actually is](#docsdecisionscleaningmethods) · `docs/decisions/CLEANING_METHODS.md`
- [Decision Note — Compute Infrastructure (Hybrid Local + Cloud)](#docsdecisionscomputeinfrastructure) · `docs/decisions/COMPUTE_INFRASTRUCTURE.md`

### TECHNICAL — how the loop works

- [PROPWASH — 3D Data Pipeline Deep Dive](#docs3ddatapipeline) · `docs/3D_DATA_PIPELINE.md`
- [Deep Dive — Layering Thermal onto the 3D Model (precisely)](#docsthermallayeringpipeline) · `docs/THERMAL_LAYERING_PIPELINE.md`
- [PROPWASH — Thermographic Digital Twin + Human Presence Detection](#docsthermographicdigitaltwin) · `docs/THERMOGRAPHIC_DIGITAL_TWIN.md`
- [PROPWASH — Dynamic Pressure Control Hardware](#docsdynamicpressurehardware) · `docs/DYNAMIC_PRESSURE_HARDWARE.md`
- [Deep Dive — Flight Software Stack (ROS 2 / PX4 / MAVLink / Auterion / Jetson)](#docsflightsoftwarestack) · `docs/FLIGHT_SOFTWARE_STACK.md`
- [Deep Dive — Communication Architecture & the Autonomy Ladder](#docscommunicationandautonomy) · `docs/COMMUNICATION_AND_AUTONOMY.md`

### OPERATIONS & REGULATORY

- [PROPWASH — Field Operations, End to End](#docsfieldoperations) · `docs/FIELD_OPERATIONS.md`
- [PROPWASH — Launch Playbook](#docslaunchplaybook) · `docs/LAUNCH_PLAYBOOK.md`
- [Regulatory Strategy — How to Get Maximum Autonomy, Legitimately](#docsregulatorystrategy) · `docs/REGULATORY_STRATEGY.md`
- [FAA Waiver Package — 14 CFR 107.35 (Multiple sUAS, One RPIC)](#docswaiver10735) · `docs/WAIVER_107_35.md`

### BUSINESS — IP and vendors

- [PROPWASH — How to Protect Your IP (so it can't be copied)](#docsipprotection) · `docs/IP_PROTECTION.md`
- [Vendor Outreach — draft letters](#docsvendoroutreach) · `docs/VENDOR_OUTREACH.md`
- [Lucid Bots — partnership outreach & questions](#docslucidoutreach) · `docs/LUCID_OUTREACH.md`

### DATA
- [Surface treatment table](#surfacetable) · `prescriptions/surface_treatment_v1.json`


<a id="claude"></a>

---

# CLAUDE.md — PROPWASH

> **Source file:** `CLAUDE.md`

## CLAUDE.md — PROPWASH

> Project context for Claude Code. Read this fully before writing or modifying code.
> This file is the source of truth for *what we are building and why*. Where it marks
> something **UNVERIFIED** or **OPEN**, do not treat it as settled — surface it, don't silently build on it.

---

### 1. What PROPWASH is

PROPWASH is a software-and-services company (in formation) building an **AI-orchestrated exterior building–cleaning platform**. The core product is not a drone — it's the **intelligence layer** that:

1. **Maps** a property with a sensing drone.
2. **Fuses** the sensor data into a per-surface model (what surface, what condition, where the grime/biofilm is).
3. **Prescribes** how to clean each zone (pressure, chemical mix, dwell, nozzle, standoff, flight path).
4. **Drives execution** on a cleaning drone (a Lucid Bots Sherpa) via the most automated path the hardware legally and contractually allows.
5. **Verifies** the result with a post-clean thermal re-scan and **re-queues** failed zones with adjusted parameters until they pass.

The defensible IP is the closed loop **Sense → Fuse → Plan → Execute → Verify → (re-queue)** and the per-surface prescription + verification models — *not* drone flight control, which the cleaning-drone vendor owns.

**Operator/founder:** Kevin. **Base market:** coastal San Diego (Carlsbad). **Year-1 model:** lean, single crew, residential + light commercial.

---

### 2. The single most important architectural rule

**AI agents never sit inside a flight-stabilization or safety loop.** Three tiers, do not collapse them:

| Tier | Owner | Responsibility | Rate | Determinism |
|------|-------|----------------|------|-------------|
| 0 | Cleaning drone flight controller (vendor) | Flight stabilization | 50–400 Hz | Hard real-time, never touched by us |
| 1 | On-aircraft / safety supervisor | Relative-nav, collision avoidance, geofence, pump/valve safety, abort | 10–30 Hz | Deterministic; can override any agent |
| 2 | PROPWASH orchestrator (our backend) | Zone sequencing, work-order dispatch, telemetry aggregation | ~1 Hz | Soft real-time |
| 3 | Claude agents | Planning, prescription, verification reasoning, learning | seconds | Advisory / supervisory |

If a code change would let a Tier-3 agent write a Tier-0 setpoint or suppress a Tier-1 safety check, **stop and flag it.**

---

### 3. The five agents

All are Claude-powered, run on PROPWASH servers (Tier 3), and emit decisions to a shared log.

1. **Mapping Agent** — ingests sensing-drone imagery, produces a georeferenced surface map.
2. **Predictive (Fusion) Agent** — fuses thermal + RGB (+ photogrammetric structure) into per-zone signatures: surface type, angle, grime/biofilm confidence, moisture.
3. **Supervisor Agent** — prescribes cleaning parameters per zone, sequences zones, generates work orders.
4. **Cleaning Agent** — translates a work order into the execution interface the Sherpa actually supports (see §7). Monitors execution telemetry.
5. **Post-Clean Agent** — triggers the verification re-scan, computes residual, decides PASS / re-queue, and feeds outcomes back to the learning model.

---

### 4. Hardware inventory

| Role | Device | Notes |
|------|--------|-------|
| Sensing / mapping | ⚠️ **SUPERSEDED — see `docs/decisions/FLEET_ARCHITECTURE.md`** | The Autel line is on the **FCC Covered List** (Dec 2025): no new US import. Recommended replacement is the **Skydio X10D** (Blue UAS cleared, FLIR Boson+ radiometric thermal + optical on one gimbal). |
| Cleaning execution | **Lucid Bots Sherpa** | Operator-piloted spray drone. Onboard chemical tank w/ variable mix. Controlled from ground via **SIYI MK15**. Requires **FAA Part 107**. |
| Ground detail (later) | **Lucid Lavo Bot** | Wheeled pressure-washing robot. |
| Ground station | Laptop (i7 / 32 GB) + LTE | Runs orchestrator or connects to cloud. |

---

### 5. ⚠️ CRITICAL SENSOR CAVEAT — resolve before building the fusion model

Earlier planning assumed **multispectral / NIR biofilm detection** (e.g., a Sentera 6X on a Freefly Astro). The current hardware choice is the **Autel EVO II 640T, which is thermal + RGB only — it has no multispectral/NIR bands.**

Consequences the fusion layer must respect:

- You **cannot** claim true multispectral biofilm spectral detection with the Autel alone. With Autel you have: (a) **thermal** → moisture / evaporative-cooling differentials where biofilm tends to live, and (b) **RGB computer vision** → visible staining, streaking, surface classification.
- Biofilm presence is therefore **inferred** from thermal + visible cues, not measured spectrally. Treat "biofilm confidence" as a **proxy score**, and label it as such in the data model.
- **OPEN DECISION:** either (A) accept thermal+RGB inference for Year 1, or (B) add a dedicated multispectral sensor if direct biofilm detection is a real product/IP requirement. Do not write code or patent language that asserts multispectral detection while only the Autel is in the loop.

---

### 6. Data flow (loose-sync — the two drones never talk to each other)

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

### 7. ⚠️ Lucid integration — three paths, by honesty of dependency

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

### 8. Core data schemas (implement as typed models — Pydantic)

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

### 9. Surface treatment matrix — STARTING ASSUMPTIONS, calibrate from real jobs

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

### 10. Operator model (Year-1 reality)

Operator stays **in command** (Part 107). PROPWASH minimizes the *skill* required, not the *authority*:

- Pre-job: receives a job packet (zones, addresses, est. time), confirms ready.
- Per-zone: app says which nozzle to fit + when to begin; operator confirms; executes the prescribed clean while monitoring video + thermal overlay; can override at any time.
- Post-zone: app shows PASS / retry-with-new-params.

Target: a trained-but-non-expert operator after short training. **Do not** design a flow that hides automation from the operator or the regulator.

---

### 11. IP & trademark strategy (founder intent — not legal advice; engage an attorney/agent)

- **Trade secret (kept in-house, never published):** fusion/grime-scoring model, the calibrated surface/pressure table built from customer data, the learning model that adjusts prescriptions from execution-vs-result deltas, verification threshold tuning.
- **Provisional patent** on the *method* (sense→fuse→prescribe→execute→verify→re-queue, incl. verification-driven parameter adjustment). Provisional is low-cost and gives ~12 months + "patent pending"; **verify current USPTO fees** and use an attorney for claims. A provisional is a priority placeholder, **not** enforceable protection by itself.
- **Utility patent** conversion once the method is proven in the field.
- **Trademark** the brand **PROPWASH** (you trademark brand identifiers, *not* "the idea"). Likely classes: software/SaaS (42), cleaning/maintenance services (37), possibly goods (e.g., 7/9/12) depending on what you sell. Confirm classes with counsel.
- **Copyright** registers automatically on the codebase; formal registration strengthens enforcement.

Do not write patent/marketing copy that claims capabilities the shipped system doesn't have (esp. multispectral detection per §5, or "fully autonomous" per §7).

---

### 12. Recommended tech stack

- **Backend:** Python 3.11+, **FastAPI** (async, WebSocket telemetry), **Pydantic** models.
- **Data:** **PostgreSQL** (properties, zones, jobs, prescriptions, verification, audit log) + **PostGIS** for geometry. **Redis** for live state / job queue.
- **Imagery/geo:** OpenDroneMap (or Pix4D/DroneDeploy) for SfM; store orthomosaics in object storage (S3 or equivalent).
- **Agents:** Anthropic API; agents are stateless services that read/write the DB + queue. Keep prompts and tool schemas versioned in-repo.
- **Frontend:** **React** operator/ops dashboard (the existing PROPWASH dashboard). WebSocket for live telemetry.
- **Execution adapter:** one `ExecutionTransport` interface with implementations `WorkOrderTransport` (Path A), `VendorApiTransport` (Path B, flagged off), `CompanionTransport` (Path C, flagged off).

---

### 13. Suggested repo layout

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

### 14. Build roadmap

1. **Schemas + DB** (§8) and the **surface table as data** (§9).
2. **Simulator** (`sim/`) — mock execution + telemetry so the full loop runs with no hardware. (A working React simulation of this loop already exists; mirror its state machine.)
3. **Fusion pipeline** (thermal+RGB+SfM) → zone signatures, with the §5 caveat encoded.
4. **Supervisor** prescription + **work-order (Path A)** dispatch.
5. **Post-Clean** verification + re-queue loop.
6. **Dashboard** wired to live WebSocket telemetry.
7. Only after Lucid answers §7: implement Path B/C behind flags.

---

### 15. ⚠️ DO-NOT-ASSUME / OPEN QUESTIONS (read before building)

1. **Lucid exposes no confirmed control or pump API.** Path A only until confirmed. (§7)
2. **Autel = thermal + RGB, NOT multispectral.** "Biofilm" is a proxy score. (§5)
3. **Surface/pressure numbers are unvalidated defaults.** Calibrate from field data; enforce ceilings (esp. solar). (§9)
4. **No covert automation / no circumventing Part 107.** Operator stays in command; more flight automation needs an FAA pathway. (§7, §10)
5. **Financial targets (jobs/week, margins, revenue) are goals to validate, not facts.** Don't encode them as business logic.
6. **Provisional patent ≠ protection; you can't trademark an idea.** Keep claims honest and consult counsel. (§11)
7. **The safety layer is deterministic and authoritative.** Agents advise; they never override safety. (§2)

When in doubt, implement the conservative path and leave a `# TODO(PROPWASH): needs Kevin/Lucid/attorney decision` marker rather than guessing.

<a id="docsgonogo"></a>

---

# Is this worth pursuing? — a deliberately skeptical read

> **Source file:** `docs/GO_NO_GO.md`

## Is this worth pursuing? — a deliberately skeptical read

> Kevin's question: *is this space too crowded, and is it worth pursuing further even with tech
> they don't have?*
>
> This document argues the **against** case as hard as it can, then says what survives.
> Companion to `COMPETITIVE_LANDSCAPE.md` (who is out there) — **this one is the verdict.**
>
> All figures are cited, dated **2026-08-16**, and come from vendor/press sources, which are
> promotional. Treat them as the optimistic end.

---

### The one-paragraph answer

**The market is not too crowded. But the plan as written points at the weakest intersection of
every axis it could have chosen** — coastal geography where solar cleaning barely pays,
residential scale where jobs are worth hundreds instead of $14,000, and a "we detect dirt" claim
that shipped in commercial PV software years ago. Same technology, repointed at **inland/desert
commercial and solar assets**, is a materially better business. And one number in our own model
is **4.8× too optimistic** and needs fixing before any funding conversation.

**Verdict: pursue — but re-aim, and prove the intelligence sells before buying a spray drone.**

---

### Part 1 — The case AGAINST (taken seriously)

#### 1.1 The solar wedge is weakest exactly where we're based ⚠️

| Geography | Annual soiling loss | Cleanings/yr justified |
|---|---|---|
| **Coastal SoCal** (Santa Monica, Long Beach — **and Carlsbad**) | **2–8%** | **~1** — rain rinses |
| Inland / desert SoCal | **5–25%** | 2+ |
| Desert, remote | up to **30%+** | continuous programmes |

At SCE's ~34.5¢/kWh, recovering 10% of a 12,000 kWh/yr system is ~$414/yr against ~$400 for two
cleanings — *near-breakeven inland*. **On the coast, with lighter soiling and free rain rinsing,
the arithmetic is worse.**

**CLAUDE.md §1 names coastal Carlsbad as the base market and solar as the wedge. Those two
choices fight each other.** Carlsbad is a fine place to *live*; it is close to the worst place in
Southern California to sell solar cleaning on ROI.

#### 1.2 The market grows slowly

Solar panel cleaning: **$1.22B (2025), 3.5% CAGR** to 2035. That is a mature service market, not
a hypergrowth one. Nothing wrong with it — but nobody should pitch this as a rocket ship, and a
$10M target is ~0.8% of the *entire global* solar-cleaning market. Exterior building cleaning
overall is much larger, which is an argument for **not** over-indexing on solar.

#### 1.3 The SaaS-to-operators play is weaker than I said last turn ❌

**I recommended licensing to Lucid's 400+ operators. I have to walk that back.**

**Lucid Refresh** is already a **subscription that bundles**: Sherpa drone + **Lavo AI autonomous
pressure-washing robot** + **Lucid Command fleet-management software** + **"job intelligence"** +
training + equipment loaner guarantee. One price, one vendor.

So selling software into that base means competing with a bundle, through the relationship of
the company that owns the hardware, the channel and the customer. That is a hard motion, and I
under-weighted it.

Worse for the long game: Lucid **just raised $20M explicitly to build "America's leading exterior
cleaning platform,"** keeps autonomy in-house (they acquired Avianna), and has now shipped an
**autonomous** ground robot. **The capability gap closes from their side, funded, while we
write Python.**

#### 1.4 "We see the dirt" is already commoditised ❌

Sitemark, MapperX, Anvil Labs, Inspekt AI and Folio3 already ship automatic classification of
thermal *and visual* anomalies **including soiling**, with pixel-precise measurement and
historical digital twins. In utility solar, **SolarVision AI-class systems already dispatch
cleaning automatically** when SCADA performance data flags underperforming strings — that is a
closed loop, in production, today.

Any patent or marketing built on soiling detection is weak. (`IP_PROTECTION.md` and CLAUDE.md §11
should both be read against this.)

#### 1.5 Operator pain is sales, not pressure settings

An operator running 10+ jobs/year averages **$200K revenue** with a payback under two months.
Their constraint is **finding the next commercial contract**, not deciding whether stucco takes
4.0 or 4.5 bar. Software that optimises the thing that isn't the bottleneck doesn't get bought.

#### 1.6 The base market already has our exact thesis, taken

**DronePower1 markets Carlsbad specifically**, on the *high-solar-adoption-on-Spanish-tile-roofs*
argument. That is our wedge, our city, our roof type — already someone's homepage.

#### 1.7 ⚠️ Our own revenue model is 4.8× optimistic

This is the most uncomfortable finding in the document.

| | Per crew / operator per year |
|---|---|
| `reports/revenue_model.py`, premium route | **$960,000** |
| Observed: Lucid operator running 10+ jobs/yr | **$200,000** |

| Crews needed for $10M | |
|---|---|
| Our model (premium, 1 aircraft) | **7** |
| At observed $200K/crew | **33** |
| At an aggressive $400K/crew | **17** |

Cross-check: 400+ operators, ~1,000 robots, **$75M cumulative** network revenue ≈ **$187K per
operator cumulative** — i.e. most of that fleet is part-time or adjacent-service, not a
full-time exterior-cleaning business.

**The model's 300 kW/day × 200 days is not a plan, it is a ceiling nobody has hit.** It must be
recalibrated against observed job values before it is shown to anyone.

---

### Part 2 — What survives the beating

#### 2.1 The services economics are genuinely better than I assumed ✅

| Metric | Value |
|---|---|
| Average **commercial** job | **$14,023** |
| Median job needing 8+ hours flight | **$30,588** |
| Operator payback on hardware | **< 2 months** (vendor claim) |
| Operator with 10+ jobs/yr | **$200,000/yr** |

Fourteen good commercial jobs is a $200K business. That is a real, financeable services company
with modest capex — and it is *nothing like* the residential single-family job the repo currently
models.

#### 2.2 Damage liability is the real product, and nobody sells it ✅

On a **$30,588** job against solar glass, historic stucco or failing window seals, the expensive
event is not a slow clean — it is **destroying a surface**. Our deterministic safety layer
(`safety/checks.py`), hard per-surface pressure ceilings, and hash-chained audit log
(`safety/audit_log.py`) produce something none of the 18 regional operators and none of the
inspection platforms produce:

> **Provable, per-surface, gated execution with a tamper-evident record of what pressure touched
> what material and why.**

That is an **insurance and risk instrument**, not a convenience feature. It is the answer to
"who pays when the panels crack," and it is worth more on a $30K job than on a $600 one.

#### 2.3 Verification has a contractual home — in solar PPAs ✅

Utility and commercial PPAs define obligations by **Performance Ratio** and **Availability
Guarantee**, with documented monthly PR against contract. A cleaning vendor who can hand over a
verified, geolocated, before/after record tied to those metrics is selling into an **existing
compliance requirement**, not creating a new want.

That is where the closed loop stops being a demo and becomes a line item.

#### 2.4 The whitespace is real, just narrower than claimed ✅

- Regional operators: execute, no per-surface model, no verification.
- Inspection platforms: analyse, then hand a human a report.
- Utility solar dispatch systems: close the loop **for PV only, at farm scale, via SCADA** — not
  for mixed-surface buildings, and not with damage-gated execution.

**Nobody joins per-surface prescription + safety gating + execution + verification on
heterogeneous building envelopes.** That's narrower than "nobody closes the loop," and it is
still ours.

---

### Part 3 — The verdict

#### Pursue. But re-aim on three axes.

| Axis | As written | Re-aimed | Why |
|---|---|---|---|
| **Geography** | Coastal Carlsbad | **Inland / desert** — Inland Empire, Imperial Valley, Palm Springs, Phoenix | Soiling 5–25% vs 2–8%; the ROI story only works where the dust is |
| **Segment** | Residential + light commercial, single-family demo | **Commercial / industrial + solar assets** | $14K–$30K per job vs hundreds; multi-aircraft only pays at this scale; damage exposure is where our safety layer earns |
| **Product claim** | "We detect grime" | **"We prove it was cleaned, and prove nothing was damaged"** | Detection is commoditised; gated execution + audit trail is not |

Note that the deconfliction work already told us this: the reference **house supports max 1
aircraft**. Every multi-aircraft economic argument in this repo only pays on large commercial and
solar sites. The code has been pointing at the right customer for a while; the plan hasn't caught up.

#### Sequence — cheapest disproof first

1. **Sell the scan, not the wash.** Inspection + verification reports. No Part 107 spray op, no
   water, no containment, no damage exposure, no drone capex beyond the Autel. `FIELD_OPERATIONS.md`
   §3 already flagged this; the landscape confirms it is uncontested *within cleaning*.
   **This tests whether anyone pays for the intelligence before you bet on hardware.**
2. **Find one inland commercial solar customer** with a PR-based obligation. Deliver the
   before/after verified record against their Performance Ratio.
3. **Only then** decide whether to operate spray hardware yourself, or license to operators who
   already do.

#### Kill criteria — decide these now, honestly

Stop, or change strategy, if:

- **Nobody pays for a scan-only report** after ~10 serious commercial conversations. If the
  intelligence has no standalone value, the moat isn't a moat.
- **Lucid ships per-surface prescription + verification inside Lucid Refresh.** They are funded,
  they own the channel, and they are already building autonomy. This is the single most likely
  way the opportunity closes.
- **The dry-down curve can't be calibrated** to make thermal verification reliable
  (`FIELD_OPERATIONS.md` §6). Without trustworthy verification the loop doesn't close, and the
  loop *is* the differentiator.
- **Recalibrated unit economics stay under ~$300K/crew/yr.** At $200K, $10M needs 33 crews — an
  operational sprawl that contradicts the owner-operated plan.

#### What to fix in the repo immediately

- [ ] **Recalibrate `reports/revenue_model.py`** against observed job values ($14K commercial,
      $30.5K major). The current 300 kW/day × 200 days is unvalidated and 4.8× optimistic.
- [ ] **Reword any claim resting on soiling detection** — patent language, marketing, IP doc.
      Claim the *gated closed loop*, not the sensing.
- [ ] **Add a commercial/industrial reference structure** to `geometry/source.py`. Every demo is
      a single-family house; every dollar is in flat commercial roofs and solar arrays.
- [ ] **Re-run the market assumption in CLAUDE.md §1** — coastal Carlsbad as base market conflicts
      with solar as wedge.

---

### Part 4 — Honest limits of this analysis

- **Vendor figures are promotional.** Payback "under two months" and "400% ROI" are Lucid's
  marketing. The $200K/operator and $14K/job figures were given by Lucid to a trade publication —
  directionally useful, not audited.
- **$75M "network revenue" is cumulative and undated**, so per-operator annualisation is an
  inference, not a measurement.
- **Soiling percentages vary enormously** by microclimate, tilt, and rainfall year. Carlsbad's
  actual number should be measured on real arrays, not read off a blog.
- **No primary research.** No customer interviews, no operator interviews, no state registries.
  Everything here is desk work and should be treated as a hypothesis to test, including the
  verdict.
- **The strongest single validating action** remains asking Lucid directly: *how many operators
  in Southern California, what does a typical SoCal operator bill annually, and does Lucid Refresh
  do per-surface prescription today?* Three questions, and the answers largely settle this
  document.

<a id="docscompetitivelandscape"></a>

---

# Competitive Landscape — California & the Southwest

> **Source file:** `docs/COMPETITIVE_LANDSCAPE.md`

## Competitive Landscape — California & the Southwest

> Who is already doing drone exterior cleaning in our target geography, and what that means
> for positioning.
>
> **Screened 2026-08-16 by web scan. Not exhaustive.** This market is fragmented and fast-moving;
> most operators are 1–3 person outfits that never rank in search. Treat the counts as a
> **floor, not a census** — the real number is higher.

---

### 0. The headline

**The service layer is crowded. The intelligence layer is empty.**

We found **~18 identified drone exterior-cleaning operators across CA + AZ**, including
**three already working San Diego County — one of which names Carlsbad as a core market.**

But none of them appear to be doing what PROPWASH's moat actually is: the closed
sense → fuse → prescribe → execute → verify → re-queue loop. The companies that *do* have
inspection-grade thermal analytics are **inspection companies, not cleaning companies**.

That gap is the whole strategic finding of this document.

---

### 1. California — ~14 identified

#### San Diego County — our base market, already contested

| Company | What they do | Threat |
|---|---|---|
| **DronePower1** | Drone solar cleaning, DI water, purpose-built fleet. **Explicitly names Carlsbad a core San Diego market**, citing *high solar adoption on Spanish-tile roofs*. Veteran-owned | 🔴 **Direct.** That is our stated wedge, our stated base market, and our stated roof type — someone got there first |
| **CleanEdge Technologies** | Drone exterior + solar, San Diego. Targets hotels, HOAs, logistics roofs, corporate/stadium solar, municipal campuses | 🔴 **Direct.** The commercial-solar wedge |
| **South Bay Solar Cleaning** | Commercial drone washing, San Diego + SoCal; Tesla Solar Roof specialty | 🟠 Adjacent-direct |
| **California Drone Cleaning** | LA-based, services **San Diego to San Francisco** | 🟠 Statewide coverage |
| *Advanced Solar Cleaning* | Solar panel cleaning, San Diego (not drone-based) | 🟡 Incumbent to displace |

#### Los Angeles / SoCal

| Company | Note |
|---|---|
| **Los Angeles Drone Wash** | Facades, rooftops, high-rise; CA + Miami |
| **Drone Wash Los Angeles** | Franchise location of DRONEWASH+ |
| **Droneworx Pro-Washing** | SoCal, "premier power washing" |
| **WashMeDrone** | Roof, window, **solar**, high-rise — SoCal **and Phoenix** |
| **AltitudeWash** | Drone window cleaning, streak-free glass |
| **Advanced Drone Solutions** | LA drone cleaning |
| **RayAccessPro** | LA drone window cleaning |

#### Northern California

| Company | Note |
|---|---|
| **Maxx ECO Wash** | **FAA-certified**, positions as NorCal's leading aerial drone building-washing firm. SF Bay, Silicon Valley, Sacramento. The most professionalised operator found in CA |

---

### 2. Arizona — ~5 identified

| Company | Note |
|---|---|
| **Phoenix Drone Pros** | **10+ years flying in the Valley.** Buildings, windows, roofs, solar |
| **The Eco Drone** | Commercial across AZ — Phoenix, Mesa, Chandler |
| **Desert Drone Services** | Buildings, hotels, hospitals, stadiums, schools, churches, apartments |
| **Drone Wash Phoenix** | Franchise location of DRONEWASH+ |
| **WashMeDrone** | SoCal operator also covering Phoenix |

**Nevada, New Mexico, Utah, Colorado: not separately confirmed.** Absence of search results is
not absence of operators — assume similar density in Las Vegas and Albuquerque and verify before
treating them as open territory.

---

### 3. National players pushing into the Southwest

| Company | Why it matters |
|---|---|
| **Lucid Bots** | Not a competitor — **the category leader and our assumed vendor.** ~$34M raised, **400+ active operators across 40+ states, >$75M in operator revenue.** Every one of those operators is a potential competitor *and* a potential SaaS customer |
| **DRONEWASH+** (2021) | Nationwide, **franchise model**, already has LA and Phoenix locations. Franchising is how this market consolidates — and it moves fast |
| **Spinoff Robotics** | Tethered aerial robots: façade + **solar panel washing**. Closest to our solar wedge technically |
| **Apellix** | Tethered industrial power-wash and coating |
| **SkyWash Drones** (Houston, 2022) | Windows, façade, roof — Southwest-adjacent |

---

### 4. The adjacent category nobody has connected to cleaning

There *is* a mature drone-thermal-analytics industry. It just doesn't clean anything:

| Company | What they do |
|---|---|
| **Sitemark** | Solar inspection + drone thermography software |
| **MapperX** | AI-powered PV thermal inspection |
| **Anvil Labs** | Drone digital twins for predictive maintenance |
| **Inspekt AI** | AI drone inspections for building maintenance |
| **Folio3 AI** | Drone inspection + analytics |

These platforms already do things we have not built: automatic classification of thermal
anomalies (hotspots, diode failures, open circuits) **and visual anomalies including soiling**,
pixel-precise measurement, historical digital twins with change tracking.

**Read this carefully — it cuts both ways.**

- ❌ **Against us:** "we detect soiling from thermal + RGB" is *not* novel. It is a shipping
  feature in commercial PV inspection software. Any patent or marketing claim resting on
  soiling detection alone is weak.
- ✅ **For us:** none of them **prescribe a treatment, drive execution, or verify the result**.
  They produce a report and hand it to a human. The loop — prescription, safety gating,
  execution, verification, and *parameter adjustment from the outcome* — is still open.

**Our defensible claim is not "we see the dirt." It is "we close the loop on it."** The
sense→fuse→**prescribe→execute→verify→re-queue** chain is what nobody in either column is doing,
and CLAUDE.md §11 should be read with this in mind.

---

### 5. What this changes

#### 5.1 Being "the drone cleaning company in Carlsbad" is not a position

Three operators already work San Diego County; one markets Carlsbad specifically on the
tile-roof-solar thesis. With Lucid at 400+ operators, buying a Sherpa is not a barrier to entry —
it is a purchase order. A services-only business here competes on **price, scheduling and
reputation**, none of which is defensible and none of which is what this codebase is.

#### 5.2 The intelligence layer is the actual whitespace

Nobody in either column joins inspection-grade analytics to cleaning execution and verification.
That is the gap, it is where all the code in this repo already points, and it is consistent with
the SaaS line already modelled in `reports/revenue_model.py`.

#### 5.3 Lucid's 400+ operators are the market, not the competition

This is the most actionable finding in the document. Those operators:

- already own the hardware — no capex to sell them;
- have no prescription intelligence, no per-surface model, no verification;
- are exactly who a licensing product is for.

**Selling to the operators beats out-competing them.** It also reframes the Lucid relationship:
we are not asking for a control API to compete with their customers, we are offering a layer
that makes their customers' fleets more valuable — a materially easier conversation
(`VENDOR_OUTREACH.md`).

#### 5.4 The verification product may be the wedge, not the wash

`FIELD_OPERATIONS.md` §3 already found that scan-only is viable revenue with **no spray
liability**. This landscape strengthens that: the scanning/reporting layer is uncontested in
cleaning, needs no Part 107 spray operation, no water, no containment, no damage exposure — and
it is the half of the business that is actually differentiated.

---

### 5.4b "Apex" — checked, and it is not a manufacturer

*Checked 2026-08-16. Two companies trade under the name; **neither sells drones**.*

| | |
|---|---|
| **Apex Drone Cleaning** — `apexdronecleaning.com` | US service operator. HQ **Greenville, SC**, plus **Southeast Florida**. Buildings, windows, solar, up to 25 storeys |
| **Apex Drone Wash** — `apexdronewash.com.au` | **Sydney, Australia.** CASA-approved pilots. Markets **soft wash explicitly** — *"clean without high-pressure risks, perfect for sensitive materials like solar panels, windows, and facades"* |

**Apex Drone Cleaning sells services only — no drones, no equipment.** They name no hardware
manufacturer or model, describing it only as *"state-of-the-art drone technology."*

**Two things worth taking from it:**

1. **They are a competitor, not a supplier** — the same category as the ~18 CA/AZ operators above,
   just in different states.
2. **They have no intelligence layer at all.** No mapping, no analytics, no inspection reports, no
   verification method — the only documentation mentioned is **before-and-after photos**. That is
   precisely the gap this company exists to fill, and more evidence that the service tier competes
   on price and reputation rather than capability.

**Useful validation:** Apex Drone Wash marketing **soft wash as the selling point for solar,
windows and façades** confirms the low-pressure positioning is commercially proven, not a niche
engineering preference (`decisions/BUILD_SPEC.md` §2).

---

### 5.5 Does the Sherpa map the building? **No.** ⭐

*Checked 2026-08-16 against Lucid's own product pages.*

This matters more than any other single capability question, so it was checked directly rather
than assumed.

| Question | Finding |
|---|---|
| Does the Sherpa map / 3D scan / survey? | **No.** No mapping, 3D scanning, reality capture or surveying appears anywhere in Lucid's Sherpa material |
| Is it autonomous? | **No.** *"The Sherpa Drone is operated by a single pilot with one ground crew member,"* requiring **FAA Part 107** certification |
| What sensing does it have? | Collision-avoidance radar (0.5–50 m per earlier vendor material). **Obstacle avoidance, not mapping** — the same distinction as laser rangefinder ≠ LiDAR |
| SDK / API / developer program? | **None published.** The only software offering on the product page is *Sherpa Academy*, a training course |
| Their `/platform` page | Returns **404** |
| The "Smarter, Swifter, and Open to All" post | An **industry roundup**, not a product announcement. Its RTK sub-inch site models and 3D Gaussian splatting language describes **competitors' drones**, not Lucid products |

#### What this means

**1. The mapping layer is wide open.** The Sherpa is a spray tool that sprays where a pilot
points it. It has **no model of the building, no per-surface knowledge, and no record of what was
cleaned.** Everything PROPWASH does upstream of the nozzle is uncontested by the category leader.

**2. It validates the two-drone architecture** (CLAUDE.md §6). Scout maps, cleaner sprays, both
sync through the plan. **Lucid has no scout.** To close the loop they would need a sensing
aircraft, a photogrammetry pipeline, a per-surface model and a verification stage — which is the
entire contents of this repository.

**3. It reframes "Lucid doesn't allow integration."** They are not blocking you. **There is
nothing to integrate into** — no API, no addressable onboard compute, no map to enrich. The
Sherpa is a well-built end-effector on a human-piloted airframe.

#### ⚠️ The caveat that keeps this honest

**Lavo AI is marketed as an autonomous pressure-washing robot.** A ground robot that navigates
autonomously needs SLAM — so **mapping competence exists inside Lucid**, it is simply not in the
Sherpa product. They also acquired the autonomy company Avianna, and just raised $20M.

**So this is a current-product gap, not a capability gap.** It is a real opening, and it is the
opening most likely to close from their side. That is already logged as a kill criterion in
`GO_NO_GO.md` §3 — *"Lucid ships per-surface prescription + verification inside Lucid Refresh."*
Add mapping to that trigger.

---

### 6. Honest limits of this scan

- **Web search only.** No state business registries, no trade-association lists, no USPTO.
- **Undercounts badly.** Small operators without SEO are invisible here. The true CA + AZ count
  is likely **2–3× what we found**.
- **NV / NM / UT / CO unverified.** Do not treat as open territory.
- **No revenue, headcount or fleet data** for any regional operator — we cannot tell a
  one-drone side business from a real firm.
- **Capability claims are their marketing**, not verified. "AI-powered" on a cleaning company's
  site usually means route planning, not a fusion model.

**Before acting on this:** pull the state business registries for CA and AZ, and — the fastest
signal available — **ask Lucid how many of their 400+ operators are in Southern California.**
That single number tells you more about the competitive density of the base market than any
amount of searching.

<a id="docsbusinessplan"></a>

---

# PROPWASH — Path to $10M/year

> **Source file:** `docs/BUSINESS_PLAN.md`

## PROPWASH — Path to $10M/year

> Strategy is the source of truth for *direction*; numbers here are **goals to validate, not facts**
> (per CLAUDE.md §15.5). Treat every dollar figure as a hypothesis with a test attached.

---

### 0. The core insight

PROPWASH is **not a drone-cleaning service**. It is a **data-and-software company** that uses a
cleaning service as (a) its go-to-market wedge and (b) its data-collection engine. The defensible,
scalable asset is the closed-loop intelligence (Sense → Fuse → Plan → Execute → Verify → re-queue)
and the calibrated prescription + verification models — **not** swinging a wand at more buildings.

A single fully-booked crew tops out around **$600–800K/year** (≈3 jobs/day × ~$1,000 × 5 days).
$10M as pure services ⇒ ~13+ crews ⇒ low-margin, labor-heavy treadmill. That is not the plan.

**The plan: services prove and feed the system; recurring commercial contracts + software licensing
produce the $10M.**

---

### 1. The wedge: AI-verified solar cleaning

Lead with **AI-verified solar panel + roof cleaning**, not generic "exterior cleaning." Why solar first:

| Reason | Why it matters |
|---|---|
| **Quantifiable ROI** | Dirty panels lose 5–20% output. Thermal scan *measures* soiling before/after — you sell **measured output recovery with proof**, not "we cleaned it." |
| **Recurring** | Panels re-soil → quarterly/biannual contracts → recurring revenue (the thing that scales and is valuable). |
| **Commercial scale** | Warehouses, dealership canopies, HOAs, municipal, small solar farms = $50K–500K+ recurring contracts. A handful = most of the number. |
| **Lowest risk surface** | DI water only, low pressure (CLAUDE.md §9) → least damage/liability while learning. |
| **Drone-native** | Rooftop commercial work is dangerous/expensive for humans; drones are genuinely better. |
| **Ties to your tech** | Your thermal sensor directly detects soiling/hotspots → your verification loop *is* the value prop. |

Win solar → land-and-expand into roofs/gutters/façades for the same customers.

⚠️ **Riskiest assumption to kill first:** that thermal soiling cleanly maps to recoverable kWh.
Prove it on the first 5 jobs before building a sales deck on it (see §5).

---

### 2. Products to build (in order)

1. **Operator app** — per-zone checklist, nozzle/standoff/dwell guidance, live thermal overlay,
   PASS/retry. Lets a non-expert be productive → scale crews without scaling expertise. *(Operational moat.)*
2. **Customer ROI report** — automated before/after thermal report showing measured soiling removed
   and estimated output/value recovered. **This is the sales + retention engine.** *(Built — see
   `propwash/backend/reports/roi_report.py`.)*
3. **PROPWASH SaaS platform** *(the $10M unlock, yr 2+)* — license the orchestration + verification
   software to other Lucid Sherpa operators / cleaning contractors. 80%+ margins. This is where the
   valuation and the $10M get real.

---

### 3. The flywheel

Every job feeds the calibrated surface/pressure table + verification model (trade secrets, §11).
More jobs → better prescriptions → better results → better proof → more contracts → more data.
After ~12–18 months of real jobs the prescription model is non-replicable by new entrants **and**
is the thing you license. Services build the moat; software is the money.

---

### 4. Phased path (milestones, not promises)

| Phase | Window | Focus | Crews | Run-rate (goal) |
|---|---|---|---|---|
| **0 — Prove the loop** | 0–6 mo | 20–40 paying solar/roof jobs; nail unit economics + verify loop | 1 | $100–250K |
| **1 — Recurring commercial** | 6–18 mo | Convert proof → recurring contracts (PM firms, HOAs, solar O&M) | 2–3 | $1–2M |
| **2 — Productize** | 18–36 mo | Launch SaaS + franchise/equipped-operator model in new metros | network | toward $5–10M |

$10M ≈ **recurring commercial contracts + software licensing + a network of operators on your platform** —
not you personally cleaning everything.

---

### 5. 30 / 60 / 90 day plan

**Next 30 days**
- Commit to solar as the wedge.
- Run 5 real solar jobs (even at cost). Produce 5 ROI reports.
- **Validate the thermal → kWh recovery correlation** (the make-or-break assumption).
- Capture true cost-per-job.

**Next 60 days**
- Operator app + ROI report to MVP.
- Sign first *recurring* commercial pilot (one HOA or one commercial solar site).
- Call Lucid (see `docs/LUCID_OUTREACH.md`).

**Next 90 days**
- Close 3 recurring contracts.
- Harden prescription model on real data.
- Decide the Phase-2 fork (services-led vs. platform-led).

---

### 6. Risks to kill early (do not skip)

1. **Lucid dependency (§7):** No confirmed API; in-house autonomy. Call them this month. If they
   won't partner, the licensing play must target their operator base *with* them or stay Path A.
   **Single biggest strategic unknown.**
2. **Thermal-ROI must be real (§5):** Edge is "measured output recovery." Prove on first 5 jobs.
3. **Honest claims (§5, §7, §11):** No "multispectral," no "fully autonomous." Honesty *is* the
   moat and what makes you fundable.
4. **Part 107 / operator-in-command (§10):** Don't design flows that hide automation from the
   regulator. More flight automation needs an FAA pathway.

---

### 7. The open strategic fork

**Operator-led services company with great software**, or **software/platform company that licenses
the brain?** The blended path above leans platform (that's where $10M lives), but it's a function of
your appetite for ops vs. product. Decide by end of Phase 0 — the data from real jobs will tell you
which one the market is pulling you toward.

<a id="docsscalingto10m"></a>

---

# PROPWASH — Full Report: What It Takes for YOUR OWN Company to Reach $10M / Year

> **Source file:** `docs/SCALING_TO_10M.md`

## PROPWASH — Full Report: What It Takes for YOUR OWN Company to Reach $10M / Year

> **Scope:** owner-operated cleaning company. **No licensing / SaaS in the core plan** — that's a
> later, separate business model (see §12). This report is the path to $10M as a business *you own
> and run*.
>
> Every dollar figure is a **goal to validate, not a fact** (CLAUDE.md §15.5). Inputs marked
> **UNVERIFIED** (e.g. Sherpa unit cost) must be confirmed. All numbers are produced by
> `propwash/backend/reports/revenue_model.py` — edit the assumptions and re-run
> (`python -m propwash.backend.reports.revenue_model`) to stress-test them.

---

### 1. Executive summary

As an owner-operated services company, $10M/year is reachable **without licensing**, but only by
combining three things: (1) **recurring** commercial contracts, (2) a **verification premium** on
price (your thermal before/after proof lets you charge more than commodity cleaners), and (3)
**multi-surface upsell** (solar → roof → gutter → façade on the same accounts). The lever that keeps
it from becoming a 14-crew treadmill is **revenue-per-crew**, not crew count.

**Recommended route — PREMIUM (7 crews):**

| Stream | Revenue | Gross profit |
|---|---:|---:|
| Own services (recurring commercial) | $6.72M | $3.36M |
| Multi-surface upsell + verification premium | $3.70M | $1.85M |
| **TOTAL** | **$10.42M** | **$5.21M (50% margin)** |
| Crew capex to stand up 7 crews | — | ~$731K (staged) |

**Alternative — VOLUME (10 crews):** ~$10.66M at base pricing; same ~50% margin but **3 more crews,
~$1.05M capex, and a lot more operational/HR load.** The premium route gets to the same number with
fewer moving parts — that's the smarter build.

---

### 2. The two owner-operated routes (pick PREMIUM)

| | PREMIUM (recommended) | VOLUME |
|---|---|---|
| Crews | **7** | 10 |
| Pricing | ~$16/kW (verification premium) | ~$12/kW (base) |
| Upsell intensity | High (0.55 uplift) | Moderate (0.48) |
| Site focus | Larger commercial + portfolios | Broader mix |
| Total revenue | ~$10.4M | ~$10.7M |
| Capex | ~$731K | ~$1.05M |
| Ops/HR burden | Lower | Higher |

Same destination, fewer people and less capital on the premium path. You earn the premium with the
ROI report — measured kWh recovered is something commodity pressure-washers cannot show.

---

### 3. Unit economics (the engine)

- **Commercial solar pricing:** base ~$12/kW per clean; **premium ~$16/kW** with verification proof. VALIDATE on real bids.
- **Crew throughput:** ~300 kW/day × 200 working days = **$720K/crew/year** gross at base price (~$960K at premium).
- **Services gross margin:** ~50% after labor, chemicals, travel, insurance, equipment depreciation.
- **Recurring cadence:** 2 cleans/site/year (biannual) — this is what makes revenue compound instead of resetting.
- **Capex per crew:** ~$104.5K = Sherpa (**~$60K, UNVERIFIED**) + Autel 640T (~$9.5K) + truck/kit (~$35K).
- **Capex for 7 crews:** ~$731K, **staged across years** — you do not buy 7 kits on day one.

Value-story example (from the ROI generator): a 205 kW site with heavy soiling →
**~$6,900 / ~21,700 kWh estimated recovered** per service. That proof justifies the premium and the renewal.

---

### 4. What needs to be BUILT (product & engineering)

Ordered by leverage. Status reflects this repo today. (Owner-operated plan — note SaaS/multi-tenant
items are deferred to §12.)

| # | Build item | Why it's required | Status |
|---|---|---|---|
| 1 | Core loop: schemas, safety, agents, orchestrator, sim | Foundation of everything | ✅ Done |
| 2 | Customer ROI report | Earns the verification premium + drives renewals | ✅ Done |
| 3 | **Operator app** | Non-experts run jobs → add crews without adding experts | ⬜ Next |
| 4 | **Fusion pipeline on real Autel imagery** | Real zone signatures instead of sim | ⬜ |
| 5 | **Persistence: Postgres + PostGIS + Redis** | Many jobs/properties/crews at once | ⬜ |
| 6 | **Scheduling/dispatch + recurring-contract engine** | Recurring revenue needs automated re-booking | ⬜ |
| 7 | **Calibration/learning loop** | Field data → better prescriptions → higher first-pass PASS rate → lower cost/job | ⬜ |
| 8 | Path B/C transports (only if Lucid opens API) | Higher automation, flagged off until §7 resolved | ⬜ Gated |
| — | ~~Multi-tenancy + billing~~ | **Deferred — only needed for licensing (§12)** | ⏸ Later |

---

### 5. What needs to be OPERATIONALIZED (people, equipment, capital)

- **Crews:** scale 1 → 7 over ~4–5 years. Each crew = 1 Part 107 pilot + drone kit + truck.
- **Hiring ladder:**
  - *Phase 0:* you operate (founder-pilot).
  - *Phase 1:* +1–2 pilots, +1 ops/sales hire.
  - *Phase 2:* +ops manager, +scheduler/dispatcher, +1–2 more pilots, dedicated sales.
  - *Phase 3:* +account managers for recurring portfolios, +finance/admin.
- **Equipment:** buy drone/truck kits to demand; don't pre-buy.
- **Capital:** ~$731K crew capex (staged) + payroll runway. Owner-operated services can largely
  **self-fund from recurring cash flow** once Phase 1 contracts land — likely **less outside capital
  than a software play**, which is an advantage of this route. A working-capital line or equipment
  financing for drone kits is the most likely outside need.
- **Insurance & compliance:** commercial drone liability, workers' comp, Part 107 currency per pilot.

---

### 6. What needs to be SOLD (go-to-market & pipeline math)

- **Wedge:** AI-verified commercial **solar** cleaning — quantifiable ROI, recurring, drone-native, safest surface.
- **Buyers:** property managers, HOAs, REITs, solar O&M firms, school districts, municipalities, warehouse/logistics owners.
- **Recurring-contract math (premium route):** $6.72M of own-services at an average ~$40–60K/yr
  recurring account ⇒ roughly **110–170 active recurring accounts**, built over years.
- **Land-and-expand motion:** one site → ROI report proof → portfolio rollout → multi-surface
  bundle → biannual auto-renewal. Net revenue retention is the quiet engine of this plan.
- **Why you win the bid:** you don't quote "a cleaning," you quote **measured output recovery with proof.**

---

### 7. Partnerships & regulatory (gates, not optional)

- **Lucid (§7):** Even owner-operated, your execution rests on Lucid hardware with no confirmed API.
  Work `docs/LUCID_OUTREACH.md` now — at minimum confirm Refresh data access; a partnership de-risks fleet growth.
- **FAA Part 107 (§10):** Operator stays in command. Each crew needs a current Part 107 pilot. Any
  increase in flight automation needs a proper FAA pathway/waiver — budget time/legal; don't assume it.
- **Legal/IP (§11):** Provisional patent on the *method*; keep the prescription table + learning model
  as trade secrets. Engage counsel. A provisional is a placeholder, not protection.

---

### 8. The data moat (why this stays defensible even as services)

Every job feeds the calibrated surface/pressure table + verification model. Higher first-pass PASS
rate → fewer re-cleans → lower cost/job → fatter margin than competitors at the same price. The moat
shows up as **margin and reliability**, not just as a future product.

---

### 9. Year-by-year milestone ladder (owner-operated)

| Year | Revenue (goal) | Crews | The job to be done |
|---|---:|---:|---|
| **0** (0–6 mo) | $0.1–0.25M | 1 | Prove loop; 20–40 jobs; validate thermal→kWh; nail unit economics |
| **1** | $0.7–1.2M | 2 | First recurring commercial contracts; operator app + DB; call Lucid |
| **2** | $2.5–3.5M | 3–4 | Scheduling/recurring engine; learning loop live; build sales muscle |
| **3** | $5.5–7M | 5–6 | Premium pricing established; portfolio accounts; account managers |
| **4–5** | **$10M+** | 7 | Premium route at steady state; ~50% gross margin |

---

### 10. KPIs to track from day one

- Cost per job + gross margin per job
- **Thermal-soiling → measured kWh-recovered correlation** (make-or-break metric)
- First-attempt verification PASS rate (drives cost/job and the moat)
- Recurring contract count + net revenue retention
- Revenue per crew (the lever that keeps crew count down)
- Re-soil interval per site (drives renewal cadence)

---

### 11. Kill-list — validate before betting big

1. **Thermal soiling ↔ recoverable kWh** is real and measurable (whole solar wedge rests on it).
2. **You can actually charge the ~$16/kW premium** — that the proof commands the price.
3. **Sherpa unit cost (~$60K)** and throughput (~300 kW/day) hold against reality.
4. **Lucid** at least exposes job data; ideally partners on fleet growth.
5. **Part 107 / automation** path doesn't block the operational model or crew scaling.

Hit these cheaply and early. The premium route's whole advantage (#2) depends on #1 being true.

---

### 12. Licensing — the LATER business model (explicitly not in this plan)

Once you have 18+ months of field-calibrated data and a hardened product, you *can* add a second
business: license the PROPWASH intelligence layer to other operators (SaaS). For reference, that
would add a high-margin (~80%) stream and could lift the blend to ~$10M with **fewer crews (6) plus
~140 licensed fleets at ~61% margin** — but it requires multi-tenancy + billing (deferred in §4),
the Lucid relationship, and a product mature enough to hand to strangers. **Park it as Phase 3+
upside; don't let it pull focus from the owner-operated build now.**

<a id="docsbrandnaming"></a>

---

# Brand Naming — Exploration Shortlist

> **Source file:** `docs/BRAND_NAMING.md`

## Brand Naming — Exploration Shortlist

> ⚠️ Exploratory. NOT trademark-cleared and NOT domain-checked. Before adopting any name,
> run a real search (USPTO TESS + common-law) and confirm `.com`, then engage counsel
> (`IP_PROTECTION.md` §11 — you trademark the brand, in classes **37** cleaning services +
> **42** software/SaaS). Current working name: **PROPWASH**.

---

### Naming criteria (the filter)

1. **Distinctive, not descriptive** — coined/suggestive names are trademarkable; "Drone
   Cleaning Co." is not. (PROPWASH passes — aviation term + "wash".)
2. **No overclaiming in the name** — avoid "Auto/Autonomous" (Part 107, §7) and
   "Spectral/Multispectral" (§5). The name must not promise capabilities we don't ship.
3. **Works for classes 37 (cleaning) + 42 (software).**
4. **Short, memorable, pronounceable; `.com` gettable.**
5. **Names the value where possible** — the moat is the per-surface intelligence, not the drone.

---

### Candidates by positioning

#### A — Aviation wordplay (the PROPWASH vein)
| Name | Why |
|---|---|
| **Downwash** ⭐ | Rotor air that drives spray *down onto* the surface — as clever as Propwash, fresher |
| Slipstream | Flight term; motion + smoothness |
| Rotorwash | Literal; a bit generic |
| Skywash | Aerial + clean; simple |
| Updraft | Aerial lift; less tied to cleaning |

#### B — Intelligence / per-surface brain (the actual moat)
| Name | Why |
|---|---|
| **Facet** ⭐ | A building's *facets* are exactly what the model classifies; connotes a cut gem = precision. Tech-company feel, ownable |
| Surfacet | "Surface" + "facet"; more literal, likely more available |
| Vantage | Oversight / the verify-and-watch angle |
| Aperture | Optics/vision; the sensing layer |
| Overstory | Canopy/overview (note: used by a tree-analytics firm — check) |

#### C — Clean / shine / clarity
| Name | Why |
|---|---|
| **Lustre** / Luster | Premium shine; consumer-friendly |
| Sheen | Short, clean; may be hard to own |
| Pristine | Descriptive — weaker trademark |
| Verge | Building edges / "on the verge" |

#### D — The verify loop (closed-loop differentiator)
| Name | Why |
|---|---|
| **Verity** | Truth/verification — names the verify-and-re-queue loop |
| Truewash | Verification + wash; a bit plain |
| Reclaim | Restoring surfaces; evocative |

#### E — Coastal / solar (San Diego roots)
| Name | Why |
|---|---|
| Meridian | Sun at its peak; navigation |
| Halcyon | Calm/clear; premium |
| Solstice | Sun; strong for the solar wedge |

---

### Recommendation (top picks)

1. **PROPWASH — keep it.** Distinctive, ownable, aviation term + wash, already embedded in the
   codebase/docs. The bar to replace it should be high.
2. **Facet** — best *new* direction: names the defensible thing (per-surface intelligence),
   reads as a precision tech company. Forms: `Facet`, `Facet Robotics`, `FacetAI`.
3. **Downwash** — freshen the aviation-wordplay family without losing its cleverness.
4. **Lustre** — if leaning premium-consumer cleaning over tech.

---

### Brand architecture — multi-surface (air + ground)

PROPWASH is expanding beyond aerial: **ground robots (Lucid Lavo Bot, CLAUDE.md §4) for
concrete floors / parking decks / warehouses**, alongside the aerial cleaning drones. The
moat (the intelligence layer) is **surface-agnostic**, so one parent brand can span both.
Problem: "PROP" = propeller = *aerial only*, so it doesn't naturally cover a wheeled floor
robot. Solution — a **"—WASH" brand family** with PROPWASH kept as the flagship:

- **Company / parent:** **PROPWASH Robotics** (robotics = air + ground; extensible; keeps the name)
- **Aerial line:** **PROPWASH** — drones: exteriors, roofs, solar (unchanged)
- **Ground / concrete line:** a "—WASH" sibling (below)

#### Ground / concrete-floor line candidates
| Name | Why |
|---|---|
| **SLABWASH** ⭐ | Concrete *slab* — floors, parking structures, warehouses; pairs perfectly with PROPWASH |
| DECKWASH | Parking decks, floors, patios |
| PAVEWASH | Pavement / hardscape |
| GROUNDWASH | Direct air-vs-ground contrast with PROPWASH |
| TERRAWASH | "Terra" = ground/earth |

**Recommended pairing: PROPWASH (air) + SLABWASH (ground)** under **PROPWASH Robotics** —
same cadence, signals a platform not a one-trick service, keeps the name you like.

#### Alternative: surface-agnostic parent
Keep PROPWASH as just the air line, with a neutral parent: **Facet** / **Vantage** (platform)
over PROPWASH + SlabWash; or an umbrella "—WASH" (**OmniWash**, **ApexWash**).

#### Trademark note
A **family of "—WASH" marks** is a recognized strategy, but "wash" is descriptive for
cleaning — protectability rides on the **distinctive prefix** (PROP-, SLAB-). Each is
registrable on its prefix in classes 37 + 42; still needs a real USPTO/counsel search (§11).

---

### Availability — preliminary web check (2026-07-06)

⚠️ **Preliminary web scan only — NOT a USPTO/TESS search and NOT authoritative domain checks.**
Existing use ≠ a registered mark, and absence from search ≠ available. Counsel + TESS + a
registrar still required before adopting anything.

| Name | Web finding | Read |
|---|---|---|
| **PROPWASH** | ⚠️ **Crowded** — Propwash Drone Solutions LLC (drone!), PropWash Co (apparel, propwash.co), PropWash Simulation, Propwash Aviation LLC | Real likelihood-of-confusion risk (drone-adjacent) + good domains gone. Usable maybe as "PROPWASH Robotics" + counsel opinion + alt domain |
| **DOWNWASH** | ✅ No cleaning/drone company found | ⭐ Same aviation cleverness as Propwash, apparently open — strongest air-line candidate |
| **SLABWASH** | ✅ No cleaning/concrete company found | ⭐ Strong ground/concrete line; pairs with Downwash or Propwash |
| **FACET** | ✅/⚠️ No direct cleaning/robotics competitor, but very common word (Facet Wealth, etc.) | .com gone, class-42 crowded; usable with a modifier |
| (context) **Drone Wash, LLC** | Registered TMs for building/facade/solar cleaning | The descriptive "—wash" cleaning space has active filings — distinctiveness matters |

**Revised recommendation:** you love PROPWASH for its aviation wordplay — **DOWNWASH gives the
same cleverness but appears actually available.** Consider the clear family **DOWNWASH (air) +
SLABWASH (ground)** under a "…Robotics" parent, or proceed with PROPWASH knowing it needs a
modifier, an alternate domain, and a counsel opinion on the existing drone company.

**Still required before adopting:** USPTO TESS + common-law search (counsel, classes 37+42),
registrar domain check, social handles.

#### Landscape scan (what's already out there)
- **Aerial drone-washing operators — crowded & descriptive (weak marks):** Drone Force USA,
  Drone Clean USA, **Drone Wash LLC (registered TMs)**, Droneworx Pro Washing, Pressure
  Doctor, RayAccess, Window Hero, Sun Brite, **Skywash Innovations (drone cleaning)**.
- **"Sky-/Aero-wash" — crowded (aircraft cleaning):** ❌ **SKYWASH** (Skywash International +
  skyVac skyWash + Sky Power Wash + Skywash Innovations), ❌ **AEROWASH** (Aerowash AB, aircraft
  washing robots). Avoid both.
- **Manufacturer product names — distinctive but taken:** Sherpa, **Lavo / Lavo Bot** (Lucid,
  the ground robot you'll use; "lavo" = Latin "I wash"), Apellix, Neo (Avidbots), KIRA (Kärcher).
- **Ground robotic washing:** Lucid **Lavo AI / Lavo Bot** is the first fully autonomous
  ground pressure-washing robot — the concrete-floor unit in the plan (CLAUDE.md §4).
- **Open-ish "—wash" prefixes found:** ✅ **DOWNWASH**, ✅ **SLABWASH**, ~ **DECKWASH** /
  **WASHBOT** (no strong brand, but generic/descriptive).

**Takeaway:** the operator space is saturated with descriptive "Drone/Sky/Aero + Wash/Clean"
names (weak, crowded). The distinctive, ownable lane is a clever/coined mark — **DOWNWASH (air)
+ SLABWASH (ground)** is the clear, distinctive family; avoid sky-/aero-/drone-wash entirely.

---

### Round 2 — fresh direction (catchy + ownable, not "—wash")

Kevin ruled out Downwash/Slabwash. The honest naming truth this space keeps proving:
**purely descriptive names are taken or weak** (Brightwork = taken by exterior cleaners incl.
an OC solar/pressure-wash firm; Drone/Sky/Aero-Wash all crowded). The win is a **distinctive,
suggestive/coined brand + a descriptive tagline** — the name is ownable, the tagline does the
describing. This is also how the robotics players name themselves (Lucid, Verobotics, Kite).

#### Preliminary-clear coined candidates (✅ no cleaning/robotics conflict found)
| Name | Root / meaning | Feel | Forms |
|---|---|---|---|
| **NITIDO** ⭐ | Latin/Italian *nitido* = clean, bright, sharp | Premium, techy, memorable | Nitido · Nitido Robotics |
| **TERSO** | Latin *tersus* = wiped clean, polished | Short, modern, brandable | Terso · Terso Robotics |
| **LUSTRO** | *lustre/gloss* (IT/ES/PL) | Evokes the shine/result | Lustro · Lustro Robotics |

Tagline carries the "what": e.g., **"NITIDO — robotic exterior cleaning, verified."** or
**"NITIDO Robotics — map. clean. prove."** (the sense→clean→verify loop).

#### Why coined beats descriptive here
- **Trademark strength:** suggestive/coined marks are the strongest and most ownable; generic
  descriptors ("Drone Wash") are weak or unregistrable and, as shown, already taken.
- **Multi-surface:** a coined name isn't locked to "aerial" (unlike Propwash) — it covers the
  air drone AND the ground robot cleanly.
- **Domain reality:** short coined words are far likelier to have an affordable `.com`
  (or `getX`/`Xrobotics.com` fallback) than common English words (Facet/Vertex/Cascade `.com` gone).

#### Verdict
Lead candidate: **NITIDO (Robotics)** + descriptive tagline. Alternates: **TERSO**, **LUSTRO**.
All three appear clear in-space (still need TESS/counsel + registrar checks). Avoid English
descriptors — the space has proven they're taken.

---

### Round 3 — expanded screened set (coined/evocative)

Preliminary web scan only (not TESS/registrar-authoritative). Grouped by flavor.

#### ✅ Apparently clear in-space (worth clearing formally)
| Name | Root / meaning | Flavor |
|---|---|---|
| **NITIDO** ⭐ | Latin/Italian: clean, bright, sharp | clean + premium/techy |
| **NITOR** | Latin: brightness, splendor (root of nitido) | shine, short/strong |
| **TERSO** | Latin *tersus*: wiped clean, polished | clean, modern |
| **TERGO** | Latin *tergere*: to wipe clean | clean, distinctive |
| **LUSTRO** | lustre / gloss | the shine result |
| **CLARIA** | *clarus*: clear, bright | clarity + AI feel |
| **RIVO** | Latin *rivus*: stream | water / flow |

#### ⚠️ Deprioritized — adjacency conflicts found
| Name | Why out |
|---|---|
| Lumio | prominent residential **solar** company (your wedge) |
| Solix | Solinftec **Solix** solar-powered sprayer robot |
| Renovo | established **car-care** brand |
| Puravia | too close to "Pura Vida" cleaning companies |
| Verio | **Verobotics** = facade-cleaning-robot company |
| Brightwork | multiple exterior cleaners (incl. an OC solar/pressure-wash firm) |
| Skywash / Aerowash | aircraft-cleaning brands |
| Propwash | drone company + apparel already own it |

#### More ideas to consider (NOT yet screened)
Clario · Claro · Vitrea (Latin *vitreus* = glassy/clear) · Sereno · Munda (Latin: clean) ·
Aeris (air) · Onda (wave) · Puro · Niva

#### Refined top 3
1. **NITIDO** — clean/bright, premium, multi-surface, techy. Lead.
2. **NITOR** — shorter, punchier sibling (same Latin root).
3. **TERSO** — modern, brandable ("Terso Robotics").

**Competitor names to avoid echoing:** Verobotics, Skyline Robotics, SolarCleano, AX Solar
Robot, Solavio, Lucid/Sherpa/Lavo, Kärcher, Apellix.

---

### Round 4 — the company's *character* (identity-driven names)

Instead of "clean" words, these embody what PROPWASH *is*. All ✅ appear clear in the
cleaning/drone space (but several are common in defense/tech broadly → class-42 may be
crowded; class-37 cleaning looks open). Preliminary scan, not TESS/registrar.

#### The Seer — all-seeing intelligence that maps + verifies (the moat)
| Name | Why it fits the character |
|---|---|
| **ARGUS** ⭐ | Argus Panoptes, the hundred-eyed all-seeing guardian of myth — the company's whole edge is *seeing* every surface and *verifying* the clean. Mythic, memorable, ownable |
| **KESTREL** ⭐ | The falcon that *hovers* dead-still while scanning with extraordinary sight, then strikes with precision — literally a cleaning drone: hover → see → act. Aerial + precision |
| Vantage | Commanding view / oversight |

#### The Guardian — protects & restores the building envelope
| Name | Why |
|---|---|
| **AEGIS** | The shield of Athena — protection; caretaker of the building's surfaces (common in defense, but clear in-space) |
| Halcyon | Calm/clear; the mythical bird that stilled the seas — premium, serene |

#### The aerial / coastal spirit (San Diego, flight, water)
| Name | Why |
|---|---|
| **TERN** | Coastal seabird that dives cleanly to the water — aerial + water + San Diego coast; short, brandable |
| **ZEPHYR** | The gentle west wind — light, aerial, clean, motion |

#### Refined standouts (this round)
1. **ARGUS** — captures the intelligence/verification character better than any name so far.
2. **KESTREL** — the perfect metaphor for the drone itself: hover, see, strike with precision.
3. **TERN** — clean, coastal, aerial, short; strong if you want lighter/friendlier.
4. **AEGIS** — if you want to lean "guardian/protection."

**Note on breadth:** Argus/Aegis/Zephyr/Vantage are widely used in defense & tech — great in
the cleaning class, but budget for a crowded software class-42 search. Kestrel and Tern are
less crowded overall.

#### ⚠️ "-Robotics" form check — the mythic/real-words are TAKEN in robotics
Checking the exact company form killed the character-lane favorites:
| Name | Finding |
|---|---|
| **Argus / Argus Robotics** | ❌ ARGUS Robotics (defense) + Argus Systems / Dynamic / Industry / OS — crowded in robotics/AI |
| **Kestrel** | ❌ American Robotics "Kestrel" (C-UAS) + Autel "Kestrel" VTOL drone + Kestrel Drone & Mapping |
| **Halcyon** | ❌ **Contested in ALL 3 classes** — cleaning (Halcyon Solar Panel Cleaners + Halcyon Pressure Washing, Oceano CA + Halcyon Home Services), robotics (Halcyon Robotics), software (Halcyon.ai/Technologies/.io). Also a CA place name (Oceano); domains gone. Beautiful word, but unownable here. |

**Pattern (the real lesson):** evocative real-word/mythic names are *already claimed* across
robotics/AI/drones — popular words are both unavailable AND weak trademarks. **Coined words
keep coming back clear** (and are the strongest marks). Steer to the coined lane.

#### Cross-round finalists (revised)
- **Clean/Latin lane (RELIABLE — still clear):** **NITIDO · NITOR · TERSO · TERGO · LUSTRO · CLARIA · RIVO**
- **Character lane:** mostly taken (Argus/Kestrel/Halcyon ❌); Tern/Aegis remain but are common.
- **Takeaway:** commit to a coined name + descriptive tagline; it's the only lane that's both
  available and ownable.

---

### Round 5 — mythological + acronym (deep cuts that fit)

Famous myths are taken (Atlas/Apollo/Argus/Talos ❌). The **deep-cut myths tied to
purification, water, and the first robot** screen clear — and several double as acronyms of
the company's capabilities. Preliminary scan, not TESS/registrar.

#### ✅ Mythological — clear in-space, on-theme
| Name | The story (why it fits) | Notes |
|---|---|---|
| **KATHAROS** ⭐ | Greek *katharós* = "pure, clean" — the root of **catharsis** (a cleansing). The essence of clean, made a name | clear; distinctive, ownable |
| **ALPHEUS** ⭐ | The river Heracles diverted to wash out the **Augean stables** — myth's legendary "impossible clean made effortless by redirecting water" | clear; a built-in brand story |
| **VESTA** | Roman goddess of the hearth & **purity** (the Vestals kept the sacred flame pure) — AND a clean acronym (below) | ⚠️ clear in-space, but **Vestas** (wind-energy giant) is phonetically close — flag for counsel |
| **NAIAD** | Greek water-nymphs of springs & streams — water, freshness, cleansing | clear; uncommon, elegant |

#### ✅ Acronym angle — a coined word that encodes the abilities
| Name | Expansion | Notes |
|---|---|---|
| **VESTA** | **V**erified **E**xterior **S**urface **T**reatment & **A**nalysis | myth + acronym in one (see Vestas caveat) |
| **NAIAD** | **N**etworked **A**utonomous **I**nspection & **A**nalysis **D**rone | myth + acronym; ties to water |
| **VAST** | **V**erified **A**utonomous **S**urface **T**reatment | memorable, speaks to scale of buildings |
| **AVES** | **A**erial & **V**erified **E**xterior **S**ervices (aves = Latin "birds") | aerial-feel; screen it |
| **VERA** | **V**ision-**E**nabled **R**obotic **A**utonomy | clean, human-feel; common-ish, screen it |

#### ❌ Killed this round
Talos (talosmgt.com — direct AI robotic-cleaning competitor + PAL humanoid), Hygeia (Hygeia
Robotics, home cleaning), Aeris (iRobot's Aeris Cleantec air purifier), Orca (ORCA Hub
inspection UAVs + Orca Security).

#### Refined finalists (all lanes)
1. **KATHAROS** — literally "clean"; deep, ownable, on-theme.
2. **ALPHEUS** — the cleaning myth; a story baked into the name.
3. **VESTA** — myth **and** capability-acronym (mind the Vestas wind proximity).
4. Clean-Latin lane still standing: **NITIDO · NITOR · TERSO**.

---

### Round 6 — fresh batch (all ✅ clear in-space)

Preliminary scan, not TESS/registrar. Broad-usage caveats noted.

| Name | Story / meaning | Caveat |
|---|---|---|
| **ALCYONE** ⭐ | The nymph turned into the **halcyon** bird (kingfisher) — the *actual myth behind "halcyon."* Same serene-coastal feeling Kevin loved | ✅ **clear in-space** (no cleaning/robotics/drone use). ⚠️ used in OTHER classes: Alcyone Consulting (defense), Alcyone Technologies (IT — nearest to software), Alcyone Therapeutics (biotech) — coexists across classes but clear the IT one w/ counsel. `.com` likely gone; spelling/pronunciation friction (al-SY-uh-nee). Still cleaner than Halcyon (whose conflicts were IN cleaning+robotics+software) |
| **CANDOR** ⭐ | Latin *candeo* = "to shine, be bright-white" (root of incandescent/candid) **and** English *candor* = clarity/honesty — shine + transparency (fits the verify ethos) | Candrone (drone co) phonetically near-ish; real word = check distinctiveness |
| **SEQUANA** | Gaulish goddess of the river Seine — water, healing, cleansing; elegant deep-cut | Sequana Medical exists (pharma, diff. class) |
| **NIVEO** | Latin *niveus* = "snow-white, bright" — clean-white | Nivea (skincare) phonetic proximity |
| **VELA** | Constellation "the Sails" — nautical/coastal; also acronym-able | some tech use (Vela Games/fusion) |
| **AETHER** | The pure upper air/light the gods breathe — clarity + sky | crypto/tech use → class-42 crowded |

#### Two brilliant standouts
- **ALCYONE** — if you loved *Halcyon*, this **is** Halcyon's origin myth, and it's open. Keeps
  the calm/coastal/premium feeling with a name you can actually own.
- **CANDOR** — a rare double: it means both **bright/clean** (Latin root) and **clarity/
  honesty** (English) — literally your product (a bright clean) and your ethos (verified,
  transparent results). Memorable, real word, easy to say/spell.

#### Running finalist pool (getting strong — time to converge soon)
- **Myth:** ALCYONE · KATHAROS · ALPHEUS · SEQUANA
- **Coined-clean:** NITIDO · NITOR · TERSO · NIVEO
- **Meaningful real-word:** CANDOR
- **Myth + acronym:** VESTA · NAIAD

---

### Round 7 — catchy + descriptive + acronym (broadened)

Preliminary scan; broad-usage caveats noted. Killed this round: **Vertex** ❌ (Vertex Drone
Washing NE + Vertex C80 facade drone), **Vantage** ❌ (Vantage Robotics UAV), **Verity** ❌
(Verity AG drones).

#### ⭐ Acronym-words (a catchy word that ALSO encodes the company)
| Name | Acronym | Why it's catchy/descriptive | Availability |
|---|---|---|---|
| **VISTA** ⭐ | **V**erified **I**ntelligent **S**urface **T**reatment & **A**nalysis | "vista" = a commanding **view** — the drone's-eye, see-everything intelligence | ✅ clear in-space; common word broadly (class-42 software crowded) |
| **RIVA** | **R**obotic **I**nspection, **V**erification & **A**utonomy | also Italian *riva* = "shore/coast" (San Diego) | ✅ clear in-space (Riva yachts diff. class) |
| **SOLV** | **S**urface **O**bservation, **L**earning & **V**erification | sounds like "solve" — *we solve your cleaning* | ✅ clear in-space (Solv Health diff. class) |
| **CLARI** | **CL**eaning **A**nalysis, **R**obotics & **I**ntelligence | reads as "clarity" | ✅ clear in-space (Clari software diff. class) |
| **VESTA** | **V**erified **E**xterior **S**urface **T**reatment & **A**nalysis | myth (purity goddess) + acronym | ⚠️ Vestas (wind) proximity |

#### ✅ Catchy descriptive real-words (clear in-space)
| Name | Why |
|---|---|
| **SPRUCE** ⭐ | "spruce up" = to clean/tidy — literally what you do; friendly, easy to spell/say; also a tree (exterior/nature). Clear in-space (some home-svc/software use elsewhere) |
| **VISTA** | (above) — view/oversight |
| **CANDOR** | shine (Latin *candeo*) + clarity/honesty |

#### Top picks for "catchy + descriptive + ownable"
1. **VISTA** — real, catchy word (a commanding view) **and** a clean acronym of the abilities **and** clear in-space. Best all-rounder.
2. **SPRUCE** — the most literally descriptive + friendly ("we spruce up your building"); great consumer-facing service brand.
3. **RIVA** / **SOLV** — coined acronym-words, coastal/benefit-driven, ownable.
4. **CANDOR** — shine + transparency (the verify ethos).

> **Pool is now large (7 rounds).** Recommend converging: pick 3–5 favorites, then decide on
> **domain + trademark** — that's what actually narrows it, not more names.

---

### Round 8 — Japanese-origin (clean, precise, respected, forward)

Japan's brand of *cleanliness (seiketsu), precision craft (takumi), and continuous improvement
(kaizen)* maps perfectly to this company. Simple 2–3-syllable words travel well. Preliminary
scan; broad-usage caveats noted. (Note: authenticity/pronunciation matter when a US brand uses
a Japanese word — keep meanings accurate.)

#### ✅ Clear in-space + on-theme
| Name | 漢字 | Meaning | Say it | Why it fits |
|---|---|---|---|---|
| **MIGAKU** ⭐ | 磨く | to polish / shine / **refine** | mee-GAH-koo | double meaning: polish a surface **and** hone/improve (the learning loop). Clear (a language app uses it, diff. class) |
| **TAKUMI** ⭐ | 匠 | master artisan / craftsman | tah-KOO-mee | precision, mastery, best-in-class — the "respected craft" feeling. Clear in-space |
| **AKARI** | 明かり | light / brightness | ah-KAH-ree | clean, bright, elegant. Clear (Noguchi Akari lamps = design, diff. class) |
| **SUMI** | 澄み | clarity / clearness (of water & air) | SOO-mee | short, clean, purity of a clear result. Clear in-space |

#### Also on-theme (NOT yet screened)
Kiyo (清, pure/clean) · Yuki (雪, snow-white) · Haku (白, white/pure) · Hikari (光, light) ·
Hare (晴れ, clear sky) · Sae (冴, clear/sharp) · Sora (空, sky — ⚠️ OpenAI "Sora" conflict).
❌ **Kirei** (綺麗, clean) — taken by cleaning companies (Kirei Cleaning + Kao KireiKirei soap).

#### Top Japanese picks
1. **MIGAKU** — "to polish & refine": the shine you deliver **and** the self-improving loop. Poetic + on-theme.
2. **TAKUMI** — master craftsman: precision, respect, best-in-class. Strong, simple, cool.
3. **SUMI** — clarity/purity; shortest and cleanest to say.
4. **AKARI** — light/brightness; elegant, premium.

Kiyo / Yuki / Haku / Hikari also screened ✅ clear in-space.

#### Domain probes (fetched the .com — 2026-07-06)
| Domain | Result |
|---|---|
| migaku.com | ❌ taken — active language-learning SaaS (diff. industry; exact-name co + domain gone) |
| akari.com | ❌ taken — active massage-therapy practice (CA) |
| takumi.com | ⚠️ no content returned — almost certainly registered/premium |
| sumi.com | ⚠️ no content returned — almost certainly registered/premium |

**Takeaway:** the clean single-word `.com` is gone for all of these (true of nearly every
short real-word name we've hit). That does **not** kill a name — **trademark in your industry
(class 37/9) ≠ owning the exact .com.** Modern startups just use a modified domain:
`get<name>.com`, `<name>robotics.com`, `<name>.ai`, `fly<name>.com`. Decide on the *mark*
first; the domain is a solvable, secondary step.

#### ⭐ Japanese names that ALSO work as acronyms (all ✅ clear in-space)
| Name | 漢字 / meaning | Say it | Acronym of the company |
|---|---|---|---|
| **SEIKA** ⭐ | 成果 "results / achievement / fruition" | SAY-kah | **S**urface **E**xterior **I**nspection, **K**leaning & **A**nalysis — the meaning ("results") = your **verified-results** edge |
| **KAISEI** ⭐ | 快晴 "perfectly clear blue sky / fine weather" | kai-SAY | **K**leaning **A**utonomy, **I**nspection, **S**urface **E**xterior **I**ntelligence — clarity/clean-air |
| **NAMI** | 波 "wave" (water, coast) | NAH-mee | **N**etworked **A**erial **M**aintenance & **I**nspection — water + coastal (⚠️ NAMI = a mental-health nonprofit, diff. sector) |
| **SUMI** | 澄み "clarity" | SOO-mee | **S**urface **U**tility, **M**apping & **I**nspection |
| **HIKARI** | 光 "light" | hee-KAH-ree | **H**igh-altitude **I**nspection, **K**leaning, **A**nalysis, **R**obotics & **I**ntelligence |

❌ **Mirai** (未来 "future") — MiraiKikai makes autonomous window/solar-panel cleaning robots
(direct competitor) + Mirai Robotics; also the "Mirai" botnet association. Avoid.

**Best Japanese-acronym picks:** **SEIKA** ("results" + full pipeline acronym) and **KAISEI**
("clear sky" + acronym) — meaning *and* mechanics aligned.

---

### ★ THE FINAL 3 (feel them as real brands)

Three distinct directions — pick the *feeling*, then clear it with counsel + a registrar.

#### 1. SEIKA — *"the proof is in the clean"*
- **成果 (SAY-kah)** = results · achievement · fruition. Acronym: **S**urface **E**xterior
  **I**nspection, **K**leaning & **A**nalysis.
- **Positioning:** We don't just clean — we *prove* it. The name literally means "results,"
  which is your verify-and-show-the-ROI edge.
- **Taglines:** "Results you can see." / "Cleaning, measured." / "The proof is in the clean."
- **Family:** Seika Air (drones) · Seika Ground (concrete/Lavo) · Seika Robotics (parent).
- **Domain path:** getseika.com · seika.ai · seikarobotics.com. **TM:** clear in-space; screen software class.

#### 2. TAKUMI — *"precision, perfected"*
- **匠 (tah-KOO-mee)** = master craftsman / artisan.
- **Positioning:** The mastery of a lifelong craftsman — delivered by robots. Precision,
  respect, best-in-class. Premium, confident, forward.
- **Taglines:** "Precision, perfected." / "The master's clean." / "Mastery, at altitude."
- **Family:** Takumi Air · Takumi Ground · Takumi Robotics.
- **Domain path:** takumirobotics.com · gettakumi.com · takumi.ai. **TM:** clear in-space; common word (screen).

#### 3. VISTA — *"every surface, in view"*
- **VIS-ta** = a commanding view. Acronym: **V**erified **I**ntelligent **S**urface
  **T**reatment & **A**nalysis.
- **Positioning:** The intelligence that *sees* every surface — a commanding view of your
  building's condition. Catchy English word + full-capability acronym.
- **Taglines:** "Every surface, in view." / "See it clean." / "The whole picture, spotless."
- **Family:** Vista Air · Vista Ground.
- **Domain path:** vistarobotics.com · flyvista.com. **TM:** clear in-space; software class crowded (Vista Equity etc.).

**Strong alternates if none click:** KAISEI (clear-sky + acronym) · MIGAKU (polish/refine) ·
CANDOR (shine + clarity) · NITIDO (Latin "clean").

**Decision gate:** pick 1–2, then (a) registrar check for a workable domain, (b) USPTO
TESS + counsel in classes 37 (cleaning) + 9/42 (robotics/software). That clears it — not more names.

---

### Pressure test — SEIKA (⚠️ FAILS)

- **Linguistic trap:** romaji "Seika" maps to many kanji; the **dominant company-name reading
  is 製菓 "confectionery"** (Meiji Seika, Kameda Seika, Marukawa Seika, Imuraya Seika all =
  "○○ Confectionery Co."), and 青果 = "produce." Intended 成果 "results" is NOT the default —
  "Seika Robotics" could read as *"Confectionery Robotics"* to a Japanese speaker.
- **Crowded + domain gone:** Seika Corporation (TSE-Prime machinery co) owns **seika.com**;
  also Sumitomo Seika (chemicals), Meiji Seika Pharma. "Seika" ≈ generic Japanese biz suffix.
- **Verdict:** drop. Clever acronym, shaky word.

#### Meaning-integrity re-rank of the Japanese finalists (romaji-homophone check)
| Name | Reads reliably as intended? |
|---|---|
| **TAKUMI** 匠 master craftsman | ✅ unambiguous, positive — **survives** |
| **MIGAKU** 磨く to polish/refine | ✅ clear verb — **survives** (migaku.com taken) |
| KAISEI | ⚠️ 快晴 "clear sky" but also 改正 "legal revision" / 改姓 "surname change" |
| SUMI | ⚠️ 澄み "clarity" but also 墨 "ink" / 隅 "corner" |
| NAMI | ⚠️ "wave" but common name + NAMI nonprofit |

**Revised Japanese lead: TAKUMI** (unambiguous "master craftsman"), with **MIGAKU** as the
poetic alternate. Non-Japanese hedge with no meaning-risk: **CANDOR** (shine + clarity) or **NITIDO**.

---

### Pressure test — TAKUMI (⚠️ partial pass)

- **✅ Meaning holds up:** 匠 reliably = "master craftsman" — no homophone trap (passes where
  Seika failed). Easy to say.
- **⚠️ Crowded, worst conflict in-lane:** **Takumi Precision / Takumi CNC** — global CNC
  machine-tool maker (Taiwan/Hurco, since 1988; aerospace/automotive/semiconductor; owns
  takumi.com.tw, takumiusa.com, takumicnc.eu). Precision industrial automation = **adjacent to
  robotics** → real likelihood-of-confusion risk in machinery/hardware classes (7/9), exactly
  where PROPWASH's identity/IP sit. Also common broadly (knives, steakhouses, golf; Initial D).
- **Verdict:** usable for the cleaning-**service** brand (class 37 clearer), **risky for the
  robotics/tech identity**. Domain gone. Counsel must weigh the Takumi CNC conflict.

#### What two pressure tests reveal
Seika ❌ (linguistic trap), Takumi ⚠️ (robotics-adjacent conflict) — **real-word/common names
keep cracking under scrutiny.** The pressure-resistant options are **coined / less-common**:
- **MIGAKU** (磨く "polish/refine") — clean meaning, a *verb* rarely used as a company name →
  least crowded Japanese option; only ding = migaku.com (edtech, diff class).
- **NITIDO** (Latin "clean") — coined; no meaning trap; clear in-space; coined = strongest,
  least-crowded trademark. **Likely most defensible overall.**

**Emerging conclusion:** if you want a name that *survives* legal scrutiny, favor a coined
name (NITIDO) or the low-crowding Japanese verb (MIGAKU) over the popular real-words.

---

### Pressure test — CANDOR (⚠️ partial pass)

- **✅ Meaning clean:** honesty/transparency + Latin *candeo* "to shine/be bright-white" — no
  trap, easy to say/spell, fits the verify-ethos.
- **✅ Clear in cleaning/robotics-hardware space.**
- **⚠️ Crowded in software/AI (class 42):** Candor Technology (AI mortgage underwriting),
  Candor Cloud (AI governance), Candor (YC 2025, AI gov-funding), Candor.co (careers). Since
  PROPWASH *is* an AI company, real likelihood-of-confusion in the software class — mirror of
  Takumi (whose conflict was hardware/robotics). Domain candor.com/.co gone.
- **Verdict:** easy, meaningful, clear in cleaning — but crowded in AI/software. Partial pass.

#### Three pressure tests, three cracks — the pattern is decisive
| Name | Result | The crack |
|---|---|---|
| SEIKA | ❌ | reads as "confectionery"; seika.com = Seika Corp |
| TAKUMI | ⚠️ | Takumi CNC — conflict in hardware/robotics (your IP class 7/9) |
| CANDOR | ⚠️ | multiple Candor AI/software brands (your class 42) |

**Every popular real-word cracks on an adjacent class.** Survivors = low-crowding:
**MIGAKU** (rare-as-company-name JP verb) and **NITIDO** (coined = strongest mark).
**Recommendation:** converge on **NITIDO** (most defensible) or **MIGAKU** (meaningful +
low-crowding); take the top 2 to a trademark attorney — preliminary web scanning has done its job.
- [ ] Pick 2–3 finalists.
- [ ] USPTO TESS + common-law search (counsel) in classes 37 + 42.
- [ ] Confirm `.com` (short one-words like Facet/Lustre are often taken/expensive).
- [ ] Check social handles + that it doesn't overclaim (§5/§7).
- [ ] Decide keep-vs-rename; if renaming, update repo, docs, and the visor branding.

### Pressure test — VESTA (❌ HARD FAIL — worst result of any candidate)

*Screened 2026-08-16. Preliminary web scan, not TESS/counsel.*

Round 5 flagged Vesta only for phonetic proximity to **Vestas** (wind energy). That was the
least of it. Vesta is the first candidate to fail in **all three** of our classes at once.

#### ❌ Class 37 (cleaning services) — DIRECT HIT, and more than one

| Conflict | What they do | Severity |
|---|---|---|
| **Vesta Wash** — `vestawash.com` | **14+ years**, DE / MD / PA. Soft-washing **roofs, siding, stucco, decks, pavers, concrete**; commercial up to 10 storeys and 50-building portfolios | 🔴 **Fatal.** This is our exact service line, in our exact naming pattern |
| **Vesta Pro Wash** — `tampasoftwashing.com` | Tampa FL. Pressure + soft washing, window cleaning, commercial janitorial | 🔴 Second independent user, same class |
| **Vesta Property Pro** — `vestapropertypro.com` | Wesley Chapel FL. Commercial cleaning, power washing, junk removal | 🟠 Third |

**Vesta Wash is the single most damaging conflict any candidate has hit.** It is not an
adjacent-class coexistence question — it is an incumbent exterior soft-washing company whose
surface list (roof, siding, stucco, deck, concrete) reads like our own §9 treatment matrix.

Note the specific trap: our naming pattern pairs the mark with "wash". **Naming the company
Vesta and keeping any "wash" in the brand family literally reproduces an existing company's
name.**

#### ❌ Class 9 (robotics / hardware)

- **Amazon "Vesta"** — Amazon's home-robot programme, named for the same goddess, using
  cameras and computer-vision navigation. Amazon is not a party you coexist with by accident.

#### ❌ Class 42 (software / AI)

- **Vesta.AI** — property-management automation and ML. *Adjacent to our own customer.*
- **Vesta AI Labs**, **Vesta AI** (consulting), **vesta.com** (AI agents across workflows).

#### ⚠️ Phonetic (the original flag, still live)

- **Vestas Wind Systems** — global wind-energy company. Renewables adjacency matters given
  the solar wedge.

#### Verdict

**❌ Kill it.** Not "clear with counsel" — kill it. Every other finalist cracked on exactly one
adjacent class; Vesta cracks on the **primary** class with an incumbent doing the same work, and
then again on both secondary classes.

The Round-5 entry recorded it as "clear in-space" — that scan was not deep enough. Corrected here.

#### Four pressure tests, and the pattern is now unambiguous

| Name | Result | The crack | Class hit |
|---|---|---|---|
| SEIKA | ❌ | reads as "confectionery"; seika.com = Seika Corp | meaning |
| TAKUMI | ⚠️ | Takumi CNC — hardware/robotics | 7/9 |
| CANDOR | ⚠️ | multiple Candor AI/software brands | 42 |
| **VESTA** | ❌❌ | **Vesta Wash + Vesta Pro Wash (cleaning), Amazon Vesta (robots), Vesta.AI (software)** | **37 + 9 + 42** |

Evocative real-words are not merely crowded — in *this* industry they are **already in use by
exterior-cleaning companies**, because the pool of "clean / pure / bright" words is exactly what
every power-washing business in the country has already reached for.

**This settles it: stop testing real-words.** The remaining candidates are the ones that were
never going to be reached for by a regional pressure-washing outfit:

- **NITIDO** — coined from Latin *nitidus* "clean/bright". No meaning trap, no in-space use
  found, and a coined mark is the strongest kind. **Most defensible.**
- **MIGAKU** — 磨く "to polish / refine". A Japanese *verb*, almost never used as a company
  name; only ding is migaku.com (edtech, different class).

**Recommendation unchanged and now firmer: take NITIDO and MIGAKU to counsel. Do not spend more
cycles on real-words.**

---

### Pressure test — NITIDO (❌ FAIL) and MIGAKU (✅ PASS) + drone-cleaning sweep

*Screened 2026-08-16. Preliminary web scan, not TESS/counsel.*

#### ⚠️ Correction: NITIDO was never "coined"

Earlier rounds recommended NITIDO on the grounds that it was **coined**, and therefore the
strongest possible mark. **That was wrong.** *Nítido* is a common, everyday adjective in
Spanish, Portuguese and Italian meaning "clean / clear / sharp."

That single error inverts the recommendation, because it means the name is exactly what every
Spanish-speaking cleaning business in the US reaches for first.

#### ❌ NITIDO — class 37 is already full

| Conflict | Where | Note |
|---|---|---|
| **NITIDO CLEANING SERVICES, LLC** | Murray, UT | D&B-listed entity, exact name |
| **Cleaning by NÍTIDO** — `cleaningbynitido.com` | Chicago, IL | commercial cleaning / sanitization |
| **Nitido & Pro Cleaning Services** | Coral Springs, FL | residential + commercial |
| **Nitido Cleaning LLC** | Three Bridges, NJ | |
| **Nitido 031 Cleaning Services** | Bronx, NY | |
| **Nítido / Nítidos Cleaning Service** | Instagram | two more |
| `nitidosolutions.com` | Anthem Home & Carpet | commercial cleaning |

Seven-plus independent users **in the primary class**. None are exterior/drone specialists, so
it is less acutely damaging than Vesta Wash — but a mark that common is weak, hard to police,
and cannot be owned.

**Class 9 / 42 adjacency:** **NIDO SYSTEM / NIDO.AI** (Veneto, Italy) — "a distributed Physical
AI platform connecting autonomous drones, docking stations and robotic nodes into one
coordinated monitoring network," EASA-compliant, TRL 8. Not the same string, but one letter and
a near-homophone away, **in precisely our technical space**. That is the kind of adjacency
counsel flags immediately.

**Verdict: ❌ kill NITIDO.** Not coined, crowded in class 37, and shadowed by NIDO.AI in class 9/42.

#### ✅ MIGAKU — the first candidate to survive

| Class | Finding |
|---|---|
| **37 — cleaning** | ✅ **Nothing found.** No cleaning, pressure-washing or exterior-services company under this name |
| **9 / robotics + drones** | ✅ **Nothing found.** Absent from the drone-cleaning landscape entirely |
| **9 / 41 — software** | ⚠️ **Migaku Inc.** — language-learning app (iOS, Android, web), active press. The only real conflict |
| **42 — AI/software** | ⚠️ same entity; the app markets AI-driven features |

**磨く (mi-GA-ku), "to polish / to refine."** The double meaning still holds and is still the best
fit of any candidate: you *polish a surface*, and the learning loop *refines* the prescription.

**The one thing to clear:** Migaku Inc. sits in education/consumer-app territory (class 41, and
class 9 as software). PROPWASH is class 37 services plus class 9 hardware — genuinely different
goods and channels, so coexistence is plausible. But we *are* also a software company, so this
is the same shape of question that partially sank Candor. **Counsel decides this one; it is a
real question, not a formality.**

**Not yet screened:** Japanese-market use of 磨く on cleaning products. Common verb, likely
some usage. Matters only if there is ever a JP filing.

**Verdict: ✅ proceed to counsel.** Cleanest result of any name tested — the only candidate with
*nothing* in class 37 and *nothing* in drones/robotics.

---

#### 🔍 Drone-cleaning landscape sweep (new — none of the earlier rounds checked this)

Every previous round screened "cleaning" and "robotics" generically. Nobody checked the
**drone-cleaning** niche, which is where our actual competitors live.

**The market has real incumbents and real money:**

| Company | Position |
|---|---|
| **Lucid Bots** (Charlotte, NC) | Sherpa + Lavo. **$20M Series B, ~$34M total. 400+ active operators across 40+ states, >$75M in operator revenue.** Our assumed hardware vendor is also the category leader |
| **Spinoff Robotics** | Tethered aerial robots — façade cleaning, **solar panel washing**, inspection. Closest to our solar wedge |
| **CleanHeights Robotics** (Singapore) | Autonomous cleaning robots for facility management |
| **Apellix** | Tethered industrial power-wash + coating |
| **DRONEWASH+** (2021) | Nationwide drone exterior cleaning, **franchise model** |
| **SkyWash Drones** (Houston, 2022) | Window, façade, roof |
| Drone Clean USA · Drone Force USA · DroneWorx Pro Washing · Pressure Pros Wash · Drone Powered Solutions · Sun Brite Services | Regional service operators |

**Finding 1 — the "—WASH" suffix is crowded in our exact niche.** DroneWash+, SkyWash,
DroneWashingEquip, DroneWorx Pro Washing, Pressure Pros Wash. The `<X>WASH` construction is the
default naming move in drone cleaning, which weakens **any** name built that way — including the
proposed **SLABWASH** ground line.

**Finding 2 — PROPWASH itself screens clean here.** No drone-cleaning or pressure-washing company
under that name surfaced. And "prop wash" is an **aviation term of art** (the airflow behind a
propeller) that is *arbitrary* applied to cleaning services — which is a genuinely favourable
trademark posture in class 37, better than any of the descriptive candidates we spent eight
rounds generating.

**Finding 3 — Lucid Bots is the category leader, not a neutral supplier.** 400+ operators and
$75M of operator revenue means they have every incentive to keep autonomy in-house. This is
evidence *for* the Path-A-first posture in CLAUDE.md §7, not against it.

#### Where this leaves the naming exercise

| Name | Class 37 | Drones/robotics | Software/AI | Verdict |
|---|---|---|---|---|
| SEIKA | — | — | — | ❌ meaning trap |
| TAKUMI | ✅ | ❌ Takumi CNC | ⚠️ | ⚠️ |
| CANDOR | ✅ | ✅ | ❌ several | ⚠️ |
| VESTA | ❌❌ Vesta Wash | ❌ Amazon Vesta | ❌ Vesta.AI | ❌❌ |
| NITIDO | ❌ 7+ users | ⚠️ NIDO.AI | ⚠️ | ❌ |
| **MIGAKU** | **✅ clear** | **✅ clear** | ⚠️ Migaku Inc. (edu app) | **✅ best** |
| **PROPWASH** | **✅ clear** | **✅ clear** | ✅ | **✅ + already ours** |

**Recommendation: the two real candidates are MIGAKU and PROPWASH — and PROPWASH is free.**

After nine rounds, the incumbent screens as well as anything we generated, is arbitrary rather
than descriptive in its class, and is already in the repo, the docs and the visor. The honest
advice is to **keep PROPWASH** and take **MIGAKU** to counsel only if you want the option.

The one thing worth changing regardless: **drop SLABWASH for the ground line.** The "—wash"
suffix is the crowded part, and doubling down on it is the weakest available move.

---

### Log
| Date | Note | By |
|---|---|---|
| 2026-07-06 | Exploration shortlist drafted; recommend keep PROPWASH or explore Facet / Downwash | Claude (advisory) |
| 2026-08-16 | **NITIDO ❌** — not coined (common ES/PT/IT word); 7+ cleaning cos in class 37; NIDO.AI shadows it in drones. **MIGAKU ✅** — clear in cleaning AND drones; only conflict is Migaku Inc. (language app). Drone-cleaning sweep added: "—wash" suffix is crowded in-niche (DroneWash+, SkyWash), but **PROPWASH itself screens clean and is arbitrary in class 37**. Recommend keep PROPWASH; drop SLABWASH. | Claude (advisory) |
| 2026-08-16 | **VESTA pressure-tested → ❌ hard fail.** Vesta Wash (14-yr exterior soft-wash co, DE/MD/PA) is a direct class-37 incumbent; plus Amazon Vesta (robots) and Vesta.AI (software). Round-5 "clear in-space" was wrong and is corrected. Converge on NITIDO / MIGAKU. | Claude (advisory) |

<a id="docsdecisionspayloadbuildspec"></a>

---

# Payload Build Spec — the complete wash kit

> **Source file:** `docs/decisions/PAYLOAD_BUILD_SPEC.md`

## Payload Build Spec — the complete wash kit

> **Rev B · 4 Sep 2026.** Supersedes Rev A (airborne payload only).
> Aircraft, airborne payload, ground rig, water train and chemistry — one costed kit.
>
> Prices are public list, **subject to quote — none of this is a bid.** Pressure and dwell
> values come from `prescriptions/surface_treatment_v1.json` and remain **uncalibrated
> starting assumptions** (CLAUDE.md §9). Nothing here is legal, aviation-regulatory or
> insurance advice.
>
> Rendered version with drawings: `samples/payload_build.html`

---

### 0. The three answers

#### 0.1 Which aircraft — and why the bigger one is worse

**Inspired Flight IF1200A.**

The counter-intuitive part: the Freefly Alta X advertises **33.2 lb** of payload against the
IF1200A's **19.1 lb**, and it is still the wrong choice — because the Alta X only reaches that
number *above* the 55 lb Part 107 ceiling.

#### 0.2 No second rig for foam — but a second water path

Two findings got tangled together in the question.

- **Foam:** at soft-wash pressure you cannot make clinging foam with hardware. Venturi foam
  cannons need roughly **1,000+ psi**; we run **60–100 psi**. Cling comes from the chemistry —
  a thickened surfactant package. **A purchase-order change, not an equipment change.**
- **The real split is DI vs. detergent**, driven by solar, not glass. A second hose would cost
  the entire payload budget, so: **one hose, two sources, and a sequencing rule.**

#### 0.3 Inside houses — no

The IF1200A is 1.2 m across the frame, ~1.6 m across the props. There is a real indoor market,
but it is **dry work** on a **small caged aircraft with visual-inertial navigation**, sharing no
parts with this build. Separate program.

---

### 1. The aircraft

Part 107 caps the **whole aircraft** at 55 lb / 25 kg — airframe, batteries, payload, everything.
So the only payload number that means anything is **25 kg minus what the aircraft weighs with the
batteries it needs to be useful.** Advertised "max payload" figures are quoted at maximum gross
takeoff weight, which for larger airframes sits well above the Part 107 line.

| Aircraft | Airframe + batteries | Usable under Part 107 | Advertised max |
|---|---|---|---|
| **IF1200A** (hexacopter) | 16.3 kg | **8.66 kg / 19.1 lb** | 28.7 lb with certification |
| Alta X (quadcopter) | 19.8 kg | ~5.20 kg | 33.2 lb @ 34.9 kg MTOW |

**The smaller aircraft gives 66% more usable payload.** Inspired Flight publishes 19.1 lb as its
Part 107 figure, meaning they have already done this subtraction. A tethered wash payload needs
4–5 kg, so 8.66 kg is comfortable and 5.2 kg is not.

#### 1.1 Deliberately not on the list: prop guards

The instinct near a wall is to cage the props. On a 1.2 m hexacopter a full guard set is
**0.8–1.5 kg** — 10–17% of the entire payload budget — and it buys less than it appears to,
because a guard that touches stucco still upsets the aircraft.

**Standoff is the better control:** the co-aligned rangefinder feeding a deterministic Tier-1
minimum-distance hold (CLAUDE.md §2). A safety check that cannot be talked out of its job by an
agent, and it weighs nothing.

`TODO(PROPWASH): revisit if field data shows contact incidents.`

---

### 2. The airborne payload

#### ⚠️ The constraint that shapes everything: the hose is the payload

Equipment comes to **4.10 kg**, leaving **4.56 kg** of the aircraft's 8.66 kg limit. A 3/8" hose
full of water weighs **0.211 kg per metre**.

**That is 21 metres of unsupported hose and no more.** At 40 m the hose alone is 8.4 kg — it
exceeds the entire payload before you attach a single fitting.

**So the ground tether-management system is a load-bearing structural element, not an accessory.**
It must carry the hose weight and present near-zero tension at the aircraft.

| Hose ID | Charged mass | Max unsupported @ 4.56 kg |
|---|---|---|
| 1/2" | 0.347 kg/m | 13.1 m |
| **3/8"** | **0.211 kg/m** | **21.6 m** |
| 5/16" | 0.160 kg/m | 28.5 m |

#### 2.1 How the gun attaches — forward boom, not drop bracket

A drop mount puts the nozzle **inside the rotor downwash**, which atomises the spray and blows it
back over the aircraft, and it sets a **90 mm moment arm** below the CG that the flight controller
must trim against continuously. A **340 mm forward boom** pushes the nozzle past the rotor disc and
cuts the arm to about **28 mm**.

Jet reaction force: `F(lbf) = 0.0745 × gpm × √psi` → ~12 N at our pressures. **It is the moment,
not the force, that costs control authority.**

#### 2.2 The mounting plate

One carbon or aluminium belly plate bolts to the aircraft's **Universal Payload Interface**
(M600-compatible spacing). Everything else hangs off that plate — so the plate, not the airframe,
is the part you fabricate.

- Wet components sit **forward** along the water path: clamp → solenoid → flow sensor → boom → gun.
- **Companion computer aft in an IP66 enclosure**, as far from the nozzle and its drift as the
  plate allows.
- **Rangefinder co-aligned with the spray axis**, so the standoff it measures is the standoff the
  prescription specified.
- **The hose clamp is deliberately not on this plate.**

#### 2.3 ⚠️ The single most important fabrication rule

**Hose tension must never pass through the gimbal or the payload plate.** It goes straight into the
airframe's structural rail via its own clamp, with a slack service loop between the clamp and the
gun.

Get this wrong and every hose tug becomes a torque on the gimbal servo and a bending load on your
mounting bolts — the two things most likely to fail in flight.

---

### 3. Where the load actually goes

The powered reel — **not the aircraft** — carries the hose. It pays out and takes up to hold
near-zero tension at the drone, which is what makes working height independent of payload. At the
aircraft the hose lands on a clamp bolted to the **airframe rail**; only a slack loop continues to
the gun, so gimbal motion and hose motion are mechanically decoupled.

---

### 4. The fluid system — where the foam question lands

One aircraft, one hose, four surfaces with incompatible requirements. The design problem is not how
to make foam; it is **how to keep detergent away from the solar panels** when everything shares a
single line.

```
  RO ──▶ DI resin ──▶ DI TANK ──┐
                                 ├──▶ 3-WAY VALVE ──▶ PUMP ──▶ PROPORTIONER ──▶ PSM ──▶ hose ──▶ gun
              BULK TANK ────────┘                                  ▲                    └─ TDS check point
              (tap · roof + walls)                             chem drum
                                              └──────── SHARED WETTED VOLUME ────────┘
                                          once detergent is in here, it is in here
```

**THE RULE: DI-only zones run first, every day — before chemistry has ever entered the shared
volume.** Reverse that order and the only way back is a verified flush (§4.3).

Switching source is trivial; the shared volume downstream of the proportioner is not. Detergent
that has been through the pump, hose, boom and gun is still there on the next zone, which is why
**sequence, not plumbing, is the primary control.**

#### 4.1 Why solar drives this and glass does not

- **Glass wants 0 ppm so it dries without spots.** Get it wrong and you get water spots — a
  cosmetic failure, visible, and fixable by doing it again.
- **Solar wants 0 ppm *and* zero surfactant, because residue costs the customer generating
  capacity.** Get it wrong and you have measurably degraded the asset you were paid to improve —
  and it is invisible until someone reads the inverter.

That asymmetry is why the sequencing rule is written around solar. It is also the one surface where
the failure is **silent**, which is exactly the case verification exists for: the Post-Clean agent
should be reading **panel output**, not just thermal residual.

`TODO(PROPWASH): inverter API integration — needs Kevin's call on scope.`

#### 4.2 Enforce the order in software, not in a checklist

This is a scheduling constraint, and the Supervisor agent already sequences zones. Encoding it there
makes it **structural rather than procedural** — the work order cannot be emitted in an order that
puts a chemical zone ahead of a DI-only zone. A laminated card in the truck is not the same
guarantee, and it is the sort of rule that gets skipped at 4pm on the third job.

#### 4.3 If you do have to switch back mid-day

| Segment | Volume | ×3 flush |
|---|---|---|
| 40 m of 3/8" hose | 2.85 L | 8.6 L |
| Pump, proportioner, PSM, boom, gun | ≈0.6 L | 1.8 L |
| **Total** | **≈3.5 L** | **≈10.4 L · 2.7 gal · ~30 s at 6 gpm** |

A flush is **cheap** — the reason to sequence instead is not cost, it is that a flush is only as
good as its verification. Catch the discharge in a bucket and read it: **under 10 ppm before you
point the gun at a panel.** A $25 handheld TDS meter is the whole quality system here.

---

### 5. Foam, and why you are not going to make any

| Method | What it needs | Verdict |
|---|---|---|
| Venturi foam cannon | ~1,000+ psi to draw air through the orifice | ✗ We run 60–100 psi. It will dribble |
| Compressed-air injection (CAFS) | A second line up the tether, plus a compressor | ✗ Air line is more hose weight — the entire constraint |
| Onboard mini-compressor | Compressor + power + plumbing on the aircraft | ✗ ~1 kg of your 4.56 kg, to make foam |
| **Thickened surfactant chemistry** | A different drum | **✓ Cling from the formulation. No hardware, no weight** |

**Buy the cling, don't build it.** Soft-wash surfactants are formulated for exactly this — cling and
dwell at low pressure, because the chemistry is doing the work and it has to stay on a vertical
surface long enough to do it. It also removes a failure mode: a foamer is one more wetted component
to cross-contaminate and flush before you touch a panel.

---

### 6. Water — the part that will surprise you

Two of four surfaces need deionised water, and **Carlsbad has some of the least convenient feed
water in the state for making it.** Published figures put local TDS at roughly **474–611 ppm** with
hardness around **18 grains per gallon** — "very hard." DI resin capacity scales inversely with feed
TDS.

| Configuration | Feed TDS | Gal per refill | Resin cost/gal | 120-gal job |
|---|---|---|---|---|
| DI resin alone | ≈550 ppm | ~150 | ~$0.66 | ~$79 |
| **RO → DI resin** | ≈15 ppm | ~5,500 | ~$0.02 | ~$2 |

#### ⚠️ The RO stage pays for itself in about a month

RO removes 95–99% of dissolved solids *before* the resin sees them, extending resin life roughly
**30×** on Carlsbad water. On one 120-gallon solar job that is a **~$77 swing**; at three jobs a week
it is on the order of **$11,000 a year** in resin you would otherwise throw away.

**Treat the RO stage as mandatory, not an upgrade.** These are published averages — **put a $25 TDS
meter on your own tap before you buy anything.**

#### 6.1 RO is slow, so the tank is the real equipment

A 300–600 GPD RO unit produces **0.2–0.4 gpm**. Your gun consumes **4–8 gpm** — twenty times faster
than you can make water. You never make DI water at the job; **you make it overnight at the shop and
haul it.**

| Job type | DI needed | Tank | Water weight | Vehicle |
|---|---|---|---|---|
| Residential — array + glass | 60–90 gal | 100 gal | 834 lb | 3/4-ton bed or light trailer |
| Small commercial | 150–250 gal | 275 gal | 2,294 lb | Braked trailer |
| Commercial solar farm | 500–1,000 gal | — | 4,170–8,340 lb | ⚠️ Needs on-site high-flow RO. Phase 2 |

**Water is the heaviest thing you own.** A 275-gallon tote outweighs the entire rest of the kit,
aircraft included. **Commercial solar farms do not close on this configuration** — a 0.4 gpm RO
cannot feed a 1,000-gallon day, and hauling it is four tons.

---

### 7. The four surfaces, and what each actually asks for

| Surface | Pressure | Water | Chemical | Tip | Limiting factor |
|---|---|---|---|---|---|
| Composite shingle roof | 5.0–6.5 bar | Tap | Degreaser *or* biocide (§8) | 40° fan, 0.5 mm | Dwell. Industry soft wash is 15–20 min, our table says 35 s |
| Solar panel | 1.5–2.0 bar | ⚠️ **DI only** | **None. Ever.** | 25° narrow, 0.35 mm | Residue and cell damage. Hard ceiling in the safety layer |
| Window glass | 2.0–2.4 bar | **DI** | Ammonia-free | 20° jet | ⚠️ No agitation — see below |
| Stucco / gutter | 3.5–7.0 bar | Tap | Degreaser (+ solvent, gutters) | 40–45° fan, 0.6–0.7 mm | Overspray and containment |

#### ⚠️ The honest limit on glass: a drone cannot scrub

Water-fed-pole window cleaning works because of the **brush**. The pure water rinses; the bristles
break the bond. **You have no brush**, so on glass you are relying on chemistry, dwell and rinse
alone.

**That is fine for light atmospheric soil and useless on bonded soil** — hard-water spotting,
construction film, mineral etch. Competitors market "streak-free"; treat that as a claim to verify
on your own glass before you put it in a quote. Contact cleaning means a drone that pushes against
the building — a force-control problem on a different aircraft. **Not year one.**

#### 7.1 One head, two tips

Four surfaces want four tips, and hand-changing nozzles per zone destroys the makespan the scheduler
is built to protect. A full rotating selector costs **0.50 kg** of a 4.56 kg budget. The cheaper
answer covers the spread: **a two-tip head with a solenoid selector, about 0.20 kg** — a 25°/0.35 mm
for solar and glass, and a 40° fan for roof and stucco. The gutter case falls back to a hand change,
which is once a job, not once a zone.

---

### 8. ⚠️ The regulatory fork you have not priced yet

Everything so far assumed Part 107. **Dispensing changes that.** FAA Part 137 governs agricultural
aircraft operations, which the FAA defines to include dispensing **"economic poisons"** from an
aircraft, manned or unmanned — and the FAA's own guidance frames it as covering dispensed substances
**including disinfectants**.

Sodium hypochlorite on a roof is not being used as a soap. **It is being used to kill gloeocapsa
magma** — that is pest control, and a reasonable reading puts it inside Part 137. Many drone
soft-wash operators already hold the certificate.

| | Path A — no biocide | Path B — biocide |
|---|---|---|
| Chemistry | DI, surfactant, degreaser | Sodium hypochlorite + surfactant |
| Roof result | Removes surface soil. **Algae returns fast** | Kills the organism. Industry-standard result |
| FAA | Part 107 | **Part 137 AAOC — 90–180 days** |
| California | — | DPR applicator licensing + county Ag Commissioner registration |
| Insurance | Easier | Chemical application changes the conversation |
| Time to first roof job | Immediate | **Two to six months** |

**Why this is the decision, not a footnote.** It sets your **launch date**. If roofs need Path B, the
roof product cannot ship until the certificate does — which argues for opening on **solar, glass and
scan-only work**, all Path A, and adding roofs when the paperwork lands.

It also resolves the open dwell question in `prescriptions/surface_treatment_v1.json`: the 35 s roof
dwell is only defensible with a biocide doing the work. Path A roofs need the full 15–20 minute soak,
which changes the schedule, the water volume and the tank sizing above.

`TODO(PROPWASH): needs an aviation attorney, not a search result.`

---

### 9. Indoor work — the answer, and the better version of the question

| Blocker | Why it does not resolve with a smaller payload |
|---|---|
| **Size** | 1.2 m frame, ~1.6 m across props. Residential rooms and stairwells are not survivable geometry |
| **Navigation** | No GPS indoors. Position hold needs VIO or LiDAR SLAM — a different autonomy stack, not a payload |
| **Downwash** | Outdoors the air leaves. Indoors it recirculates, lifting dust and pushing overspray back through the room |
| **Liquid** | Water near furnishings, electrical and drywall. The liability question that ends the conversation with an underwriter |
| **Tether** | A charged hose through a doorway is a snag path with no clear line back to the reel |

#### The market you probably meant is real — and it is dry

**High interior volumes** — warehouse and hangar ceilings, atriums, gymnasiums, stadium concourses,
church naves — are genuine and underserved, currently served by scissor lifts and scaffolding at real
cost. In some jurisdictions overhead **combustible-dust removal is a fire-code obligation**, which
means a budget line and a schedule.

But that work is **dusting and blow-down, not washing**: no water, no tether, no chemistry. Different
aircraft (small, caged, VIO-navigated), different payload, different sale.

**It shares one thing with this build, and it is the valuable thing:** the map, the per-surface model
and the verification loop are method, not plumbing. They port. The hardware does not.
**Phase 3, separate program.**

---

### 10. The complete kit

#### A · Aircraft

| # | Item | Note | Cost |
|---|---|---|---|
| A1 | **IF1200A airframe** | Blue + Green UAS. PX4. 43 min. ⚠️ Recently listed sold out — ask about lead time first | $32,000 |
| A2 | **GCS + battery sets** | Bundle delta. 3+ sets for a field day | $8,000–$20,000 |
| A3 | **Skydio X10D scout** | The mapping half of the loop. FLIR Boson+ radiometric, 30 mK | $16,000 |
| A4 | Scout batteries, case, controller | | $4,000–$6,000 |
| A5 | Corrosion kit + rinse station | Conformal coat, dielectric grease, stainless, freshwater rinse | $500–$1,000 |
| A6 | Spare arms, motors, props | Near-surface work eats props | $1,500–$3,000 |
| | **Aircraft subtotal** | | **$62,000–$78,000** |

#### B · Airborne payload — 4.10 kg

| # | Part | Spec / note | Mass | Cost |
|---|---|---|---|---|
| B1 | **Soft-wash gun / lance** | Rated ≥20 bar (4× our ceiling). Brass or SS wetted parts | 1.20 kg | $200–$400 |
| B2 | **Single-axis pitch gimbal** | Pitch only — the aircraft yaws | 0.60 kg | $300–$600 |
| B3 | **Boom, ~340 mm** | CF tube 25 mm OD. Length set by rotor-disc clearance | incl. | $80 |
| B4 | **Belly plate** | 3 mm CF or 5052 alu. 4× M4 to Universal Payload Interface | 0.70 kg | $150–$400 |
| B5 | **Two-tip head + selector solenoid** | 25°/0.35 mm and 40° fan (§7.1) | 0.20 kg | $150–$300 |
| B6 | **Main solenoid valve** | 12 V, ≥8 gpm, low ΔP. Driven by `PUMP_CHANNEL` | 0.30 kg | $60–$150 |
| B7 | **Flow sensor** | Closes the loop on delivered volume vs ground speed | 0.10 kg | $40–$90 |
| B8 | **Laser rangefinder** | **Co-aligned with spray axis.** Standoff hold — why you skip prop guards | 0.10 kg | $150–$400 |
| B9 | **Companion computer** | ARM SBC, **IP66 enclosure, mounted aft** | 0.50 kg | $200–$500 |
| B10 | **Hose clamp / strain relief** | **Bolts to airframe rail, NOT the plate** | 0.40 kg | $80–$200 |
| | **Airborne equipment** | **Leaves 4.56 kg for hose = 21.6 m unsupported** | **4.10 kg** | **$1,410–$3,120** |

#### C · Ground rig — where the IP lives

| # | Item | Why | Cost |
|---|---|---|---|
| C1 | **Soft-wash pump**, 4–8 gpm @ 60–100 psi | Commodity 12 V rig. **60–100 psi *is* 4–7 bar** — our exact table | $1,500–$2,500 |
| C2 | **Electronic pressure regulator** | **This is the PSM.** It never flies | $1,500–$4,000 |
| C3 | **Firmware pressure ceiling** | Must **refuse** an over-ceiling command in hardware — not trust software | incl. C2 |
| C4 | **Powered hose reel** | ⚠️ **Load-bearing.** Holds the hose so the drone doesn't have to | $800–$2,000 |
| C5 | **3/8" hose, 60 m** | 0.211 kg/m charged. Reel carries it; only 21 m may hang free | $200–$500 |
| C6 | **Chemical proportioner** | Per-zone mix ratio, driven by the prescription | $400–$1,200 |
| C7 | **3-way source valve** | DI tank vs bulk tank, upstream of the pump (§4) | $80–$250 |
| C8 | **Containment / recovery** | Detergent to a storm drain is a regulated discharge in California | $500–$1,500 |
| | **Ground rig subtotal** | | **$4,980–$11,950** |

#### D · Water & chemistry

| # | Item | Why | Cost |
|---|---|---|---|
| D1 | **RO unit, 300–600 GPD** | ⚠️ **Mandatory on Carlsbad water** — ~30× resin life (§6) | $400–$1,200 |
| D2 | **DI resin vessel + first fill** | Mixed bed, 1.6–3.6 ft³. Polishes RO permeate to 0 ppm | $400–$900 |
| D3 | **DI buffer tank, 100–275 gal** | You make water 20× slower than you spray it. Fill overnight | $250–$700 |
| D4 | **Bulk tank, 100–200 gal** | Untreated water for roof and stucco | $200–$500 |
| D5 | **Trailer, braked** | ⚠️ 275 gal of water is **2,294 lb**. Axle rating is a real spec | $2,500–$6,000 |
| D6 | **Handheld TDS meter ×2** | The entire quality system for §4.3 | $50 |
| D7 | **Thickened soft-wash surfactant** | **This is your "foam."** Cling from chemistry (§5) | $150–$400 |
| D8 | **Eco degreaser, ammonia-free glass** | Path A chemistry — no Part 137 exposure | $200–$500 |
| D9 | *Sodium hypochlorite + injector* | ⚠️ **Path B only.** Do not buy until §8 is decided | $300–$800 |
| | **Water & chemistry subtotal** | | **$4,150–$11,050** |

#### Kit total — $72,500 to $104,000

Against a single Lucid Sherpa at **$75,000**, which maps nothing, integrates nothing, and leaves you
with no scout, no ground rig and no water system.

---

### 11. Buy it in this order

| Phase | What | Proves | Cost |
|---|---|---|---|
| **1** | **Ground rig on a bench** — C1, C2, C3, D6, gun on a stand | The per-surface pressure loop and the firmware ceiling. **The actual IP.** No aircraft, no licence, no liability | $3,100–$6,600 |
| **2** | **Water train** — D1–D4, D6 | Your real TDS, real resin cost, real fill time. All of §6 replaced with measurements | $1,300–$3,300 |
| **3** | **Scout + photogrammetry** — A3, A4 | **Scan-only revenue.** No spray, no water, no damage exposure — the differentiated half | $20,000–$22,000 |
| **4** | **Cleaner + payload** — A1, A2, A5, A6, B1–B10, C4–C8, D5 | The closed loop | $48,000–$72,000 |

**Phases 1 and 2 cost under $10,000, need no aircraft and no certificate, and test the only thing
that can't be bought:** whether per-surface prescription and verification actually hold up against
real dirt. If the pressure loop doesn't work on a bench, none of the $70,000 above it matters.

---

### 12. ⚠️ Before you cut metal or sign anything

1. **Will Inspired Flight support a liquid spray payload?** Warranty and airworthiness.
   *A "no" ends this build — ask before anything else.*
2. **Exact Universal Payload Interface bolt pattern and load rating.** The plate can't be drawn to
   scale until you have their drawing.
3. **Insurance for a self-integrated spray drone.** Still unasked, still likely the deciding number —
   and §8 changes the quote.
4. **Part 137 applicability to hypochlorite soft washing.** An aviation attorney, not a search result.
5. **Your own tap water TDS.** A $25 meter, ten minutes, and it re-prices all of §6. **Do this today.**

---

### Sources

- [Inspired Flight IF1200A](https://shop.inspiredflight.com/products/if1200a-heavy-lift)
- [Freefly Alta X specifications](https://freeflysystems.com/alta-x/specs)
- [FAA — Dispensing Chemicals and Agricultural Products (Part 137) with UAS](https://www.faa.gov/uas/advanced_operations/dispensing_chemicals)
- [Puretec — DI tank capacity vs feed TDS](https://puretecwater.com/resources/how-many-gallons-of-deionized-water-will-a-di-tank-produce/)
- [Fusion Spray — selecting soft-wash surfactants](https://fusionspray.com/blogs/blogs-basics-and-faqs/selecting-the-best-surfactant-for-pressure-washers-and-soft-washing)

<a id="docsdecisionsverdictandprices"></a>

---

# ⭐ VERDICT — the two aircraft, the system, and what it costs

> **Source file:** `docs/decisions/VERDICT_AND_PRICES.md`

## ⭐ VERDICT — the two aircraft, the system, and what it costs

> *"Give me the verdict — what drone for both applications, scout and cleaning, and prices."*
>
> Final procurement recommendation. Screened **2026-08-16**.
> Prices are list/retail from public sources and are **subject to quote**. Every compliance
> claim must be re-verified at purchase (§6).

---

### THE VERDICT

| Role | Aircraft | Price |
|---|---|---|
| **SCOUT / MAPPING** | **Skydio X10D** | **~$16,000** |
| **CLEANER** | **Inspired Flight IF1200A** | **~$32,000** airframe |

Both **US-made**, both **Blue UAS Cleared**, both **open enough to run our stack**.

#### The headline number

**The complete two-aircraft PROPWASH fleet — everything, both aircraft, ground rig, payload,
software — costs $71K–$93K.**

**A single Lucid Sherpa costs $75,000 outright.**

For the price of one closed spray drone that maps nothing and integrates nothing, you get a
scout, a cleaner, the ground rig that holds the pressure IP, and a stack you own end to end.

---

### 1. SCOUT — Skydio X10D · ~$16,000

| | |
|---|---|
| **Compliance** | ✅ Blue UAS Cleared (X10D since 2024; X10/R10/Dock added July 2026). NDAA compliant, US-manufactured |
| **Thermal** | **Teledyne FLIR Boson+, 640×512, 30 mK** — first on any small UAS; ~40% more sensitive than comparable units |
| **Optical** | Three optical sensors in the same camera system → **RGB + thermal co-registered on one gimbal** |
| **Navigation** | Six custom nav cameras, visual-inertial odometry — holds position without GPS |
| **Price** | ~$16,000 (an Army order implies ~$17.3K/unit) |

**Why it wins:** it replaces the Autel — now on the FCC Covered List — without losing the one
property that mattered. `THERMAL_LAYERING_PIPELINE.md` §1 argued co-registered RGB+thermal on one
gimbal is what turns cross-sensor alignment into a fixed boresight constant. The X10D keeps that.

**And 30 mK sensitivity is the spec that matters most for us.** Our grime proxy reads a
*differential* — a patch cooler than the surface around it. Sensitivity, not resolution, is what
makes a 2 °C depression legible.

> ⚠️ **Note the variant.** X10**D** is the *defense* SKU. The commercial **X10** may be the right
> purchase and may price differently ($15–20K for complete packages). Ask for both.

---

### 2. CLEANER — Inspired Flight IF1200A · ~$32,000

| | |
|---|---|
| **Compliance** | ✅ **Blue UAS *and* Green UAS dual-certified.** US-built, domestically sourced electronics |
| **Endurance** | ⭐ **43 min max flight time** |
| **Payload** | **19.1 lb under Part 107**; up to 28.7 lb with certification |
| **Flight stack** | Open **PX4** architecture |
| **Payload interface** | Universal Payload Interface (M600-compatible spacing) |
| **Price** | **$32,000** airframe direct; bundles with GCS quoted around **$52,000** retail |

**Why it beats the Alta X** — and this reverses my earlier recommendation:

1. **Blue UAS certified *today*.** Freefly's Alta X entered the Blue List in Dec 2023 on an
   Exception to Policy that **expired 28 February 2026**, and Freefly now publishes material on
   transitioning to the AUVSI Green List. Since Blue listing is **one of only two FCC exemptions**,
   this is purchase eligibility, not a badge.
2. **More than double the endurance at load** — 43 min vs ~20 min. Endurance is what shapes the
   field day (`FIELD_OPERATIONS.md` §5.1); fewer swaps, longer job windows.
3. **The payload gap doesn't matter.** A tethered rig puts **3–5 kg** in the air. 19.1 lb is
   ample; the Alta X's 35 lb buys nothing we need.

> ⚠️ **Currently listed as sold out.** Lead time is a real scheduling input — ask first.

---

### 3. FULL COSTED BILL OF MATERIALS

| Item | Low | High |
|---|---|---|
| **SCOUT** — Skydio X10D | $16,000 | $16,000 |
| Spare batteries, case, controller | $4,000 | $6,000 |
| Agisoft Metashape Professional (perpetual) ⚠️ verify | $3,500 | $3,500 |
| **CLEANER** — IF1200A airframe | $32,000 | $32,000 |
| GCS, batteries, care plan (bundle delta) | $8,000 | $20,000 |
| **GROUND RIG** — 12V soft-wash system | $1,500 | $2,500 |
| Electronic regulator + our controller (**the PSM**) | $1,500 | $4,000 |
| DI stage, chemical proportioner, containment | $1,500 | $3,000 |
| **AIRBORNE PAYLOAD** — gun, hose, valve, nozzle, flow sensor | $1,500 | $3,500 |
| Rangefinder + companion computer | $1,500 | $2,500 |
| **TOTAL — full loop, both aircraft** | **$71,000** | **$93,000** |

#### ⭐ The ground rig is almost free, and it's a perfect match

Commodity 12V soft-wash systems run **5.3–7 gpm at 60–100 PSI** for **$1,500–$2,500**.

**60–100 PSI is 4–7 bar. That is our prescription range exactly** — stucco 4.0, tile 5.0,
shingle 5.5, gutter 6.5. We are not designing exotic hardware; we are buying a standard
contractor rig and putting an electronic regulator and our controller on it.

**The "PSM" from `DYNAMIC_PRESSURE_HARDWARE.md` is a ~$3–6K ground assembly, not an
aerospace project.**

---

### 4. SPEND IT IN THIS ORDER

| Phase | What | Cost | Aircraft needed |
|---|---|---|---|
| **1a** | **Scout + photogrammetry software** → start **scan-only revenue** | **$23,500–$25,500** | scout only |
| **1b** | **Ground rig** → proves the per-surface pressure loop and the firmware ceiling | **$4,500–$9,500** | ❌ none |
| **1c** | Auterion Developer Program + Virtual Skynode (evaluate onboard SDK) | subscription | ❌ none |
| **2** | **Cleaner + airborne payload + integration** | **$43,000–$58,000** | ✅ |

**PHASE 1 TOTAL: $28,000–$35,000 — and it earns money.**

That is **37–47% of a single Sherpa**, it generates the differentiated product (verified scans
and reports), it carries **no spray liability, no water, no containment, no damage exposure**, and
it tests the only question that matters: *will anyone pay for the intelligence?*

**If the answer is no, you stopped at $30K instead of $90K.**

---

### 5. WHAT YOU GET THAT NOBODY ELSE HAS

| Capability | Lucid Sherpa ($75K) | This fleet ($71–93K) |
|---|---|---|
| Sprays a building | ✅ | ✅ |
| **Maps the building** | ❌ | ✅ |
| **Per-surface classification** | ❌ | ✅ |
| **Per-face grime layer** | ❌ | ✅ |
| **Per-surface prescription, safety-gated** | ❌ | ✅ |
| **Tamper-evident audit of pressure vs material** | ❌ | ✅ |
| **Verification + re-queue** | ❌ | ✅ |
| **Your code on the aircraft** | ❌ | ✅ |
| **Scan-only revenue with no spray liability** | ❌ | ✅ |

---

### 6. ⚠️ VERIFY BEFORE YOU SPEND

Nothing here is a quote. Six things to confirm, in order of how badly they can hurt:

1. **Liquid spray payload support from Inspired Flight** — warranty and airworthiness position.
   ⚠️ *This can disqualify the aircraft outright.* Ask before anything else.
2. **Skydio radiometric export** — can you get **raw per-pixel temperature** out, in a form
   `fusion/thermal_registration.py` can consume? A colourised JPEG is useless to us.
3. **Blue UAS status on the DCMA list itself**, not vendor pages, for both aircraft — and
   **which FCC exemption** each purchase relies on. Both exemptions expire **1 Jan 2027**.
4. **Insurance** for a self-integrated spray drone versus a vendor-supported one.
   *Still unasked, still likely the deciding number.*
5. **IF1200A lead time** — listed sold out.
6. **X10 vs X10D** — commercial versus defense SKU, price and capability difference.

> `TODO(PROPWASH): all six are quotes/questions, not research. None can be resolved from a desk.`

<a id="docsdecisionsfleetarchitecture"></a>

---

# Fleet Architecture — every aircraft and system, for all needs

> **Source file:** `docs/decisions/FLEET_ARCHITECTURE.md`

## Fleet Architecture — every aircraft and system, for all needs

> *"Continue analyzing, finding the best drone and system for all my needs."*
>
> Supersedes the single-aircraft framing in `BUILD_SPEC.md`. Screened 2026-08-16.
>
> ⚠️ **This document changes the scout recommendation and re-ranks the cleaning airframe.**
> A December 2025 FCC action broke assumptions made throughout this repo.

---

### 0. ⚠️ THE RULE CHANGE THAT RESETS EVERYTHING

On **22 December 2025** the FCC added to its Covered List **all uncrewed aircraft systems, and
UAS critical components, produced in a foreign country.** Wiley called it
"unexpected, first-of-its-kind." It is far broader than the DJI action we already logged.

| What | Effect |
|---|---|
| Covered equipment cannot obtain **new FCC equipment authorizations** | No new import, marketing or sale in the US |
| **Previously authorized models stay valid** | Existing fleets keep flying |
| Scope includes **"UAS critical components"** | Not just airframes — components too |

**Two exemptions (issued 7 Jan 2026, effective through 1 Jan 2027):**

1. **Blue UAS Cleared List** — DCMA-managed (moved from DIU in July 2025)
2. **Buy American** — manufactured in the US with **domestic content > 65% of cost**
   (rising to 75% after 2028)

#### What this breaks in our own plan

- ❌ **The Autel EVO MAX 4T V2 — our scout — is Covered.** The FCC named **DJI *and* Autel**
  explicitly, and then covered all foreign-produced UAS besides. Autel is contesting it (arguing
  the FCC relied on classified material it could not see, and on allegations aimed at DJI), but
  **the proceeding is live and the listing stands.**
  → **CLAUDE.md §4 names the Autel as the sensing platform. That needs to change.**
- ❌ **Foxtech / EAUAV payloads look worse, not better.** "UAS critical components" plausibly
  captures a foreign-made powered payload. Already a "no" on pressure class; now likely a
  sourcing problem too.
- ⚠️ **Every compliance claim in this repo has a shelf life.** The exemptions expire
  **1 January 2027**. Re-verify at purchase — do not trust this document or any vendor's page.

---

### 1. The fleet — four roles

| # | Role | Recommendation | Status |
|---|---|---|---|
| 1 | **Scout / mapping** | **Skydio X10D** | ⭐ NEW — replaces the Autel |
| 2 | **Cleaner (aerial soft-wash)** | **Inspired Flight IF1200A** *or* Freefly Alta X Gen2 | ⭐ RE-RANKED |
| 3 | **Ground unit (hardscape, high pressure)** | Deferred — conventional gear first | Phase 3 |
| 4 | **Second aerial (pre-soak pipelining)** | Deferred — only pays on large commercial | Phase 3 |

---

### 2. Role 1 — Scout. **Skydio X10D**

The Autel replacement, and on the merits it is an upgrade rather than a compromise.

| | Skydio X10D |
|---|---|
| Compliance | ✅ **Blue UAS Cleared** (X10D since 2024; X10, R10 and Dock added July 2026) |
| Thermal | **Teledyne FLIR Boson+** — described as the most precise radiometric thermal sensor in small UAS |
| Optical | **Three optical sensors** alongside the thermal, in one camera system |
| Origin | US |

#### Why it preserves the thing that mattered

`THERMAL_LAYERING_PIPELINE.md` §1 argued the single strongest case for the Autel 4T V2 was
**co-registered RGB + thermal on one gimbal** — it turns cross-sensor alignment from a per-frame
problem into a fixed boresight constant, which is what makes Metashape's multi-camera workflow
clean.

The X10D carries its optical and thermal sensors in **one camera system**, so that property
survives the swap. `geometry/autel_ingest.py` models boresight as a constant; the module needs a
rename and a new file-format reader, **not a redesign**.

**Radiometric matters more than resolution here.** Our grime proxy reads *differential*
temperature — a patch cooler than the surface around it. That needs trustworthy per-pixel
temperature, which is exactly the Boson+'s claim.

**Budget alternative: Parrot ANAFI USA** — Blue-cleared, multi-sensor, and described as the most
accessible option on the list. Lower capability; a reasonable way to start cheap.

> ⚠️ **Verify before buying:** radiometric (not just thermal) output, whether the raw radiometric
> data is *exportable* for our own registration, and thermal resolution. A thermal camera that
> only exports a colourised JPEG is useless to `fusion/thermal_registration.py`.

---

### 3. Role 2 — Cleaner. **Re-ranked, and it is closer than it looked**

#### The wrinkle in the Alta X recommendation

Freefly's Alta X was incorporated into the DIU Blue List 2.0 in **December 2023**, then granted a
**one-year Exception to Policy extension running to 28 February 2026** — which has now passed.
Freefly publishes a knowledge-base article on *"DIU Blue List and transition to AUVSI Green
List,"* which suggests a move from Blue to Green.

**Blue listing is one of only two FCC exemptions.** So this is no longer a nice-to-have badge —
it is a purchase-eligibility question.

Freefly is US-made, so the **Buy American >65% domestic content** exemption very likely covers it
regardless. But that is an inference, not a verified fact, and it should be confirmed in writing.

#### Side by side

| | **Inspired Flight IF1200A** | **Freefly Alta X Gen2** | **Watts PRISM Sky** |
|---|---|---|---|
| Blue UAS status | ✅ **Blue UAS-certified** (IF1200A + IF800 listed) | ⚠️ ETP lapsed Feb 2026; Green List transition | ⚠️ NDAA stated; **Blue status unconfirmed** |
| Also | **Green UAS dual-certified** | — | — |
| Payload | 8 kg / 19.1 lb | **15.9 kg / 35 lb** | 11.3 kg / 25 lb |
| Endurance | ⭐ **~43 min** | ~20 min @ 20 lb | — |
| Flight stack | Open **PX4** | **Auterion** Skynode | **Auterion** |
| Onboard app | Companion computer (DIY) | ⭐ **AuterionOS SDK, sandboxed** | ⭐ AuterionOS |
| Payload interface | Universal Payload Interface | Bay: Ethernet + power + LTE | Rails top *or* bottom |
| Price | quote | ~$45,000 | quote |

#### The payload question resolves itself

We established in `BUILD_SPEC.md` that with **tethered water** the aircraft carries a gun, a hose,
a valve, a nozzle, a flow sensor, a rangefinder and a small computer — call it **3–5 kg**.

**So 8 kg is ample. The Alta X's 15.9 kg advantage buys nothing we need**, while its ~20 min at
load is less than half the IF1200A's 43 min. Endurance is the number that shapes the field day
(`FIELD_OPERATIONS.md` §5.1), and more endurance means fewer battery swaps.

#### The real trade

| If your priority is… | Choose | Because |
|---|---|---|
| **Compliance certainty + endurance** | **IF1200A** | Blue-cleared today; 43 min; 8 kg is enough for a tethered rig |
| **The AuterionOS onboard app** | **Alta X** or **PRISM Sky** | Managed ROS 2 sandbox, supported, enforces the Tier separation structurally |

**A companion computer on the IF1200A's PX4 gets the same *function*** — read telemetry, command
motion, drive actuators. Auterion buys a *supported, sandboxed* way to do it, which is worth real
money for the insurer and waiver story (`PLATFORM_VENDOR_CHOICE.md` §2), but it is not the only path.

#### 🎯 Recommendation

**Lead with the Inspired Flight IF1200A**, on compliance certainty and endurance, and build the
onboard layer as a companion-computer app on open PX4.

**Keep Alta X / PRISM Sky live** if Auterion's SDK proves decisive after the Virtual Skynode
evaluation — which costs a subscription and no aircraft.

*This reverses `BUILD_SPEC.md` §1. The reason is the FCC action, not new opinion.*

---

### 4. Roles 3 and 4 — deliberately deferred

#### Ground unit (hardscape)

Concrete, driveways and parking decks genuinely need **100–200 bar** — the range we correctly
refused for the aircraft. That is a **ground robot's** job.

**Do not buy one yet.** A conventional surface cleaner and an operator does hardscape today at
near-zero capex. The robot is justified when hardscape is a large, recurring share of revenue —
and the intelligence layer transfers to it unchanged, because per-surface prescription and
verification do not care what the machine is.

#### Second aerial (pre-soak pipelining)

The phase scheduler shows why this waits: on the reference house, deconfliction caps concurrency
at **1 aircraft**, so a second aircraft changes job time by **nothing**. And the 900-second-dwell
model showed a single aircraft already hides **66 of 66.5 minutes** of dwell by switching zones.

**A second aircraft pays only on large commercial and solar sites, and only with a 107.35 waiver.**
Both belong to the re-aimed segment in `GO_NO_GO.md`, not to Year 1.

---

### 5. The complete system

```
 SCOUT              Skydio X10D  (Blue) ── RGB + radiometric thermal, one gimbal
   │
   ▼
 PROCESS            photogrammetry → our fusion → per-face surface + grime layer
   │
   ▼
 PRESCRIBE          per-zone pressure / chemistry / dwell, safety-gated, human-signed
   │
   ▼
 EXECUTE            IF1200A + soft-wash gun on a ground tether
   │                 ├── airborne: gun, hose, valve, nozzle, flow sensor, rangefinder, computer
   │                 └── GROUND:  pump · electronic regulator (= the PSM) · firmware ceiling
   │                              chemical injection · DI stage · containment
   ▼
 VERIFY             re-scan → PASS / re-queue → deviation log → surface-table calibration
```

**Two aircraft, one ground rig, one software stack.** The ground rig holds the pressure IP; the
aircraft is a positioning system for a nozzle; the software is the company.

---

### 6. Capital, in the order it should be spent

| | Item | Aircraft needed? |
|---|---|---|
| 1 | **Ground rig** — pump, regulator, gun on a stand | ❌ |
| 2 | **Auterion Developer Program + Virtual Skynode** (evaluate the SDK) | ❌ |
| 3 | **Scout** — Skydio X10D (or ANAFI USA to start cheap) → **scan-only revenue** | ❌ cleaner |
| 4 | Vendor quotes: Inspired Flight, Freefly, Watts | ❌ |
| 5 | **Cleaner** — IF1200A + integration | ✅ |
| 6 | Ground robot / second aerial | ✅ |

**Steps 1–4 need no cleaning aircraft, and step 3 earns money.** The scout is the only aircraft
required to start, and it is the one that generates the differentiated product.

---

### 7. What must be re-verified before any purchase

- [ ] **Blue UAS Cleared List membership**, on the **DCMA list itself** — not vendor marketing —
      for every airframe considered. *Freefly Alta X's status is specifically unclear.*
- [ ] **Skydio X10D radiometric export** — can we get raw per-pixel temperature out, in a form
      `fusion/thermal_registration.py` can consume?
- [ ] **Which FCC exemption** each purchase relies on (Blue listing vs Buy American >65%) — and
      that it is documented, since **both expire 1 January 2027**.
- [ ] **Liquid spray payload support** — warranty and airworthiness, from Inspired Flight and
      Freefly. ⚠️ Still the disqualifying question.
- [ ] **Whether a foreign-made payload counts as a "UAS critical component."** ⚠️ Counsel.
- [ ] **Insurance** for a self-integrated spray drone. Still unasked, still likely decisive.

> `TODO(PROPWASH): CLAUDE.md §4 hardware inventory is out of date — the Autel is Covered-Listed.`

<a id="docsdecisionsplatformvendorchoice"></a>

---

# Decision — which drone company, and how our stack gets inside it

> **Source file:** `docs/decisions/PLATFORM_VENDOR_CHOICE.md`

## Decision — which drone company, and how our stack gets inside it

> **Kevin:** *"It needs to be differentiated from any other company out there, and I need to
> integrate my tech stack into the drone. Lucid doesn't allow that."*
>
> Extends `INTEGRABLE_PLATFORM.md` with the vendor screen it said was still owed.
> Screened 2026-08-16.

---

### 0. The answer: don't pick a drone, pick the operating system

**Go with Auterion.** Then choose an airframe from the several NDAA manufacturers that already
run it.

This is the single most important decision in the document, and it is not the one that was being
asked. "Which drone company" is the wrong frame — it is how you end up locked to a vendor again,
which is exactly the Lucid problem.

**AuterionOS lets you run your own application *on the aircraft's mission computer*.** Not "send
it waypoints from the ground." Your code, on the drone, sandboxed as an add-on, built on ROS 2,
able to issue position/velocity/acceleration commands, read telemetry, and **interact with
external payloads**.

That is literally the request: *integrate our technology into the drone.*

And because **Freefly, Watts Innovations and others all build on Auterion**, you write the
integration **once** and the airframe becomes a commodity you can re-source. No vendor can
switch you off. That is the structural fix for what Lucid did to you.

**Recommended first aircraft: Freefly Alta X Gen2 (NDAA).** Reasoning in §3 — but note the
airframe is now the *replaceable* part of the decision, which is the point.

---

### 1. What "integrate my stack into the drone" actually requires

Four levels, increasing depth. Lucid gives you level 0. Most vendors stop at level 2.

| Level | What it means | Who offers it |
|---|---|---|
| 0 — **Work order** | Hand a human a job sheet | Lucid (Path A) |
| 1 — **Mission upload** | Push waypoints and speeds to the aircraft | Most enterprise drones, DJI included |
| 2 — **Payload control** | Command a pump/servo as an actuator mid-mission | Any PX4/ArduPilot airframe |
| 3 — **Onboard application** ⭐ | **Your software runs on the aircraft**, reads telemetry, commands motion, drives payloads, closes a loop in flight | **AuterionOS apps via Auterion SDK** |

Level 2 is where `execution/mavlink_mission.py` sits today, and it is enough to fly a
prescription. **Level 3 is where the differentiation lives**, because it is the only level at
which the aircraft can *react to what it is seeing while it is spraying*.

#### Why level 3 is the actual moat

Everything in the repo today is **open-loop within a pass**: scan, decide, fly the plan, verify
afterwards. Every competitor could eventually do that.

With an onboard app you get **closed-loop within the pass**:

- adjust standoff or traverse speed when the live thermal says a patch is heavier than the plan
  assumed;
- hold a pass longer on a zone that isn't responding, instead of discovering it at verification;
- abort a zone the instant a surface reads wrong — before damage, not after.

**Nobody in exterior cleaning is doing in-flight adaptive treatment.** Not Lucid, not the 18
regional operators, not the PV inspection platforms. That is a defensible claim, and unlike
"we detect soiling" (which `GO_NO_GO.md` §1.4 showed is commoditised) it is not already shipping
somewhere else.

---

### 2. The Auterion route in practice

| | |
|---|---|
| **Auterion SDK** | Build onboard software for AuterionOS vehicles. **Based on ROS 2.** Apps send acceleration / velocity / position commands and receive autopilot telemetry |
| **Third-party apps** | Explicitly supported: *"through common APIs, third-party software companies can develop AuterionOS applications that add use-case-specific capabilities"* |
| **Sandboxing** | Customer apps run as add-ons **in a safe sandbox within the mission computer** — Auterion manages the OS |
| **Access** | AuterionOS **2.7+** and a **Skynode Developer Program** subscription via Auterion Suite |
| **⭐ Virtual Skynode** | **A simulated Skynode. You can develop and test the onboard app with no aircraft at all.** |

#### The sandbox is a feature, not a limitation

Read the sandbox against **CLAUDE.md §2**. Our own architectural rule says a Tier-3 agent must
never write a Tier-0 setpoint or suppress a Tier-1 check. Auterion **enforces that in the
platform**: our app is an add-on, the OS and flight control are Auterion's, and the separation is
structural rather than a promise in a design doc.

That is an easier story for an insurer, a customer and an FAA waiver application than "we
promise our code stays out of the flight loop."

#### Virtual Skynode changes the sequencing

`INTEGRABLE_PLATFORM.md` §7 said: build the ground rig before buying a $45K aircraft. Virtual
Skynode extends that further —

> **You can build and test the onboard application before buying any aircraft, and before
> building the ground rig.**

Ground rig proves the *pressure* IP. Virtual Skynode proves the *onboard* IP. Neither needs an
airframe. **The capital decision moves to the end of the process, not the start.**

---

### 3. Airframe screen — all Auterion/PX4, all NDAA, all US-made

| | **Freefly Alta X Gen2** | **Watts PRISM Sky** | **Inspired Flight IF1200A** |
|---|---|---|---|
| Payload | **15.9 kg / 35 lb** ⭐ | 11.3 kg / 25 lb | 8 kg / 19.1 lb |
| Endurance | ~41.7 min @ 5 lb · ~20 min @ 20 lb | LTE-enabled, heavy-lift | **~43 min max** ⭐ |
| Flight stack | Skynode, **Auterion Enterprise PX4** | **Auterion ecosystem**, Pixhawk-based, ArduPilot **or** PX4 | **Open PX4 architecture** |
| Payload mounting | Smart Dovetail + internal bay: **Ethernet, regulated power, LTE** | **Rail system — top *or* bottom mounting**, quad or X8 coaxial ⭐ | **Universal Payload Interface** (M600-compatible spacing) |
| Compliance | NDAA; **Blue List in process** | NDAA, US-made (Baltimore) | **Blue UAS *and* Green UAS dual-certified** ⭐ |
| Price | **~$45,000** | quote | quote |

#### How to read that table

- **Alta X — most payload, best documented integration path.** The internal bay with Ethernet,
  regulated power and LTE is purpose-built for a companion computer, and Freefly explicitly
  documents MAVSDK control "from the ground via radio, or onboard via an expansion computer."
  **Recommended first aircraft.**
- **PRISM Sky — most mechanically flexible.** Rail mounting top *or* bottom and a
  quad/X8-coaxial choice matters for a spray system, where nozzle geometry and hose routing fight
  the airframe. Worth a serious quote.
- **IF1200A — best compliance posture, least payload.** Blue *and* Green certified is the
  strongest position for institutional and federally funded work — which `GO_NO_GO.md` argued is
  the segment to target. 8 kg is thin for spray, **but with tethered water you are carrying a
  ~1.2 kg gun and hose, not a tank.** Do not rule it out on payload alone.

**Nobody should buy on this table.** Send all three the §1.0 questionnaire, and add the two
questions this document exists to ask:

1. *Do you run AuterionOS, at what version, and will you support a third-party onboard app?*
2. *What is your position — warranty and airworthiness — on a customer-integrated **liquid spray**
   payload?*

Question 2 is the one that will actually disqualify vendors. Water, electronics and rotors is a
different conversation from a camera gimbal, and a vendor who says no to it is a dead end no
matter how good the SDK is.

---

### 4. The full stack, end to end

```
  Autel 4T V2 scan
        │
        ▼
  Photogrammetry + our fusion  ──▶  per-face surface + grime layer     [Tier 3, ground]
        │
        ▼
  Supervisor  ──▶  per-zone prescription, safety-gated                 [Tier 3, ground]
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  OUR ONBOARD APP  (AuterionOS add-on, ROS 2, sandboxed)          │  ⭐ the new part
  │   · executes the zone plan                                      │
  │   · reads live telemetry + payload sensing                      │
  │   · adapts standoff / speed / dwell WITHIN the pass             │
  │   · commands nozzle select + pump on/off                        │
  │   · aborts a zone on an unexpected surface reading              │
  └─────────────────────────────────────────────────────────────────┘
        │                                    │
        ▼                                    ▼
  Auterion flight control              GROUND PUMP + regulator        [Tier 0/1 — theirs]
  (untouched, sandboxed away)          = the PSM, pressure IP          [ours, not flying]
        │
        ▼
  Post-clean verification ──▶ PASS / re-queue ──▶ learning
```

Two things to notice:

1. **The pressure intelligence never flies** (`INTEGRABLE_PLATFORM.md` §4). It lives on a ground
   pump we own outright. The aircraft only selects a nozzle and toggles a pump.
2. **The flight controller is never touched.** The sandbox guarantees it. We modulate fluid and
   request motion; we do not stabilise the vehicle.

---

### 5. Why this is genuinely differentiated

| Layer | Anyone can copy? | Ours |
|---|---|---|
| Buy a cleaning drone | ✅ trivially — Lucid has ~1,000 deployed | — |
| Detect soiling from thermal/RGB | ✅ ships in PV inspection software today | — |
| Plan a coverage path | ✅ standard mission planning | — |
| **Per-surface prescription with hard safety ceilings** | ⚠️ needs the surface model + calibration data | ✅ |
| **Tamper-evident audit of what pressure touched what material** | ⚠️ nobody has built it | ✅ |
| **In-flight adaptive treatment from live sensing** | ❌ **nobody in cleaning is doing this** | ✅ level 3 |
| **Verification-driven parameter learning across jobs** | ❌ needs the deviation log, which compounds | ✅ |

The bottom four rows are the company. The top three are table stakes that a competitor buys with
a purchase order.

**And the moat compounds in the right direction:** every job feeds the deviation log, which tunes
the surface table, which makes the next prescription better. A competitor starting two years
later doesn't just lack the code — they lack the data.

---

### 6. Sequence — capital last

| Step | Cost | Proves |
|---|---|---|
| 1. **Skynode Developer Program + Virtual Skynode.** Port the Tier-2 executor to an AuterionOS app; fly the reference house in simulation | subscription only | The onboard app works. **No aircraft.** |
| 2. **Ground rig** — pump, electronic regulator, gun on a stand | low four figures | The pressure control loop + safety ceiling. **No aircraft.** |
| 3. **Quote all three vendors** on the two questions in §3 | free | Who will actually support a spray integration |
| 4. **Scan-only revenue** in parallel (`GO_NO_GO.md` §3) | Autel only | That anyone pays for the intelligence |
| 5. **Buy one airframe** and integrate | ~$45K + integration | The whole thing |

**Steps 1, 2 and 4 all happen before any airframe purchase.** If step 4 fails, you have spent a
subscription and a few thousand dollars, not forty-five plus an integration programme.

---

### 7. Open questions — ask before committing

- [ ] **Skynode Developer Program: cost, terms, and commercial-product licensing.** Can we ship a
      commercial product built on it, and on what royalty or licence basis?
- [ ] **Will Freefly / Watts / Inspired Flight support a liquid spray payload?** Warranty and
      airworthiness position. **This is the disqualifying question.**
- [ ] **Does the sandbox permit the actuator control we need**, or only motion commands? The docs
      say apps "interact with external payloads" — confirm that includes commanding a servo/relay.
- [ ] **Real endurance with tether and gun running** — not the datasheet payload figure.
- [ ] **Insurance for a self-integrated spray drone** versus a vendor-supported one. Still the
      number most likely to decide this, and still unasked.
- [ ] **Auterion's own roadmap** — if Auterion or a partner ships cleaning-specific capability,
      the same commoditisation that hit soiling detection hits us.

> `TODO(PROPWASH): needs Kevin + Auterion + airframe vendors + insurer before capital.`

<a id="docsdecisionsintegrableplatform"></a>

---

# Decision — an airframe we can actually integrate into (non-Lucid)

> **Source file:** `docs/decisions/INTEGRABLE_PLATFORM.md`

## Decision — an airframe we can actually integrate into (non-Lucid)

> **Kevin's requirement:** stop building on Lucid. Own an airframe our tech can drive directly.
>
> **Supersedes the platform recommendation in `CLEANING_DRONE_PLATFORM.md`.** That doc
> recommended "DJI M350/M400 + Foxtech AeroClean, ~$25–45K" as the own-the-stack route.
> **That route is now largely closed** (§1). Screened 2026-08-16.

---

### 0. The recommendation, up front

**Freefly Alta X Gen2 (NDAA) + tethered water + ground-side pressure control.**

Three reasons, in order of importance:

1. It runs **Auterion Enterprise PX4 on a Skynode** and is **controllable via MAVSDK** — from the
   ground radio *or* from a companion computer in its own payload bay. That is exactly the
   interface `execution/mavlink_mission.py` already emits against.
2. It is **US-made and NDAA-compliant** (Blue List in process), which the DJI path no longer is.
3. With **tethered water, the hard part stops flying** (§4) — the pressure intelligence moves to
   the ground, where we control it completely and where it is not a flight-safety function.

**~$45,000 airframe.** More than a Sherpa's assumed cost, and worth it, because it is the only
configuration where the IP in this repo can actually run.

---

### 1. ⚠️ The DJI path closed in December 2025

Our earlier recommendation assumed DJI M350/M400 + a Foxtech AeroClean kit. Current status:

| Fact | Consequence |
|---|---|
| DJI is on the **FCC Covered List**. On 21 Dec 2025 a White House interagency body issued an affirmative national-security determination; the FCC implemented it the next day | **New models cannot receive FCC equipment authorisation, so they cannot be legally imported or sold in the US** |
| Existing airframes stay legal to own and fly; firmware/security updates committed to **1 Jan 2029** | An existing fleet keeps working — but you cannot *grow* one |
| US retail stock is **depleting and not being replenished** | Sourcing risk on every additional aircraft |
| From 22 Dec 2025, federal contractors **may not use drones from covered foreign entities on federally funded contracts** | **Municipal, school-district, port, military-adjacent and federally funded commercial work is off the table** |

**Read that last row against `GO_NO_GO.md`:** we just concluded the business should re-aim at
*commercial and institutional* customers. Institutional buyers are exactly the ones with federal
funding threads. Building on DJI would foreclose the segment we just decided to target.

**Foxtech's AeroClean kits are excellent hardware but built around DJI mounting, power and
comms** — AeroClean P3 (T50) and T-M400C are specified for M350/M400. The kit is not the problem;
the aircraft under it is.

---

### 2. Why Alta X fits what we already wrote

`execution/mavlink_mission.py` translates a `FlightPlan` into MAVLink mission items plus
`ActuatorServos` setpoints for pump / pressure / nozzle. That was written speculatively. It turns
out to be exactly right:

- **PX4 documents sprayers as generic actuators controlled over MAVLink** — pump activate/
  deactivate, and where the hardware supports it, flow rate and nozzle shape. Our channel model
  (`PUMP_CHANNEL`, `PRESSURE_CHANNEL`, `NOZZLE_CHANNEL`, normalised to [-1, 1]) is the standard
  PX4 pattern, not an invention.
- **MAVSDK is the recommended MAVLink API for PX4** and is what Freefly documents for Alta X:
  *"control of Alta with custom MAVSDK API software, from the ground via radio, or onboard via
  an expansion computer."*
- The Alta X **internal payload bay provides Ethernet, regulated power and LTE** — a home for a
  companion computer running our Tier-2 orchestrator, with a backhaul for telemetry.

#### Specifications that matter operationally

| | Alta X Gen2 |
|---|---|
| Payload | **15.9 kg / 35 lb** |
| Endurance | ~41.7 min @ 5 lb · **~20 min @ 20 lb** |
| Flight stack | Skynode, **Auterion Enterprise PX4** |
| Control API | **MAVSDK** (ground radio or onboard companion) |
| Price | **from ~$45,000** |
| NDAA | Airframe + Pilot Pro compliant. ⚠️ **The stock Herelink radio is NOT** — the NDAA variant swaps in a Doodle Labs link. **Buy the NDAA SKU, not the standard one.** |

**Cross-check against `FIELD_OPERATIONS.md` §5.1:** 114 min of spray time at ~20 min endurance is
~6 flights and ~5 swaps (+15 min). At a lighter tethered payload, endurance improves. That is a
workable day — unlike an 8-minute untethered tank configuration.

---

### 3. Options considered

| Option | Integrable? | NDAA / sourcing | Verdict |
|---|---|---|---|
| **Freefly Alta X Gen2 (NDAA)** | ✅ PX4 + MAVSDK + payload bay w/ Ethernet, power, LTE | ✅ US-made, Blue List in process | ⭐ **Recommended** |
| Lucid Sherpa | ❌ No confirmed developer control API; autonomy kept in-house | ✅ | The thing we are moving away from |
| DJI M350/M400 + Foxtech AeroClean | ⚠️ PSDK payload dev only; flight control not open like PX4 | ❌ **Covered List — no new imports, federal-contract prohibition** | ❌ Closed (§1) |
| Full custom PX4/ArduPilot build (Pixhawk / Cube Orange+ / ARK) | ✅ Maximum control | ⚠️ Depends entirely on sourcing | Cheapest and most work. **No support, no warranty, and you own airworthiness.** Viable later, wrong for first aircraft |
| Apellix | ⚠️ Computer-controlled but vendor-closed | ✅ US | Industrial/tank market, not building façades |

**Not screened, worth checking before committing:** Watts Innovations, Inspired Flight, Harris
Aerial — other US NDAA heavy-lift builders. Ask each the same questionnaire
(`LAUNCH_PLAYBOOK.md` §1.0). Do not take this doc's single recommendation without quoting at
least two.

---

### 4. ⭐ The architectural insight: with a water tether, the hard part stops flying

This is the most important paragraph in the document.

`DYNAMIC_PRESSURE_HARDWARE.md` designs a **PSM** (electronic pressure module) and **IHM**
(motorised nozzle turret) as *airborne* payloads. That framing came from assuming an onboard tank.
**With tethered water, it is wrong — and wrong in our favour.**

In a tethered-water configuration:

- the **pump and pressure regulator sit on the ground**, not on the aircraft;
- the drone carries a **spray gun and hose** (Foxtech's is ~1.2 kg), not a tank and pump;
- so the aircraft needs only **pump on/off** and **nozzle selection** — two simple actuator
  channels — while **pressure is commanded ground-side**.

Three consequences, all good:

1. **Dramatically less airborne integration risk.** No high-pressure electronics on a flying
   vehicle, no weight penalty, no vibration/water-ingress qualification on the hard part.
2. **The pressure intelligence — the actual IP — runs on equipment we fully own and can change
   today**, without a vendor, an airframe integration, or an airworthiness argument. A ground
   pump with a VFD or electronic regulator, commanded by our orchestrator, *is* the PSM.
3. **It is clean under CLAUDE.md §2.** Commanding a ground pump is not a flight-safety function
   and touches no Tier-0 or Tier-1 loop. The aircraft's flight controller is untouched; we
   modulate the fluid, not the vehicle. That is the most defensible possible split.

**Practical read: we can build and validate the per-surface pressure control loop on a ground rig
with a spray gun on a stand — no aircraft at all — and prove the core IP before spending $45K.**

---

### 5. What integration actually requires

| Layer | Status | Work |
|---|---|---|
| Mission upload (waypoints, speeds) | ✅ `mavlink_mission.py` emits it | Wire MAVSDK connection — documented seam in `mavlink_transport.py` |
| Pump on/off | ✅ modelled as `ActuatorServos` | Map to a real PX4 actuator output; relay/solenoid on the gun |
| Nozzle selection (IHM) | ✅ modelled | Build the turret, or fly fixed nozzles and change by hand at first |
| **Pressure control (PSM)** | ✅ modelled | **Move to ground pump (§4).** Electronic regulator + our controller |
| Telemetry back | ⚠️ | MAVSDK telemetry → Tier-2 orchestrator; LTE in the payload bay |
| Safety gating | ✅ `safety/checks.py`, hard ceilings, audit log | Enforce ground-side too — the regulator must refuse an over-ceiling command in firmware |

**Nothing here requires a vendor's permission.** That is the whole point of leaving the Sherpa.

---

### 6. What this does NOT change

- **Part 107 still governs.** An open flight stack does not grant autonomy. Pre-programmed missions
  are already legal; VLOS (107.31) and multi-aircraft (107.35) still bind and are still waiverable
  (`REGULATORY_STRATEGY.md`, `WAIVER_107_35.md`). Owning the airframe changes the *software* story,
  not the *regulatory* one.
- **The operator stays in command** (CLAUDE.md §10).
- **Tier 0 is still untouchable.** We command payload actuators and upload missions. We do not
  write flight-stabilisation setpoints, and PX4 being open source is not a licence to start.
- **Airworthiness becomes ours.** On a Sherpa, the vendor owns the aircraft's integrity. Bolt a
  spray system to an Alta X and **we** own that integration, its failure modes and its liability.
  Budget for that — it is the real cost of the freedom, and it is not in the $45K.

---

### 7. Recommended sequence

1. **Build the ground rig first.** Pump + electronic regulator + gun on a stand. Prove per-surface
   pressure control and the safety ceiling with **zero aircraft** and near-zero capex. This
   de-risks the IP that matters (§4).
2. **Quote at least three NDAA heavy-lift builders** — Freefly plus two of Watts / Inspired
   Flight / Harris — against the §1.0 questionnaire. Confirm payload-bay power, Ethernet, actuator
   outputs, and whether they will support a spray integration at all.
3. **Confirm with Foxtech** whether an AeroClean gun/tether assembly can be supplied decoupled
   from DJI mounting and control — the mechanical parts are likely reusable.
4. **Then** buy one Alta X Gen2 **NDAA SKU** and integrate.

**Do not buy an aircraft before step 1.** The ground rig tests the thesis for a few thousand
dollars; the aircraft tests it for forty-five.

---

### 8. Open questions

- [ ] Will Freefly support a **liquid spray payload** on Alta X — warranty and airworthiness
      position? Water plus electronics plus rotors is not a camera gimbal.
- [ ] Tethered-hose dynamics on an Alta X: hose weight, drag and snag behaviour differ from the
      airframes Foxtech tuned against.
- [ ] Real endurance **with the tether attached and gun running** — not the 20 lb datasheet figure.
- [ ] Auterion Enterprise PX4 licence terms for a **commercial derivative product**.
- [ ] Insurance: what does a carrier charge for a self-integrated spray drone versus a
      vendor-supported one? This may be the deciding number and nobody has asked it.

> `TODO(PROPWASH): needs Kevin + Freefly + insurer decisions before committing capital.`

<a id="docsdecisionsairframecontenders"></a>

---

# Airframe contenders — the full screened field

> **Source file:** `docs/decisions/AIRFRAME_CONTENDERS.md`

## Airframe contenders — the full screened field

> *"What other drones might be a contender to envelop this tech stack?"*
>
> Extends `VERDICT_AND_PRICES.md` with everything screened, including three not looked at before.
> Screened 2026-08-16.

---

### ⚠️ Correction: the Raptor IS a real drone

Last turn I said no cleaning drone called Raptor exists and assumed you meant Raptor Maps.
**Both were half right.** There is a real aircraft: the **Anzu Robotics Raptor** and **Raptor T**.

**But the answer is still no, for four independent reasons:**

| | |
|---|---|
| **Discontinued** | Anzu announced in **Feb 2026** that the Raptor line is **no longer available** — component shortages stalled production. They are pivoting to a "next generation" product |
| **DJI-derived** | Built under a **technology licensing agreement with DJI**, manufactured in Malaysia. The whole premise was being a DJI alternative — which is a fragile place to stand given §0 of `FLEET_ARCHITECTURE.md` |
| **NDAA status "mixed"** | Chinese-sourced components remain, including **the thermal sensor on the Raptor T**. Anzu acknowledged the concern |
| **Wrong class entirely** | Mavic-3-class small aircraft. Not a heavy lifter — it could never carry a cleaning payload |

**Verdict: ❌ dead on arrival.** Discontinued, compliance-ambiguous, and the wrong size regardless.

---

### ⭐ The strongest contender I had not screened: Harris Aerial Carrier H6 Hybrid

A **gas-electric hybrid** heavy-lift hexacopter, and the endurance figures are in a different league.

| | Carrier H6 Hybrid EFI |
|---|---|
| Power | **H2400 EFI gas-electric generator** — also runs fully electric |
| Endurance | **2.5 hours @ 4 kg payload** · 1.5 hours @ 5 kg max |
| Deploy | Folds; flight-ready in **under two minutes** |
| Family | **Carrier H6HL** (40 kg heavy-lift) · **H6 Hydrone** (hydrogen fuel cell) · H6 Electric |
| NDAA / Blue | ⚠️ **Not confirmed** |
| Price | ⚠️ **Not published** |

**Our airborne payload with tethered water is 3–5 kg — right in its sweet spot.**

#### But I checked the actual benefit, and it's smaller than it sounds

| Job | Alta X (20 min) | IF1200A (43 min) | H6 Hybrid (150 min) |
|---|---|---|---|
| **Reference house** — 114 min spray | 4.7 swaps, **14 min lost** | 1.7 swaps, **5 min lost** | **0 swaps** |
| **Large commercial** — 8 h flight | 23 swaps, **69 min lost** | 10 swaps, **30 min lost** | 2.2 swaps, **7 min lost** |

**On a house, endurance saves ~14 minutes of a ~3.7 hour day — about 6%.** Fixed setup, briefing,
pre-flight and pack-down (~100 min) dominate, so swaps barely move the total.

**On an 8-hour commercial job it saves about an hour** — and that is exactly the segment
`GO_NO_GO.md` re-aimed at.

#### ⚠️ Three problems specific to *our* use

1. **Exhaust over freshly cleaned surfaces.** A petrol generator hovering above glass and solar
   panels you have just cleaned deposits combustion products on them. **This may be
   disqualifying for solar and glass work** and I have seen nothing addressing it.
2. **Noise.** A gas engine over a residential or commercial property is an HOA and neighbour
   problem in a way an electric multirotor is not.
3. **Water + fuel + electronics on one airframe** is a materially worse risk profile than
   batteries alone.

**The H6 Hydrone (hydrogen fuel cell) sidesteps exhaust and noise** — worth asking about — but
adds hydrogen logistics, which is its own operational world.

> **Verdict: ❌ RULED OUT — Kevin's decision, 2026-08-16.** No hybrid cleaning drone.
>
> The endurance was real, but it was buying ~14 minutes on a house (6% of the day), and the
> exhaust question was never answered. **The propulsion decision is now: all-electric, battery.**
> That also takes the **H6 Hydrone** off the table — hydrogen is not a hybrid, but it is not a
> battery either, and it carries its own fuel logistics. *(Say so if you want hydrogen kept live.)*
>
> **This closes the propulsion question. It does not change the buy list** — both recommended
> aircraft were already all-electric.

---

### Ascent AeroSystems Spirit — the compliance outlier

| | |
|---|---|
| **Blue UAS** | **The only airframe on BOTH the Blue UAS Cleared List (complete system) AND the Blue UAS Framework (vetted component)** |
| Architecture | **MOSA-ready, open-system**, modular payload interface — reconfigure payloads without re-engineering the aircraft |
| Form | Coaxial rotor; **all-weather**; takes off from any terrain |
| Capacity | **10 lb for batteries *and* payload combined** |
| Origin | US (Massachusetts) |

**Too small to clean.** Ten pounds shared between batteries and payload leaves nothing for a gun,
hose and computer.

**But its dual Blue listing is the strongest compliance position of anything screened**, and
*all-weather* is interesting for a **scout** — our scan window is already narrow
(`FIELD_OPERATIONS.md` §2.1), and an aircraft that flies in conditions the X10D won't could widen it.

> **Verdict: 🔬 not a cleaner. Possible bad-weather scout.** Low priority.

---

### The complete field

| Aircraft | Role | Integrable | Compliance | Verdict |
|---|---|---|---|---|
| **Skydio X10D** | Scout | ✅ | ✅ Blue Cleared | ⭐ **BUY** — ~$16K |
| **Inspired Flight IF1200A** | Cleaner | ✅ open PX4 | ✅ Blue **+ Green** | ⭐ **BUY** — ~$32K |
| Freefly Alta X Gen2 | Cleaner | ✅ Auterion SDK | ⚠️ ETP lapsed Feb 2026 | Backup — best onboard-app story |
| Watts PRISM Sky | Cleaner | ✅ Auterion | ⚠️ Blue unconfirmed | Backup — rails top *or* bottom |
| ~~Harris Aerial H6 Hybrid~~ | Cleaner | ⚠️ | ⚠️ | ❌ **RULED OUT** — no hybrid (Kevin, 16 Aug) |
| ~~Harris H6 Hydrone~~ | Cleaner | ⚠️ | ⚠️ | ❌ Out under the same all-electric rule |
| Ascent Spirit | Scout | ✅ MOSA | ✅✅ **dual Blue listing** | 🔬 All-weather scout only; too small to clean |
| Parrot ANAFI USA | Scout | ⚠️ limited | ✅ Blue | Budget scout |
| Custom PX4 build | Cleaner | ✅ total control | ⚠️ your sourcing | Later — you own airworthiness |
| **Anzu Raptor / Raptor T** | — | ⚠️ | ⚠️ mixed | ❌ **Discontinued Feb 2026** |
| Lucid Sherpa | Cleaner | ❌ no API | ✅ | ❌ The thing we left |
| DJI M350 / M400 | Cleaner | ⚠️ PSDK only | ❌ **Covered List** | ❌ Closed |
| Apellix | Cleaner | ⚠️ vendor-closed | ✅ US | ❌ Industrial tanks, not façades |

---

### What actually decides this — ranked

After screening thirteen platforms, the ranking of what matters is **not** what a spec sheet
leads with:

1. **Will the vendor support a liquid spray payload?** ⚠️ Disqualifies faster than any spec.
   Water, electronics and rotors is not a camera gimbal.
2. **Compliance you can point at** — Blue listing or documented >65% US content. One of only two
   FCC exemptions, and **both expire 1 Jan 2027**.
3. **Openness** — can our code reach the actuators and read telemetry?
4. **Endurance** — matters ~6% on a house, ~1 hour on a commercial job.
5. **Payload** — barely matters. A tethered rig needs 3–5 kg, and everything here clears it.

**Payload capacity is the spec every vendor leads with and the one that matters least to us.**
That is what the water tether bought.

### ✅ DECIDED — propulsion

**All-electric, battery only. No hybrid, no combustion.** (Kevin, 2026-08-16.)

Rationale, recorded so it doesn't get re-litigated:

- **Exhaust over freshly cleaned glass and solar** was never resolved, and solar is the most
  failure-sensitive surface we touch. Depositing combustion products on a panel you just cleaned
  inverts the whole product.
- **The endurance gain was small where we actually work** — ~14 min of a 3.7 h house job.
- **Noise** over residential and commercial property is an HOA and neighbour problem.
- **Fuel + water + electronics** on one airframe is a worse risk profile, and we own the
  airworthiness of any self-integration.

Both recommended aircraft — **Skydio X10D** and **Inspired Flight IF1200A** — are already
all-electric, so **the buy list is unchanged.**

**The endurance problem doesn't go away; it moves to the ground.** Batteries and a fast charger
are the answer (`FIELD_OPERATIONS.md` §5.1), and at 43 min the IF1200A needs only ~2 swaps on a
house job. Buy enough batteries that swapping never blocks the job.

<a id="docsdecisionspurposebuiltscan"></a>

---

# Deep dive — every purpose-built cleaning drone, and why none of them fit

> **Source file:** `docs/decisions/PURPOSE_BUILT_SCAN.md`

## Deep dive — every purpose-built cleaning drone, and why none of them fit

> *"Do a deep dive and find a drone that fits perfectly with what I want."*
>
> This is the search I should have run before recommending a self-integration. Screened
> 2026-08-16 across **every** purpose-built cleaning-drone manufacturer I could identify.

---

### The finding, up front

**Not one purpose-built cleaning drone manufacturer publishes an SDK, an API, or any third-party
software integration path. Not one.**

That is not a gap in my search. **It is the structure of the industry.** Every maker of a cleaning
drone is trying to own the intelligence layer themselves, because the intelligence layer is where
the value is. They will sell you the aircraft. They will not let your software drive it.

**So "a cleaning drone that fits perfectly" does not exist to be bought.** The closest thing is an
open general-purpose airframe with our payload on it — which is the IF1200A recommendation, now
supported by evidence rather than assumption.

---

### Every maker, checked

| Manufacturer | Where | Electric? | Sells the aircraft? | Integration path | Verdict |
|---|---|---|---|---|---|
| **Lucid Bots** — Sherpa | Charlotte, NC | ✅ | ✅ $75K / $2,950 mo | ❌ **No API.** Autonomy in-house; acquired an AI company | ❌ |
| **Apellix** — Power/Soft Wash | Jacksonville, FL | ✅ **8 batteries + 2 rapid chargers** | ✅ **B1 $34K · X1 tethered $79K** | ❌ None documented — **and they sell competing AI software** | 🔬 Worth one call, lower odds |
| **Foxtech** — AeroClean | China | ✅ | ✅ | ❌ DJI PSDK only | ❌ 100–200 bar, DJI-mount |
| **Spinoff Robotics** — ALICE, METRON | Singapore | ✅ tethered | ❌ **Managed service only** | ❌ You never own hardware | ❌ Competitor, not supplier |
| **Aerones** | Latvia | — | — | — | ❌ **Drone projects on hold indefinitely** |
| **Aquiline Drones** | Hartford, CT | ✅ | ✅ | ⚠️ not surfaced | 🔬 Unscreened |
| **Kärcher** | Germany | — | — | ⚠️ not surfaced | 🔬 Unscreened |
| **Kite Robotics** | Netherlands | — | — | ⚠️ not surfaced | 🔬 Window-focused |
| **SIR Robotics** | — | — | — | ⚠️ not surfaced | 🔬 Unscreened |
| **Skyline Robotics** — Ozmo | US/Israel | — | ❌ crane-mounted, not a drone | — | ❌ Different machine |
| **SkyWash · DRONEWASH+ · MWE · Alpha Drones** | US | — | equipment/services | ❌ | ❌ Operators, not platforms |

**Market context:** Apellix's Power Wash Drone is **the most widely deployed commercial cleaning
drone worldwide** — active operators in 21 countries across 5 continents. Lucid's Sherpa is the
most deployed in **North America** — 400+ operators, 40+ states. Those two are the category.
Neither will let our stack in.

---

### ⭐ The one worth a phone call: Apellix

Everything about Apellix fits **except** the integration path, and unlike Lucid there is reason to
think that is negotiable.

| | Apellix |
|---|---|
| Origin | **US — Jacksonville, Florida** |
| Power | ✅ **All-electric.** 8 batteries + 2 rapid chargers shipped with each drone, ~32 min per battery — **explicitly designed for continuous all-day operation** |
| Products | Power & Soft Wash (up to 4,000 PSI, 11 GPM) · Spray Painting & Coating · CBRN Decon |
| Pressure | "**Up to** 4,000 PSI" implies a variable range that should reach our 1.8–7 bar soft-wash band — **needs confirming** |
| Model | **Sells the aircraft.** B2B equipment sales, customers build businesses on them |
| Deployment | **Most widely deployed cleaning drone in the world** |
| Integration | ❌ **No API/SDK documented** |

#### Why they might say yes where Lucid says no

- **Their positioning is software-controlled aerial robotics**, not "a drone with a hose." That is
  philosophically our argument.
- **They are not racing us.** Lucid raised $20M explicitly to build "America's leading exterior
  cleaning platform" and is shipping autonomy (Lavo AI, Avianna acquisition). Apellix shows no such
  play — which makes an intelligence partner *complementary* rather than competitive.
- **Their battery architecture already solves our field problem.** 8 batteries and 2 rapid chargers
  per aircraft is exactly the answer to the swap burden, shipped as standard.
- **They are smaller.** Smaller companies do bespoke integrations.

#### 💰 Apellix pricing — found

| Configuration | Price |
|---|---|
| **B1 — battery, base model** | **$34,000** |
| **X1 — tethered** | **$79,000** (includes power station + 300 ft of wire) |
| Drone + accessories | $47,000–$75,000 |
| Complete startup package (incl. ~$30K window-capable ground equipment) | **$75,000–$105,000** |

Financing is offered. **Add-ons:** Night Flight LED bar · **Soft-wash Ball Valve** ·
**Apellix Intelligence (AI) Premium** · Certified Parachute System · Extended Warranty.

#### B2 specifications

| | Apellix B2 Power & Soft Wash |
|---|---|
| Pressure | Up to **4,000 PSI** — ⚠️ **minimum not published** |
| Flow | Up to **11 GPM** |
| Power | Battery, **8 high-capacity batteries included** |
| Max height | 195 ft / 60 m |
| Weight | 21.5 lb bare · **55 lb all-up class** |
| **Payload** | **25 lb** |
| Autonomy | **"Obstacle detection and front distance hold"** |

**Two things stand out.** *Front distance hold* is **standoff hold** — one of the airborne items
on our own BOM, already solved. And a **Soft-wash Ball Valve** being a catalogue option means
soft-wash is a supported mode, not an improvisation.

#### ⚠️ But: they sell "Apellix Intelligence — Autonomous cleaning software"

This materially lowers the odds of a partnership, and it is the honest downgrade to my
enthusiasm last turn.

**Apellix is building the intelligence layer too.** It is a priced add-on described as
*autonomous cleaning software*. That puts them on the same trajectory as Lucid — and it means
PROPWASH would not be a complementary partner but **a competitor to a product they already sell.**

The call is still worth making. The odds are now lower than I implied.

#### 💵 Price comparison — closer than expected

| | Apellix B1 | Inspired Flight IF1200A |
|---|---|---|
| Aircraft | **$34,000** | **$32,000** |
| Cleaning payload | ✅ **included and proven** | ➕ ~$3,000–$6,000 in parts |
| Integration labour | ✅ none | ➕ ours |
| **All-in for a working cleaner** | **~$34,000** | **~$37,000+** |
| Batteries | ✅ 8 + 2 rapid chargers | ➕ extra |
| Standoff hold | ✅ front distance hold | ➕ we add a rangefinder |
| **Our software can drive it** | ❌ | ✅ |
| Blue UAS | ⚠️ unconfirmed | ✅ Blue + Green |

**Apellix is cheaper, all-in, for a working cleaning drone.** The entire premium on the IF1200A
buys one thing: **the right to run our own stack.**

Given `GO_NO_GO.md` concluded the software *is* the company, that is the right trade — but it is a
much narrower call than it looked, and it turns almost entirely on question #2 below.

#### The three questions to ask them

1. **What is the minimum controllable pressure**, and can it be commanded — not just set by hand?
2. **Will you expose any control or telemetry interface** to a software partner: MAVLink,
   serial, an API, anything?
3. **Will you support a customer-integrated sensing payload** on the aircraft?

> **If Apellix answers yes to #2, they become the recommendation.** It would give us a purpose-built,
> all-electric, US-made, field-proven cleaning aircraft *and* an integration path — the perfect fit
> that does not otherwise exist.
>
> **If they answer no, the IF1200A stands**, and now on evidence: we asked the whole category.

---

### Why the category is closed — and why that is good news

Every one of these companies is doing the same thing: selling the *machine* while keeping the
*decisions*. Lucid keeps autonomy in-house. Apellix publishes no API. Spinoff won't even sell you
hardware — they fly it for you.

**They are all protecting the same thing we are building.** That is the strongest possible evidence
that the intelligence layer is the valuable part.

It also means the moat is not "we have a special drone." **Nobody has a special drone.** The moat is
that we are the only ones who will have the per-surface model, the safety-gated prescription, the
audit trail and the verification loop — and we can put it on any airframe that lets us in.

**That is why the airframe must be open, and why the open one is a general-purpose heavy lifter.**

---

### Where this lands

| | |
|---|---|
| **Buy** | **Inspired Flight IF1200A** — ~$32K, all-electric, Blue + Green certified, open PX4, 43 min |
| **Before that** | **Call Apellix.** One conversation, three questions. It is the only path to a purpose-built aircraft our stack can drive |
| **Ruled out** | Lucid (no API) · Foxtech (pressure + DJI) · Spinoff (service only) · Aerones (on hold) · hybrids (Kevin, 16 Aug) |
| **Still unscreened** | Aquiline Drones · Kärcher · Kite Robotics · SIR Robotics — smaller odds, worth a look if Apellix says no |

> `TODO(PROPWASH): call Apellix before ordering the IF1200A. Three questions, one call, and it
> either changes the recommendation or confirms it.`

<a id="docsdecisionscleaningdroneplatform"></a>

---

# Decision Note — Cleaning Drone Platform

> **Source file:** `docs/decisions/CLEANING_DRONE_PLATFORM.md`

## Decision Note — Cleaning Drone Platform

> ⚠️ **SUPERSEDED IN PART (2026-08-16).** The "own the stack" recommendation below
> (DJI M350/M400 + Foxtech AeroClean) is no longer viable: DJI went onto the **FCC Covered
> List** in December 2025, so new models cannot be imported or sold in the US, and federal
> contractors may not operate them on federally funded work. See
> **`INTEGRABLE_PLATFORM.md`** for the current platform decision. Pricing and
> tethered-vs-untethered analysis here remain valid.

> **Status:** OPEN — this is the highest-risk assumption in the project (CLAUDE.md §7).
> **Type:** Hardware + integration-strategy decision. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `CLAUDE.md` §4 (inventory), §7 (Lucid integration paths), §10 (operator model) ·
> `docs/DYNAMIC_PRESSURE_HARDWARE.md` (PSM/IHM) · `docs/IP_PROTECTION.md`.
>
> ⚠️ Prices/specs below are from vendor and third-party marketing (July 2026) and are
> **UNVERIFIED** — confirm with each vendor before buying. Competitor knocks sourced from a
> rival's own blog are flagged; treat them skeptically.

---

### 0. The insight that reframes the whole decision

**The cleaning-drone choice is not really about PSI or price — it decides which integration
path (CLAUDE.md §7) is even available to you, and therefore whether your hardware IP
(PSM/IHM, `DYNAMIC_PRESSURE_HARDWARE.md`) can ever be built.**

- **Buy a Lucid Sherpa → you are locked to Path A** (work-order integration). Lucid controls
  the aircraft and keeps autonomy in-house (they acquired Avianna); **no public developer
  pump/control API is confirmed.** You cannot bolt your own pressure/nozzle hardware onto it
  without their cooperation. Safe, supported, vendor-friendly — but a ceiling on your IP.
- **Build on a DJI + third-party cleaning payload → Path B/C becomes possible** because you
  own and control the whole stack. This is the only path on which your PSM/IHM pressure/
  nozzle IP can actually be integrated — but you become the integrator and take on the
  warranty, FAA-airworthiness, and liability responsibility (CLAUDE.md §7 Path C).

So read every option below through: *"which integration path does this buy me, and what does
that do to my IP and my risk?"*

---

### 1. The market — three categories

#### A. Purpose-built commercial cleaning drones (turnkey, supported)

| Drone | Price (verify) | Pressure | Notes |
|---|---|---|---|
| **Lucid Bots Sherpa** | **$75,000** outright, or **$2,950/mo** (Lucid Refresh, incl. maintenance) | up to 4,500 PSI, 300+ sqft/min | Purpose-built for commercial contractors. Up to 150 ft. Soft-wash / pressure / window-squeegee payload. Radar collision 0.5–50 m. 1 pilot + 1 ground. Most-deployed in NA (400+ operators, $75M operator revenue, $20M Series B). **This is what CLAUDE.md §4 already specs.** |
| **Apellix Power Wash** | from **$47,000** (loaded ~$71,500) | 4,000 PSI, 8–10 gpm | Aimed at **industrial** (tanks, marine, infrastructure, painting/coating), tethered or battery+tether. Per Lucid's (biased) comparison, its tethered design limits maneuverability around complex building geometry — **not ideal for residential/commercial facades**. Cheaper, but wrong market for PROPWASH. |

#### B. DIY retrofit — DJI enterprise drone + third-party cleaning payload (own the stack)

| Component | Price (estimate — confirm) | Notes |
|---|---|---|
| **DJI Matrice 350 RTK** | ~$12–15K | Proven enterprise platform, omnidirectional sensing, RTK. |
| **DJI Matrice 400** | ~$15–20K | Newer (2025-gen), higher payload/endurance. |
| **Foxtech AeroClean P3 (T50)** payload | contact vendor | Tethered cleaning for M350/M400. **20 MPa default, up to 40 MPa (~400 bar!)**, reach 45 m (latest 120 m), **800 m²/h**. Facades, solar panels, insulators, towers. |
| **Foxtech AeroClean T-M400C** | contact vendor | **Dual tether (power + water)** for M400. 8 h continuous, 1.2 kg spray gun, 80 m hose, 110–160 bar, heights to 60 m. |
| **drone-payload RT-AP3** | contact vendor | For M300/M350 RTK / M400. 1.3 kg payload, facades / glass curtain wall / solar / wind turbines. |

**All-in estimate: ~$25–45K** — likely cheaper than a Sherpa, tethered high-pressure, **and
it's the only path that lets you own the aircraft and integrate your own PSM/IHM hardware.**

#### C. Not a fit (noted so we don't chase them)
Window-only squeegee bots, wind-turbine specialists (Aerones-class), and pure industrial
coating rigs — different market than San Diego residential + light commercial.

---

### 2. Tethered vs. untethered — the real trade-off

| | **Tethered** (water ± power from ground) | **Untethered** (battery + onboard tank) |
|---|---|---|
| Endurance | ✅ Continuous, 24/7, no battery swaps | ❌ Short — weight + tank → frequent refills |
| Pressure | ✅ Higher possible (lighter craft; up to ~400 bar on Foxtech) | ⚠️ Limited by payload weight |
| Coverage | ✅ Up to 800 m²/h large-area | ⚠️ Better for small/mid jobs |
| Maneuverability | ❌ Tether management; harder around complex geometry | ✅ Free movement, fast setup, good around facades/roofs |
| Altitude | ❌ **FAA caps tethered at ~140–150 ft AGL** | ✅ Higher AGL possible (still Part 107) |
| Setup cost/complexity | ❌ Higher (ground pump, hose reel, crew) | ✅ Lower startup, faster deploy |
| Best for | High-rise, large-area, continuous industrial | **Residential + light commercial, complex geometry** |

**Read for PROPWASH:** your market is coastal San Diego **residential + light commercial** —
mostly 1–3 stories, complex geometry (roofs, solar arrays, windows, gutters, stucco).
Maneuverability and fast setup matter more than 24/7 high-rise endurance. That leans
**untethered or a short-tether hybrid**, not a full high-rise tethered rig. The 140 ft
tethered cap is irrelevant to you (you're not doing high-rises) — but the tether's
*maneuverability penalty* around a cut-up residential roofline is a real cost. A **ground-fed
water hose without a power tether** (untethered flight, tethered water) is often the sweet
spot: onboard battery for agility, ground water for pressure/endurance without a heavy tank.

---

### 3. Third-party equipment deep dive (the retrofit path)

This is CLAUDE.md §7 **Path C** — a companion/payload on hardware you own. What it unlocks vs.
what it costs:

**What it unlocks (why it's strategically huge for PROPWASH):**
- **Your PSM/IHM hardware IP becomes buildable.** You can mount your electronic
  pressure-set module + nozzle-selector on an aircraft you own. On a Sherpa you cannot —
  Lucid controls it. This is the difference between having a hardware product line and not.
- **Path B/C software integration.** A companion computer can (within FAA/vendor limits)
  take pressure/nozzle setpoints from the orchestrator — the deeper closed-loop control the
  whole architecture is designed for.
- **Cheaper all-in** (~$25–45K vs $75K) and **no vendor lock-in / no subscription.**
- **Vendor-neutral data.** Your scan→plan→execute telemetry stays entirely yours.

**What it costs you (be honest — these are real):**
- **You are the integrator and the responsible party.** Warranty on a modified DJI is *yours*
  to manage; DJI may void coverage on a modified airframe.
- **FAA airworthiness + Part 107.** Adding a cleaning payload + companion computer is a
  modification. Operator stays in command; **any increase in flight automation needs the
  appropriate FAA pathway/waiver** (CLAUDE.md §7, §10). No covert automation, ever.
- **Liability.** A high-pressure spray system on a modified flying vehicle is a product-
  liability surface. Document the firmware ceilings, pilot override, and test logs
  (mirrors `DYNAMIC_PRESSURE_HARDWARE.md` §6).
- **Integration labor.** You own the debugging, the mounts, the calibration — real
  engineering time before it earns a dollar.

**Principle (CLAUDE.md §7):** pursue Path C **only** with proper FAA/warranty/liability review,
on hardware you own, operator genuinely in command. Prefer partnership + proper waivers over
clever circumvention.

---

### 4. Best-for-the-money verdict

| If your priority is… | Best pick | Why |
|---|---|---|
| **Turnkey, supported, lowest-risk start** | **Lucid Sherpa — subscription ($2,950/mo)** | Preserves capital (matches the lean Year-1 model), maintenance included, purpose-built, market-proven. Path A only. |
| **Own the stack + build the hardware IP** | **DJI M350/M400 + Foxtech AeroClean (or drone-payload) kit** | ~$25–45K, tethered high-pressure, unlocks PSM/IHM + Path B/C. You own the risk. |
| **Raw pressure for industrial** | Apellix | Wrong market for PROPWASH residential/commercial — skip. |

**My recommendation for PROPWASH, staged:**

1. **Year 1 — start on the Sherpa subscription ($2,950/mo), Path A.** Lowest risk, no big
   capex, get real jobs and real field data flowing (the data moat is the real asset). Prove
   the software loop and the business before touching airframe modification. This is exactly
   the CLAUDE.md §4/§7 posture.
2. **In parallel — prototype PSM/IHM on a cheap owned test rig** (not the Sherpa), per
   `DYNAMIC_PRESSURE_HARDWARE.md`, so the hardware IP advances without airframe risk.
3. **Year 2+ — evaluate the DJI + third-party retrofit as the "own-the-stack" platform**
   once (a) the business is proven, (b) you have FAA/warranty/liability review done, and
   (c) the PSM/IHM is bench-validated. That's when Path B/C and the hardware product line
   become worth the integration burden.

This keeps Year 1 cheap and legal, while deliberately building toward the owned-stack future
where the defensible hardware IP lives.

---

### 4b. Side-by-side cost model (reproducible)

Modelled in `propwash/backend/reports/drone_platform_cost.py` (`python -m
propwash.backend.reports.drone_platform_cost`). **Platform cost only** — shared running
costs (chemicals, water, labor, insurance) are identical across platforms and wash out.
All figures are **estimates to validate** (CLAUDE.md §15.5); the retrofit payload price is
the biggest unknown — tune the assumptions and re-run.

| Platform | Year 1 | Year 2 | Year 3 | Cash shape |
|---|---:|---:|---:|---|
| **Sherpa subscription** ($2,950/mo) | $35,400 | $70,800 | $106,200 | Pure opex — $0 capex |
| **Sherpa outright** ($75K + ~$5K/yr) | $80,000 | $85,000 | $90,000 | Heavy capex up front |
| **DJI retrofit + PSM/IHM** | $47,000 | $50,000 | $53,000 | ~$44K capex + ~$3K/yr |
| DJI retrofit (base, no PSM/IHM) | $43,000 | $46,000 | $49,000 | ~$40K capex + ~$3K/yr |

**Break-evens (at these estimates):**
- Owned **retrofit (+PSM/IHM) undercuts the subscription after ~16 months**, and is the
  cheapest option overall by year 2–3 (~$53K at 3 yrs vs $106K subscription).
- **Sherpa outright undercuts the subscription after ~30 months** — so if you're confident
  you'll run 3+ years, buying beats renting; below that, the subscription wins on cash.
- Retrofit capex (~$44K) is well under Sherpa outright capex ($75K).

**How to read it for a startup:** the subscription's value isn't that it's cheapest — it
**isn't** past ~1.5 years — it's that it's **$0 capex and de-risked** (maintenance included,
no integration burden) while you validate the business. The retrofit is cheapest long-run
*and* the only path that builds hardware IP, but it front-loads ~$44K and all the
integration/FAA/liability work. The model quantifies exactly what you pay for that de-risking:
roughly **$35K in year 1** to avoid a $44K capex + integration project.

---

### 4c. Which drone has the most potential?

Two different questions hide in "most potential" — answer both honestly:

- **Most near-term potential (fastest, safest path to revenue): the Lucid Sherpa.**
  Purpose-built, supported, market-proven (400+ operators, $75M operator revenue), works on
  day one via Path A. Its ceiling is that Lucid owns the aircraft and the autonomy — you can
  never deeply integrate your own hardware. It's a great *business* platform with a capped
  *IP* ceiling.

- **Most ultimate potential (highest ceiling): the owned DJI + third-party retrofit.**
  It is the **only** platform on which PROPWASH's defensible hardware IP (PSM/IHM) and the
  deep closed-loop control (Path B/C) can actually exist. It's cheapest long-run, vendor-
  neutral, and opens a **second revenue line** (selling the pressure/nozzle modules to other
  operators — `DYNAMIC_PRESSURE_HARDWARE.md`). You earn that ceiling by taking on the
  integration, FAA-airworthiness, warranty, and liability burden.

**Verdict:** the **retrofit/owned-stack platform has the most potential** — because potential
means *ceiling*, and it's the only one whose ceiling includes owning the IP and a hardware
product line. But potential ≠ the right first move. The disciplined play is **Sherpa first to
capture the business and the data moat cheaply and legally, then graduate to the owned stack**
once the business is proven and the PSM/IHM is bench-validated. Buy the near-term with the
Sherpa; build toward the ultimate ceiling with the retrofit.

---

### 4d. Payback — when each path turns cash-positive

Modelled in `propwash/backend/reports/platform_payback.py` (`python -m
propwash.backend.reports.platform_payback`): one crew's ramped revenue vs. each platform's
cash outlay. Base pricing ($12/kW), utilization ramp 35% → 60% → 75%, contribution margin
(ex-platform) 55% — **all estimates to validate**. Year-1 crew revenue at 35% util ≈ $252K.

| Platform | Payback | Cum. cash Y1 | Y2 | Y3 |
|---|:--:|---:|---:|---:|
| **Sherpa subscription** | ~1 mo | $103K | $305K | $567K |
| **Sherpa outright** | ~7 mo | $59K | $291K | $583K |
| **DJI retrofit + PSM/IHM** | ~4 mo | $92K | $326K | **$620K** |

**The finding that actually matters:** once a crew is working, **the drone platform cost is
small relative to the revenue a crew produces** — every path pays back within months and the
3-year cash spread between them (~$50K) is a rounding error against ~$1.5M of 3-year crew
revenue. **So the platform choice is a strategic/IP decision, not a cash-limiting one** — pick
it for what integration path and IP it unlocks, not to save a few thousand dollars.

Two caveats keep this honest:
- **Before revenue ramps, capex bites.** The subscription's real value is the pre-launch /
  early-ramp window: **$0 capex** protects cash while you land the first accounts. That's the
  one phase where the platform choice touches survival.
- **Sensitivity.** These revenue numbers are optimistic (from `revenue_model`, all
  goals-to-validate). At ⅓ the revenue, paybacks roughly triple — still inside ~year 1 for the
  subscription and ~1.5 years for the retrofit. The *ordering and conclusion hold* across a
  wide range; don't trust the decimals.

**Net:** the retrofit retains the most cash long-run *and* builds the IP, but the difference is
small enough that you should choose on strategy — **Sherpa subscription to protect cash through
launch, graduate to the owned retrofit once revenue is steady and the PSM/IHM is validated.**

---

### 5. Guardrails (do not violate)

1. **Operator stays in command (Part 107).** No covert automation; more flight automation
   needs an FAA pathway/waiver (CLAUDE.md §7, §10).
2. **Path A first.** Don't assume a Lucid control API exists — none is confirmed. Gate any B/C
   code behind capability checks + feature flags.
3. **Retrofit = owned hardware + full review.** FAA airworthiness, DJI warranty, and product
   liability all reviewed before any modified airframe flies a paying job.
4. **The safety layer is deterministic and authoritative** regardless of platform — solar
   pressure ceilings, keep-outs, human detection can veto any dispatch (CLAUDE.md §2).
5. **Match the tool to the market.** PROPWASH = residential + light commercial; don't buy
   high-rise industrial capability you won't use.

---

### 6. Open items

- [ ] Get real quotes: Foxtech AeroClean P3(T50) / T-M400C, drone-payload RT-AP3 (prices not public).
- [ ] Confirm DJI M350 vs M400 pricing + whether a cleaning payload voids warranty.
- [ ] Confirm the Sherpa subscription terms + what Lucid Refresh's API actually exposes (§7 OPEN).
- [ ] Decide Year-1 platform: **Sherpa subscription (recommended)** vs. jump straight to retrofit.
- [ ] Attorney/FAA review scope for any Path-C retrofit before it's more than a bench idea.

---

### 7. Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Deep dive done. Recommend **Year 1 = Sherpa subscription (Path A)**; retrofit (DJI + Foxtech/drone-payload) documented as the Year-2+ owned-stack path that unlocks PSM/IHM + Path B/C | Claude (advisory) | Awaiting Kevin's call — status OPEN. Coupling: drone choice ⇒ integration path ⇒ whether hardware IP is buildable. |

---

### Sources
- [Lucid Bots Sherpa — official](https://www.lucidbots.com/sherpa-drone)
- [Best commercial drones for building cleaning 2026 — Lucid Bots](https://www.lucidbots.com/blog/best-commercial-drone-building-cleaning) *(vendor; treat competitor claims skeptically)*
- [Lucid Bots raises $20M Series B — DroneLife](https://dronelife.com/2026/03/25/lucid-bots-series-b-autonomous-cleaning-drones/)
- [Best exterior building cleaning drones of 2026 — The Drone Girl](https://www.thedronegirl.com/2024/03/08/exterior-building-cleaning-drones/)
- [Foxtech AeroClean P3(T50) for DJI M300/M350/M400](https://www.foxtechrobotics.com/T50-Drone-Cleaning-for-DJI-M300-M350-M400-drone.html)
- [Foxtech AeroClean T-M400C tethered cleaning + power](https://store.foxtech.com/aeroclean-t-m400c-tethered-cleaning-power-solution-for-dji-m400-drone-high-altitude-building-cleaning/)
- [drone-payload facade cleaning system (M350/M400)](https://www.drone-payload.com/drone-facade-cleaning-sysytem/)
- [5 Best Washing Drones 2026 — Fly Eye](https://www.flyeye.io/5-best-washing-drones/)

<a id="docsdecisionsopenplatformintegration"></a>

---

# Decision Note — Open-Platform Integration (the "openness spectrum")

> **Source file:** `docs/decisions/OPEN_PLATFORM_INTEGRATION.md`

## Decision Note — Open-Platform Integration (the "openness spectrum")

> **Status:** OPEN — complements the DJI note; answers "how do I run my own tech on the drones."
> **Type:** Platform-openness + integration decision. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `CLAUDE.md` §2, §7, §10 · `docs/decisions/DJI_TWO_DRONE_ARCHITECTURE.md` ·
> `docs/decisions/CLEANING_DRONE_PLATFORM.md` · `docs/LUCID_OUTREACH.md`.
> ⚠️ Specs/prices from vendor marketing (July 2026), UNVERIFIED — confirm before buying.

---

### 0. Reframing "I want to bypass Sherpa's autonomy restriction"

Read the goal correctly and it's completely legitimate — read it wrong and it's out of scope.

**✅ The legitimate goal (what we build toward):** the Sherpa is a **closed** platform — Lucid
keeps autonomy in-house and exposes no developer control API, so PROPWASH is stuck at Path A
and can never run *its own* tech on the aircraft. The fix is **not to hack a closed drone** —
it's to **choose an open, developer-friendly platform where your tech is a first-class citizen
by design.** That's picking the right partner architecture, and it's what this note maps.

**❌ The line we do not cross (CLAUDE.md §7, §10):** we do **not** build anything whose premise
is concealing autonomous operation from a manufacturer or circumventing Part 107. Even on a
fully open platform, **increased flight autonomy requires the appropriate FAA pathway/waiver,
and the operator stays in command until then.** Openness gives you the *ability* to build
autonomy legally; it does not exempt you from the FAA. Payload autonomy (pressure/nozzle,
Tier-1 safety-gated) is available now; autonomous *flight* is a separate, regulated step.

**Two honest routes to escape the Sherpa's closedness:**
1. **Convince Lucid to adhere to your tech** — a partnership / API access (Lucid Refresh),
   which is the transparent path (`docs/LUCID_OUTREACH.md`). Having your own open stack is
   *leverage* in that conversation.
2. **Choose an open platform** (below) where integration is welcomed, not fought.

---

### 1. The openness spectrum (the core framework)

| Tier | Example | What you can integrate | Trade-off |
|---|---|---|---|
| **Closed** | **Lucid Sherpa** | Nothing — Path A work orders only | Supported/turnkey, but your tech is locked out |
| **Semi-open** | **DJI + Payload SDK** | Custom payloads + some mission control | Best price/capability; DJI owns the flight core + NDAA concentration risk |
| **Open commercial** | **Freefly Astro, Skydio X10** | Payloads + deep SDK (MAVSDK / APIs) | US-made, NDAA-safe, developer-first; pricier, less turnkey |
| **Fully open** | **PX4 / ArduPilot custom build** | The ENTIRE autonomy stack (MAVLink) | Total control; you're the aircraft integrator = all airworthiness/FAA/liability |

**The insight:** the further right you go, the more of your own tech runs on the aircraft —
and the more responsibility you own. Sherpa is as far left as it gets (that's the frustration);
your PSM/IHM + closed-loop control need at least **semi-open**, and "run everything through my
tech" points at **open commercial or fully open.**

---

### 2. MAVLink / MAVSDK — the open "tech between them"

For any open platform, the communication standard is **MAVLink** (the lightweight open
messaging protocol drones/ground-stations/payloads speak) and **MAVSDK** (Dronecode's SDK:
C++, **Python**, Swift, Kotlin bindings). This is the open-stack equivalent of DJI's Cloud
API/PSDK — and it's **vendor-neutral**: the same MAVSDK code talks to PX4, ArduPilot, and
Freefly Astro. So an open stack lets PROPWASH's backend speak to the drone through an **open,
non-proprietary protocol you fully control** — exactly the "communicate through our tech" goal.

---

### 3. Open platform options

#### Freefly Astro — the open-commercial sweet spot ⭐
- **US-made** commercial drone (NDAA hedge vs DJI). **Smart Dovetail** standard payload
  interface + **Pixhawk Payload Bus**; uses **MAVSDK**. Any compliant payload works on any
  compliant drone — so your **PSM/IHM cleaning payload** (or a thermal scout payload) can be
  built to a published standard.
- This is the platform CLAUDE.md §5's *original* planning assumed (Sentera 6X on a Freefly
  Astro). The instinct was right — it's open, supported, and US-made.

#### PX4 / ArduPilot — fully open, you own everything
- Open-source autopilot stacks + MAVLink/MAVSDK. Build a custom heavy-lift airframe + cleaning
  payload + your PSM/IHM, and you own the *entire* autonomy stack. Maximum integration and no
  vendor lock-in — but you become the aircraft manufacturer for airworthiness/FAA/liability.

#### Skydio X10 / X10D — open, autonomy-first, US
- US, NDAA-compliant, best-in-class autonomous navigation; open platform with APIs/ICDs and
  **custom attachment** specs (mechanical/electrical/power). Excellent **scout** (autonomous
  inspection); Skydio does **not** make a cleaning drone, so it's a scout option, not a cleaner.

---

### 4. Scout vs. cleaner on open stacks

- **Scout (scan):** Freefly Astro + thermal/RGB payload, or Skydio X10 (autonomous inspection).
  Both US-made, both feed the pipeline via MAVSDK/API.
- **Cleaner (execute):** there is **no off-the-shelf open cleaning drone** — you build one:
  an open heavy-lift airframe (Freefly-class or custom PX4) + a cleaning payload (Foxtech/
  drone-payload or custom) + your PSM/IHM over the Smart Dovetail / Payload Bus. This is
  Path C, fully owned — more work than the DJI retrofit, but maximum openness + US hedge.

---

### 5. How PROPWASH stays vendor-neutral (so the platform is swappable)

The whole point of the interface discipline: **support DJI *and* open stacks behind one
boundary**, so the platform choice (and any future policy change) is a swap, not a rebuild.

```
Orchestrator → ExecutionTransport (already exists)
                 ├─ WorkOrderTransport      (Path A — Sherpa/operator)      ✅ built
                 ├─ DjiPayloadTransport      (Path B/C — DJI PSDK)   flagged, to build
                 └─ MavlinkPayloadTransport  (Path B/C — PX4/Freefly) flagged, to build
```
A new `MavlinkPayloadTransport` (an `ExecutionTransport` speaking MAVSDK) sits beside the DJI
one — both behind `PROPWASH_ENABLE_PATH_B/C`. The safety layer (Tier 1) validates every
setpoint before either transport actuates. Your tech is the constant; the drone is the plug-in.

---

### 6. Guardrails (firm)
1. **No hacking closed hardware; no concealing autonomy; no circumventing Part 107** (§7, §10).
2. **Operator in command** until an FAA waiver authorizes more automation — on *any* platform.
3. **Payload autonomy ≠ flight autonomy.** MAVSDK/PSDK can command the payload (safety-gated);
   autonomous flight is separate and regulated.
4. **Safety layer authoritative (§2)** — vetoes any unsafe setpoint regardless of transport.
5. **Vendor-neutral interfaces** — MAVLink is open and portable; don't hard-code any vendor.

---

### 7. Recommendation

- **Pragmatic now:** DJI + PSDK (semi-open) — best price/capability, covered in the DJI note.
- **Open + US hedge (the "run everything through my tech" answer):** **Freefly Astro** for an
  open, supported, US-made platform with a standard payload bus + MAVSDK; **PX4/ArduPilot** if
  you want to own the entire stack. Both escape the Sherpa's closedness *legitimately*.
- **Build a `MavlinkPayloadTransport`** beside the DJI one so the backend speaks the open
  protocol; keep everything flagged until FAA/liability review.
- **In parallel, run the Lucid conversation** — an open stack is your leverage to get Lucid to
  adhere to your tech if you'd rather partner than build.

Escape the closed platform by **choosing openness**, not by fighting a locked one — and keep
the interfaces vendor-neutral so you're never trapped again.

---

### 8. Open items
- [ ] Freefly Astro price + payload-bus power/data specs for a cleaning payload.
- [ ] MAVSDK payload-control capability check for the pump/nozzle setpoints we need.
- [ ] FAA waiver scope for any beyond-operator automation (per platform).
- [ ] Decide: DJI (semi-open, cheap) vs Freefly/PX4 (open, US hedge) — or support both.

### 9. Decision log
| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Reframe "bypass Sherpa" → choose an OPEN platform (not hack a closed one); map the openness spectrum; recommend DJI-now / Freefly-PX4 as the open+US path; build a MAVSDK-based ExecutionTransport; keep interfaces vendor-neutral. Part 107 line firm. | Claude (advisory) | Awaiting Kevin — status OPEN |

---

### Sources
- [PX4 Autopilot](https://github.com/PX4/PX4-Autopilot) · [Dronecode / MAVSDK / MAVLink](https://dronecode.org/projects/)
- [PX4 vs ArduPilot comparison](https://thinkrobotics.com/blogs/learn/px4-vs-ardupilot-complete-comparison-guide-for-drone-developers)
- [Freefly Astro — US-made commercial drone](https://freeflysystems.com/astro) · [Freefly payloads / Smart Dovetail](https://freefly.gitbook.io/astro-public/other-user-manuals/freefly-payloads)
- [Skydio developer tools](https://www.skydio.com/developer-tools)

<a id="docsdecisionsdjitwodronearchitecture"></a>

---

# Decision Note — All-DJI Two-Drone Architecture

> **Source file:** `docs/decisions/DJI_TWO_DRONE_ARCHITECTURE.md`

## Decision Note — All-DJI Two-Drone Architecture

> **Status:** OPEN — a strong candidate architecture; revises the CLAUDE.md §4 hardware base.
> **Type:** Platform + system-architecture decision. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `CLAUDE.md` §2 (tiers), §4 (inventory), §6 (loose-sync), §7 (integration paths),
> §10 (operator) · `docs/decisions/CLEANING_DRONE_PLATFORM.md` · `docs/decisions/SPECTRAL_SENSING_DECISION.md`
> · `docs/3D_DATA_PIPELINE.md`.
> ⚠️ Prices/specs from vendor/third-party marketing (July 2026), **UNVERIFIED** — confirm before buying.

---

### 0. The architecture in one picture

```
  DJI SCOUT DRONE (scan)                    DJI CLEAN DRONE (execute)
  Matrice 4T: thermal + RGB + zoom          Matrice 350/400 + cleaning payload
        │                                          ▲
        │ geotagged thermal+RGB                    │ work order + coverage path
        ▼                                          │ (pressure/nozzle setpoints, flagged)
  ┌──────────────────────────────────────────────────────────────┐
  │  PROPWASH BACKEND  (the tech that connects them)               │
  │  NodeODM reconstruct → thermal registration → segmentation     │
  │  → prescriptions (safety-gated) → COVERAGE / FLIGHT PATH        │
  │  Tier-1 safety layer · Tier-2 orchestrator · Tier-3 agents      │
  └──────────────────────────────────────────────────────────────┘
        ▲  DJI Cloud API (MQTT)                    │  DJI Payload SDK
        │  telemetry / imagery in                  │  payload control out
        └──────────────────────────────────────────┘

  ⚠ The two drones NEVER talk to each other directly (CLAUDE.md §6).
    They loose-sync through the PLAN. The "communication tech" is the
    PROPWASH backend + the DJI SDK endpoints — not a real-time drone link.
```

---

### 0b. The moat is the MIDDLE, not the drones

Anyone can buy a DJI scout and a DJI cleaning rig — the hardware is **commodity**. What no
competitor can buy is **the connective tech between them**: the software that ingests the
scout's imagery, **generates the 3D model, extracts every surface and its condition, and
computes the flight path that drives the cleaner.** That middle layer is what makes PROPWASH
unique and hard to copy:

- **Model generation + surface detail** — thermal-onto-mesh registration, the surface/asset
  classifier trained on *your* field data, the conservative safety fusion, the grime proxy.
  (`3D_DATA_PIPELINE.md` Stages 2–3; `IP_PROTECTION.md` §2 — patent the loop, trade-secret
  the brain.)
- **The scan→plan→flight-path bridge** — prescriptions from your calibrated tables, the
  safety gate, the coverage path. Two commodity drones, loose-synced into one closed loop by
  *your* code.
- **The data flywheel** — every job sharpens the classifier and the tables. A copycat with
  identical DJI drones still starts at zero data (`IP_PROTECTION.md` §3).

**So the hardware choice (this doc) should optimize for cost/capability and for *feeding the
middle* — never mistake the drones for the product.** The drones are swappable behind
interfaces (§6); the middle is the company.

---

### 1. Why all-DJI is a coherent bet

- **One SDK ecosystem end to end.** Scout, backend, and cleaner all speak the same DJI
  protocols (Cloud API + Payload SDK + Mobile SDK). Cleaner than the current split of
  **Autel (sensing) + Lucid (cleaning, closed)** — where Lucid keeps autonomy in-house and
  exposes no confirmed control API (CLAUDE.md §7).
- **It's the only path that unlocks your hardware IP.** A DJI clean drone + Payload SDK is
  the platform on which your PSM/IHM pressure/nozzle module can actually be built and
  commanded (`CLEANING_DRONE_PLATFORM.md` §0). On a Sherpa you can't.
- **Mature developer stack.** DJI Cloud API is MQTT-based and production-proven (v1.0 → v1.11+,
  2022→2024), with Dock automation for later scaling.

---

### 2. Best DJI SCOUT (scan) drone

Your scout must do **thermal + RGB photogrammetry in one aircraft** (thermal-forward per
`SPECTRAL_SENSING_DECISION.md`).

| Option | ~Price | Thermal | RGB / photogrammetry | Verdict |
|---|---:|---|---|---|
| **DJI Matrice 4T** ⭐ | **$7,849** | FLIR Boson+ (improved NETD → better solar hot-spots) 640×512 | 4/3 CMOS + 200× zoom + laser rangefinder | **Recommended scout** — thermal+RGB+zoom+LRF in one compact SDK-native aircraft |
| Matrice 350/400 + **Zenmuse H30T** | $$$ | **1280×1024** IR + 3,000 m LRF + NIR aux | 48 MP + 34×/400× zoom | Higher-end; better thermal res if you need it, pricier |
| **Matrice 4E** | ~$6–7K | none | **61 MP mechanical shutter** — best pure RGB geometry | Only if you split thermal/RGB into 2 payloads/flights (not ideal) |
| Mavic 3 Thermal | ~$5K | 640×512 | 20 MP | Budget/compact; less zoom/robustness |

**Recommendation: DJI Matrice 4T (~$7,849).** It replaces the Autel EVO II 640T with a newer,
SDK-native platform: same-class thermal but better NETD (sharper solar hot-spots + moisture),
plus zoom and a laser rangefinder for scale (helps the glass/panel reconstruction limits in
`3D_DATA_PIPELINE.md` §2d). Thermal-forward, one aircraft, one ecosystem.

*(This would update CLAUDE.md §4: Autel EVO II 640T → DJI Matrice 4T for the sensing role.)*

---

### 3. Best DJI CLEAN (execute) drone

Covered in depth in `CLEANING_DRONE_PLATFORM.md` — the DJI-native path is:

**DJI Matrice 350 RTK or Matrice 400 + third-party cleaning payload** (Foxtech AeroClean /
drone-payload) **+ your PSM/IHM via Payload SDK.** ~$25–45K all-in. This is CLAUDE.md §7
**Path C** (own the stack): it unlocks the hardware IP and deep control, but you own the
warranty, FAA-airworthiness, and liability. Operator stays in command (Part 107).

---

### 4. The communication tech (what PROPWASH builds)

This is the heart of your question — and the good news: **most of it already exists in the
repo.** The DJI ecosystem just provides the on-drone endpoints; PROPWASH provides the brain.

#### The DJI SDK surfaces we'd use
- **Cloud API (MQTT)** — scout uploads imagery/telemetry to the backend; clean-drone streams
  execution telemetry back. Two modes: Pilot-to-Cloud (manual/operator) and Dock-to-Cloud
  (automated, later).
- **Payload SDK (PSDK v3)** — build/command the cleaning payload (and the PSM/IHM
  pressure+nozzle module). This is the endpoint the Cleaning agent's setpoints reach — **after**
  the Tier-1 safety layer validates them.
- **Mobile SDK / Waylines** — fly the scout's automated survey mission and (later, with FAA
  waivers) the clean drone's coverage path.

#### What PROPWASH builds on top (mostly done)
- **Reconstruct → surfaces → flight path** — `geometry/` + `fusion/` + `segmentation/` +
  planning (Stages 1–5). Already built and tested (scan → classified zones → safety-gated
  work orders). The coverage path (Stage 5) is the "flight path toward the surfaces" you want.
- **Two new adapters** (behind existing feature flags):
  - `DjiCloudAdapter` — MQTT ingest of scout imagery/telemetry + clean telemetry.
  - `DjiPayloadTransport` — an `ExecutionTransport` (Path B/C) that speaks PSDK to the
    cleaning payload. Mirrors the existing `WorkOrderTransport` / `VendorApiTransport` /
    `CompanionTransport` pattern; **flagged off** until FAA/warranty/liability review.

#### Two things that MUST stay true (CLAUDE.md)
1. **Loose-sync, not a live link (§6).** The drones sync through the *plan*, not a real-time
   drone-to-drone connection. The clean plan is the sync point. This is a feature — it's what
   makes the system robust and legal.
2. **Operator in command (§7, §10).** PSDK lets you command the *payload* (pressure/nozzle —
   Tier-1 safety-gated). It does **not** entitle autonomous *flight* — that needs the FAA
   pathway/waiver. Never conflate payload control with self-flying.

---

### 5. How this solves the whole tech stack (your ask)

> "…from scanning to having the geodata presented so the algorithm produces all the necessary
> surfaces as well as the flight path toward these surfaces."

| Your requirement | Where it's solved | State |
|---|---|---|
| Scout collects data | DJI M4T + waylines (Mobile SDK) | Buy + configure |
| Engine builds the geodata | NodeODM/Metashape (`3D_DATA_PIPELINE.md` §2d) | Buy + wire `SfmSource` |
| Present geodata to our algorithm | `geometry/source.py` → mesh/point cloud | ✅ Built (interface + synthetic) |
| Produce all the surfaces | `segmentation/` (surfaces + exclusions) | ✅ Built + tested |
| Produce the flight path to surfaces | Stage 5 coverage path (offset shell, sweeps, keep-outs) | Designed; not yet coded |
| Communicate scout ↔ cleaner | PROPWASH backend + DJI Cloud API/PSDK adapters | Backend ✅; DJI adapters to build |

So the remaining net-new work is: (a) wire the real `SfmSource` (NodeODM reader), (b) build
the Stage-5 coverage-path code, and (c) the two DJI adapters. Everything else is done.

---

### 6. ⚠️ The one big risk to weigh: DJI concentration / regulatory

Betting **both** drones on DJI concentrates risk in a single vendor that faces real US
regulatory headwinds (NDAA / proposed "Countering CCP Drones" restrictions, potential FCC/
procurement bans). For a US business, if DJI gets restricted, **your entire stack is exposed
at once.** Mitigations to keep in mind:
- **Abstraction saves you.** Keep the `GeometrySource` and `ExecutionTransport` interfaces
  vendor-neutral (already the design). If DJI is ever restricted, you swap adapters, not the
  whole system.
- **NDAA-compliant / Blue-UAS alternatives exist** (e.g., Anzu Robotics — DJI-tech licensed,
  US-assembled; Skydio; Freefly) — pricier, but a hedge if you sell to gov/regulated clients.
- **Don't hard-code DJI assumptions** past the adapter boundary.

This doesn't kill the all-DJI plan — DJI is the best price/capability today — but go in with
the abstraction discipline so a policy change is a swap, not a rebuild.

---

### 7. Recommendation

**Target architecture: all-DJI two-drone, PROPWASH as the connective tissue. Adopt it in
stages, keeping every vendor behind an interface.**

1. **Now — switch the scout to the DJI Matrice 4T** (~$7,849). SDK-native, better thermal
   NETD, one ecosystem. Low-risk, immediate, and it starts the DJI stack. (Updates §4.)
2. **Year 1 cleaning — still start on the Sherpa subscription (Path A)** to get revenue and
   the data moat cheaply/legally (`CLEANING_DRONE_PLATFORM.md` §4d), OR go straight to the
   DJI retrofit if you're ready to own the integration/FAA/liability. The cost model says
   platform choice isn't cash-limiting once a crew works — so decide on IP appetite.
3. **Build the two DJI adapters + Stage-5 coverage path** behind feature flags, in parallel.
4. **Year 2+ — graduate cleaning to the DJI M350/M400 + PSDK + PSM/IHM** once the business
   is proven and the FAA/warranty/liability review is done. That completes the all-DJI stack
   and turns on your hardware IP.

Net: the scout goes DJI immediately (cheap, better, starts the ecosystem); the cleaner
graduates to DJI when you're ready to own Path C. The interfaces make it safe either way.

---

### 8. Guardrails
1. **Loose-sync via the plan (§6)** — no real-time drone-to-drone link.
2. **Operator in command (§7, §10)** — PSDK commands the payload, not autonomous flight;
   more automation needs an FAA waiver. No covert automation.
3. **Safety layer is authoritative (§2)** — validates every pressure/nozzle setpoint before
   PSDK actuation; can veto any dispatch.
4. **Vendor-neutral interfaces** — `GeometrySource` / `ExecutionTransport` keep DJI swappable
   (regulatory hedge, §6).
5. **Path C only after review** — FAA airworthiness, DJI warranty, product liability.

---

### 9. Open items
- [ ] Confirm DJI Matrice 4T price/availability + thermal spec vs the H30T for our needs.
- [ ] Confirm DJI Cloud API + PSDK v3 support the payload control we need (pump/nozzle).
- [ ] Get real quotes for the M350/M400 cleaning payload (Foxtech / drone-payload).
- [ ] Assess DJI NDAA exposure for your client mix (residential = low; any gov/commercial?).
- [ ] Decide scout swap now (Autel → M4T) — update CLAUDE.md §4 if yes.

### 10. Decision log
| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Recommend all-DJI two-drone target architecture; scout → M4T now, cleaner → DJI+PSDK+PSM/IHM Year 2+; keep vendor-neutral interfaces; flag DJI NDAA concentration risk | Claude (advisory) | Awaiting Kevin — status OPEN. Communication = PROPWASH backend + DJI Cloud API/PSDK, loose-synced via the plan (§6). |

---

### Sources
- [DJI SDK guide — Enterprise Insights](https://enterprise-insights.dji.com/blog/dji-sdk-guide)
- [DJI Cloud API docs](https://developer.dji.com/doc/cloud-api-tutorial/en/)
- [DJI Payload SDK v3](https://developer.dji.com/payload-sdk/)
- [DJI Matrice 4T vs 30T vs Mavic 3T — Global Drone HQ](https://globaldronehq.com/blogs/news/dji-matrice-4t-vs-matrice-30t-vs-mavic-3t-thermal-drone-comparison-2026)
- [DJI Enterprise buyer's guide 2026 — Global Drone HQ](https://globaldronehq.com/blogs/news/dji-enterprise-drone-buyers-guide-2026-every-platform-compared)
- [Foxtech AeroClean for DJI M300/M350/M400](https://www.foxtechrobotics.com/T50-Drone-Cleaning-for-DJI-M300-M350-M400-drone.html)

<a id="docsdecisionssensorplatformshortlist"></a>

---

# Decision Note — Sensor Platform Shortlist

> **Source file:** `docs/decisions/SENSOR_PLATFORM_SHORTLIST.md`

## Decision Note — Sensor Platform Shortlist

> **Status:** OPEN — awaiting Kevin's call.
> **Type:** Hardware decision record (the survey / mapping drone only — NOT the cleaning drone).
> **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `docs/3D_DATA_PIPELINE.md` §0b, §8 · `CLAUDE.md` §4 (hardware inventory), §5 (honesty rule).

This note is the running shortlist for **which drone captures the survey data** that feeds
the fusion pipeline. It is a decision *record*, not a spec — update the status line when a
choice is locked, and reflect it into `CLAUDE.md §4`.

---

### The decision in one line

**The thermal sensor is the crown-jewel input, and it is 640×512 radiometric on every
option below — identical.** So this decision is about the *survey platform around the
thermal camera* (RGB/photogrammetry quality, obstacle avoidance, mission automation),
**not** about improving grime-detection data. Frame every trade-off through that lens.

---

### Shortlist (ranked for PROPWASH's survey role)

#### 1. Autel EVO MAX 4T **V2** — *recommended if buying fresh* (verified specs, July 2026)

**V2 confirmed specs:** 48MP 1/2" CMOS wide camera · 8K zoom (10× optical / 160× hybrid) ·
**thermal 640×512 radiometric**, 13mm lens, 16× digital zoom, −4°F to 1022°F · **laser
rangefinder 5–1200 m, ±1 m** · **RTK module option** · 42 min flight · 720° obstacle avoidance ·
SkyLink 3.0 (20 km).

**Why it fits PROPWASH specifically:** thermal and RGB are on the **same gimbal**, so they are
**co-registered** — same pose, same instant. That materially simplifies Stage-2 thermal
registration (no cross-flight alignment), which is the hardest part of painting temperature
onto the mesh. With the RTK option the mesh gains survey-grade georeferencing, improving
standoff accuracy and the area math behind the ROI report.

**⚠️ Correction — Autel is NOT an NDAA hedge.** Autel Robotics is Shenzhen-based and faces
broadly similar US regulatory scrutiny to DJI. Do **not** buy Autel to diversify away from the
DJI concentration risk flagged in `DJI_TWO_DRONE_ARCHITECTURE.md` §6 — it does not achieve
that. (Freefly / Skydio are the genuine US/NDAA hedges.) Buy Autel on sensor merit.

**⚠️ SDK is the open question.** Autel's developer ecosystem is thinner than DJI's. Lower risk
for a *scout* (we mainly need geotagged imagery + poses out), but send the Integration
Qualification Questionnaire — especially **Q1, Q2, Q4, Q8** — before buying. If imagery and
telemetry can't be pulled programmatically, the "seamless pipeline" degrades to manual SD-card
transfers.

---

#### 1b. Autel EVO MAX 4T (original) — *superseded by V2*
- **Thermal:** 640×512 radiometric (same as EVO II).
- **RGB:** 50 MP wide (larger sensor) + up to ~160× hybrid zoom.
- **4th sensor:** **Laser rangefinder** (single-point, ~5–1200 m) — **NOT LiDAR** (§0b).
- **Obstacle avoidance:** omnidirectional — the biggest real-world win flying close to buildings.
- **Automation:** modern SDK + repeatable mission planning (automated survey flights).
- **Cost (verify):** ~$9K+.
- **Best when:** buying fresh, want the strongest survey platform + safety margin near structures.

#### 2. Autel EVO II Dual 640T (V3) — *current inventory; keep if already owned*
- **Thermal:** 640×512 radiometric (identical crown-jewel channel).
- **RGB:** 8K / ~48 MP.
- **4th sensor:** none.
- **Obstacle avoidance:** basic.
- **Automation:** older SDK.
- **Cost (verify):** ~$6–7K.
- **Best when:** already owned — thermal data won't improve by upgrading, so keep flying it
  and spend the money on the PSM prototype + IP instead.

#### 3. LiDAR aircraft (e.g., DJI Matrice 350 + Zenmuse L2) — *future, only on concrete need*
- **Geometry:** true scanning LiDAR → dense point cloud directly (no SfM needed).
- **4th sensor / thermal:** different payload ecosystem; thermal via separate H20T-class payload.
- **Cost (verify):** ~$15–20K all-in — a different aircraft entirely.
- **Best when:** heavy tree occlusion, survey-grade geometry on tall/complex commercial,
  night/low-light, or faster turnaround genuinely become bottlenecks. Not Year 1. (§8)

---

### What actually differs (survey role)

| Factor | EVO II Dual 640T | EVO MAX 4T | Matters to us? |
|---|---|---|---|
| Thermal (grime proxy) | 640×512 radiometric | 640×512 radiometric | **Tie — the key channel is identical** |
| RGB → photogrammetry | 8K / ~48 MP | 50 MP wide, larger sensor | MAX 4T → better SfM mesh |
| Zoom (defect spotting) | limited | up to ~160× hybrid | MAX 4T → spot individual panels/cracks |
| Laser rangefinder | none | 5–1200 m (single-point) | MAX 4T → SfM scale + live standoff |
| Obstacle avoidance | basic | omnidirectional | **MAX 4T → real safety win near buildings** |
| Automated missions | older SDK | modern SDK / mission planning | MAX 4T → repeatable survey flights |
| Platform age / support | 2020–21 gen | current gen | MAX 4T → longer runway |
| Price (verify) | ~$6–7K | ~$9K+ | EVO II cheaper |

*(All specs/prices are UNVERIFIED — confirm with Autel before purchase.)*

---

### Recommendation

- **Buying fresh, no money committed → EVO MAX 4T.** Not for thermal (it's a tie) but for
  omnidirectional obstacle avoidance flying near buildings, better RGB→photogrammetry, zoom
  inspection, and automated survey missions.
- **Already own the EVO II Dual 640T → keep it, don't rush.** Thermal (your key channel) is
  identical; upgrade only when RGB quality, obstacle avoidance, or mission automation become
  actual bottlenecks. Early dollars are better spent on the PSM bench prototype + IP.
- **True LiDAR → future only,** on a concrete need, behind the `GeometrySource` interface
  (`SfmSource` / `SfmWithLrfSource` / `LidarSource`). (§8)

---

### Guardrails (do not violate regardless of platform)

1. **No Autel option is LiDAR.** The MAX 4T's 4th sensor is a *laser rangefinder* (single
   point), not a scanning point cloud. 3D reconstruction stays **photogrammetry (SfM)**
   either way. (§0b)
2. **Honesty (CLAUDE.md §5).** Never write "LiDAR" in a spec, patent, or pitch while flying
   a rangefinder — same overclaim trap as "multispectral biofilm detection." If we want to
   *say* LiDAR, we must *fly* LiDAR.
3. **Survey drone ≠ cleaning drone.** This decision is about the sensing/mapping aircraft
   only. The Sherpa cleaning drone stays operator-piloted under Part 107 (CLAUDE.md §7/§10).
4. **Pipeline is source-agnostic.** Stage 2+ consumes a point-cloud/mesh abstraction, so
   swapping platforms is a Stage-1 change. Don't hard-code platform assumptions downstream.

---

### Open items before locking the decision

- [ ] Confirm current Autel pricing + availability (EVO MAX 4T **V2**, EVO II Dual 640T V3).
- [ ] **Send Autel the Integration Qualification Questionnaire (Q1/Q2/Q4/Q8)** — confirm
      programmatic export of imagery + telemetry before purchase.
- [ ] Price the **RTK module** — survey-grade georeferencing materially improves mesh accuracy.
- [ ] Confirm the MAX 4T laser rangefinder is exposed in the SDK (for live-standoff use).
- [ ] Decide: are we already committed to / do we already own the EVO II Dual 640T?
- [ ] If MAX 4T is chosen → update `CLAUDE.md §4` hardware inventory to match.
- [ ] Confirm automated survey missions are within our Part 107 operating comfort/authorizations.

---

### Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Shortlist drafted; recommendation = MAX 4T if buying fresh, else keep EVO II | Claude (advisory) | Awaiting Kevin's call — status OPEN |

<a id="docsdecisionsspectralsensingdecision"></a>

---

# Decision Note — Spectral Sensing for Mold / Dirt / Biofilm Analysis

> **Source file:** `docs/decisions/SPECTRAL_SENSING_DECISION.md`

## Decision Note — Spectral Sensing for Mold / Dirt / Biofilm Analysis

> **Status:** OPEN — this resolves the biggest open question in the project (CLAUDE.md §5).
> **Type:** Sensor capability + IP decision. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `CLAUDE.md` §5 (the multispectral caveat — this note answers it), §11 (IP) ·
> `docs/3D_DATA_PIPELINE.md` · `docs/decisions/SENSOR_PLATFORM_SHORTLIST.md`.

This is the note that decides whether PROPWASH can make **real spectral claims** about
mold/dirt/biofilm — or must keep treating them as an inferred *proxy*. So read §1 first;
it reframes the question honestly before we spend money.

> **🧭 KEVIN'S STEER (2026-07-06):** *"I am looking at more thermal. It doesn't need to be
> exact."* This narrows the decision decisively toward a **thermal-forward, proxy-first**
> approach — **CLAUDE.md §5 Option A**, not the expensive multispectral platform. See the
> updated recommendation in §5a. The multispectral options below are retained as a
> **documented future upgrade**, not a Year-1 purchase.

---

### 1. The honest reframe — what "spectrum analysis of mold and dirt" actually means

Two hard truths before we pick hardware:

**Truth 1 — "Mold" (fungal) is largely NOT spectrally detectable from a drone.** True
fungal mold has no chlorophyll, is often subsurface or in shadow, and has no clean aerial
spectral signature. What *is* spectrally detectable is the family of stuff people *call*
"mold" on a building exterior:

- **Algae / cyanobacteria** — including *Gloeocapsa magma*, the black streaks on roofs.
  These **contain chlorophyll-a** and photosynthetic pigments → **they have a real
  spectral signature** (strong NIR reflectance, red-edge absorption). ✅ Detectable.
- **Moss & lichen** — chlorophyll-bearing → detectable via the same indices. ✅
- **The moisture** that mold/biofilm needs to grow → **thermal** (evaporative cooling). ✅
- **Actual fungal mold** → not reliably, from the air. ❌ Don't claim it.

**Truth 2 — This is exactly the CLAUDE.md §5 trap.** The current Autel (thermal+RGB) can
only *infer* a grime/biofilm **proxy**. To turn that proxy into a **measured spectral
index** — and to honestly say "we detect biofilm spectrally" — you need bands the Autel
doesn't have: **Red-Edge and NIR.** That's what multispectral adds.

**So the honest product claim, once we have the right sensor, is:**
> "PROPWASH detects photosynthetic biological growth (algae, cyanobacteria, moss) and
> surface soiling using calibrated multispectral indices (NDVI / NDRE / red-edge),
> combined with thermal moisture mapping." — **not** "we detect mold" or "hyperspectral
> biofilm ID" unless the hardware in the loop actually supports it.

That honesty is not a limitation — it's legal armor (§11, and IP_PROTECTION.md).

---

### 2. The spectral ladder — four rungs, increasing capability & cost

| Rung | Sensor class | Bands | Detects (for us) | Cost class |
|---|---|---|---|---|
| 1 | **RGB** (have) | 3 (visible) | Visible staining, dust, dark streaks | $ (owned) |
| 2 | **Thermal** (have) | LWIR | Moisture, evaporative cooling, solar hot-spots | $ (owned) |
| 3 | **Multispectral** | 4–6 discrete (adds Red-Edge + NIR) | **Real algae/biofilm/chlorophyll indices (NDVI, NDRE), soiling, material hints** | $$ |
| 4 | **Hyperspectral** | 100s contiguous | Fine material ID (99% vs 80%), precise biosignatures | $$$$ |

- Rungs 1–2 = what the Autel gives → **proxy only** (CLAUDE.md §5).
- **Rung 3 (multispectral) is the sweet spot** for the mold/dirt question. Red-Edge
  (~730 nm) + NIR (~860 nm) are the bands that make chlorophyll (algae/biofilm) *pop* —
  this is the same physics precision agriculture uses to see crop stress before the eye.
- Rung 4 (hyperspectral) is the literal "full spectrum analysis," and it's meaningfully
  better at *material* classification (99% vs 80% for façade materials) — but it's
  expensive, heavy, data-heavy, false-positive-prone, and overkill for Year 1. **Document
  as future, don't buy.**

---

### 3. What multispectral actually buys us (the indices)

With Red-Edge + NIR bands we compute **measured indices**, not guesses:

- **NDVI** = (NIR − Red)/(NIR + Red) → chlorophyll presence → **live algae / biofilm /
  moss** on roofs and walls. The black roof streaks light up.
- **NDRE** (red-edge NDVI) → sensitive to **early / sparse** biological growth before
  it's visible → lets us catch biofilm *before* the customer can see a stain (a real
  sales + scheduling advantage; feeds the predictive re-soil model).
- **Soiling / dust indices** (NIR reflectance change) → **solar-panel soiling** and
  general surface dirt, quantified per zone.
- **Material hints** — different surfaces (stucco vs tile vs shingle vs glass) separate
  better in NIR than RGB alone, improving the Stage-3 segmentation.

This converts the CLAUDE.md §8 `grime_confidence` field from a **PROXY** into a
**measured multispectral index** — stronger data, stronger prescriptions, honest claims.

---

### 4. The sensor options (verified July 2026)

#### Option A — DJI Mavic 3 Multispectral (M3M) — *pragmatic entry*
- **Bands:** RGB 20 MP + Green (560), Red (650), **Red-Edge (730)**, **NIR (860)**.
- **Extras:** built-in RTK, DLS 2 irradiance sensor (sun-normalization — important for
  consistent readings across days/weather), 43-min endurance.
- **Thermal:** ❌ none.
- **Price:** ~$5,000–5,700.
- **Verdict:** cheap, capable multispectral. But **no thermal** → you'd fly it *alongside*
  the Autel (two aircraft, two flights, loose-synced per CLAUDE.md §6). Best low-cost way
  to add real biofilm detection without abandoning your thermal channel.

#### Option B — Sentera 6X Thermal Pro — ⭐ *the technically best answer*
- **One synchronized payload:** 6-band **multispectral + 20 MP RGB + 640×512 radiometric
  thermal**, captured in a single pass.
- **Mounts on:** DJI Matrice 300 / 350 / 400 (Skyport V2).
- **Why it's the "brilliant" answer:** it eliminates the hardest problem in our Stage-2
  pipeline — **registering separate thermal and multispectral flights to each other.**
  One payload = one set of camera poses = thermal, multispectral, and RGB already
  pixel-aligned. Algae index + moisture + visible stain, all on the same mesh face.
- **This is literally the platform family CLAUDE.md §5 "earlier planning" assumed**
  (Sentera 6X). The instinct was right; we just have to commit to it.
- **Price:** significant — the Matrice 350 body (~$12–15K) + the 6X Thermal Pro payload
  (confirm quote). This is the serious-capital option.

#### Option C — MicaSense RedEdge-P — *multispectral-only, high res*
- 5 narrow bands + panchromatic, pansharpened to ~2 cm at 60 m. Excellent multispectral
  detail, no thermal. Similar role to the M3M but higher-end / integrator-oriented.

#### Option D — Hyperspectral (Headwall / Cubert class) — *future / overkill*
- 100s of bands, 99% material-ID accuracy. Expensive ($25K–100K+), heavy, complex
  processing, false-positive risk. **Not Year 1.** Revisit only if fine material
  discrimination becomes a proven product need.

---

### 5. Recommendation

**If spectral mold/dirt/biofilm analysis is genuinely core IP (Kevin says it is):**
thermal+RGB inference (CLAUDE.md §5 option A) is **not sufficient** — you must move to
**option B: add multispectral.** The question is only *how*, and it's a budget call:

1. **Best capability (if capital allows) → Option B, Sentera 6X Thermal Pro on a Matrice
   350.** One synchronized payload gives thermal + multispectral + RGB pixel-aligned in a
   single flight. This is the strongest data foundation, the cleanest pipeline, and the
   most defensible IP (real spectral indices, honestly claimed). It's also the biggest
   check.

2. **Pragmatic entry (cheaper, start now) → Option A, DJI Mavic 3M (~$5–6K) alongside the
   Autel EVO II 640T you already fly.** Two aircraft, two loose-synced flights (the Autel
   for thermal/moisture + solar hot-spots, the M3M for algae/biofilm/soiling indices).
   You get *real* multispectral biofilm detection now, at ~1/3 the cost of the Matrice
   path, at the price of registering two flights instead of one. Upgrade to the 6X
   payload later if the data proves the value.

3. **Do NOT** stay on Autel-only and keep calling it "spectral." If we don't add
   Red-Edge + NIR, we cannot honestly claim spectral biofilm detection (§1, CLAUDE.md §5).

**My lean:** start with **Option A (M3M + existing Autel)** to prove the biofilm-index
value on real jobs cheaply, with a documented upgrade path to **Option B (6X Thermal Pro)**
once the data justifies the capital. This de-risks a big purchase while immediately
unlocking honest spectral claims.

---

### 5a. ⭐ Updated recommendation given Kevin's steer (thermal-forward)

Kevin's steer — *"more thermal, doesn't need to be exact"* — **overrides the capital-heavy
lean above.** If exactness isn't required, we do **not** buy a multispectral platform in
Year 1. The right path is:

**→ Stay thermal + RGB (the Autel), lean hard on thermal, keep `grime_confidence` as an
honest PROXY.** This is **CLAUDE.md §5 Option A**, and it's the correct call when:

- Precision isn't the goal — thermal (moisture / evaporative-cooling differentials) plus
  RGB computer vision (visible staining, dark streaks) is **plenty to decide "this zone
  is dirty, clean it and verify."** We don't need a lab-grade biofilm index to prescribe
  a wash and re-scan.
- Capital is better spent on the **PSM pressure-control prototype + IP filings** than on a
  $5–15K sensor whose extra precision we don't need yet.
- The closed loop (sense → clean → **verify** → re-queue) is self-correcting: if the
  thermal proxy under-calls a zone, verification catches the residual and re-queues it.
  **Verification compensates for proxy imprecision** — that's the whole point of the loop.

**What "lean into thermal" concretely means for the build:**
- Invest in the **thermal pipeline quality** — good radiometric calibration, the
  reflection-rejection filter (`reflection_filter.py`), multi-frame per-face averaging.
  Getting *more* out of the thermal we already have beats adding a band we don't need.
- Keep the **honesty discipline**: `grime_confidence` stays labeled **PROXY**; the
  `ZoneSignature.source` validator stays locked to thermal/rgb/sfm. No spectral claims.
- **Leave the multispectral door open, cheaply:** design the `SpectralSource` seam (§8)
  now so that *if* a future job type ever needs real biofilm indices, adding a DJI Mavic
  3M later is a drop-in — not a re-architecture.

**Net:** Year 1 = thermal-forward, proxy-honest, no new sensor. Multispectral (§4) becomes
a **documented, ready-to-execute upgrade** we pull the trigger on only if a customer
segment (e.g., utility-scale solar soiling quantification) ever demands measured indices.

---

### 6. How this resolves CLAUDE.md §5

CLAUDE.md §5 left an **OPEN DECISION**: (A) accept thermal+RGB proxy for Year 1, or (B)
add a dedicated multispectral sensor for direct biofilm detection.

**This note recommends B**, because Kevin has stated biofilm/mold/dirt spectral analysis
is a core requirement. Consequences to propagate when the purchase is made:

- Update `CLAUDE.md §5` OPEN DECISION → resolved to B (with the chosen option).
- Update `CLAUDE.md §4` hardware inventory to add the multispectral platform.
- The `ZoneSignature.source` enum (`models/zone.py`) currently **blocks** any non-
  thermal/rgb/sfm source. **Add `MULTISPECTRAL` (and index sub-fields NDVI/NDRE) once the
  sensor is real** — and not one day before, or we reintroduce the very overclaim the
  validator exists to prevent.
- `grime_confidence` can graduate from **PROXY** to a **measured multispectral index**
  (keep the proxy path for thermal-only flights via the Autel).

---

### 7. IP implications (this is why it matters beyond data quality)

- **Real spectral detection = honest spectral claims = stronger, defensible IP.** With
  multispectral in the loop we can (truthfully) describe multispectral biofilm/soiling
  detection in patents and marketing — something CLAUDE.md §5/§11 explicitly forbids
  while only the Autel is present. Honesty widens what we're *allowed* to claim.
- **The calibrated index→prescription mapping stays a trade secret** (IP_PROTECTION.md
  §2): exactly which NDRE value on which surface triggers which chemical/pressure is
  calibrated from our field data. Buy the sensor; keep the calibration secret.
- **Early-detection = scheduling moat.** NDRE catches biofilm before it's visible →
  predictive re-clean scheduling (the living digital twin) → subscription stickiness.
- **Do not overclaim "mold."** Say "photosynthetic biological growth + moisture
  conditions." Overclaiming fungal-mold spectral ID is both false and a liability (§1).

---

### 8. Architecture / pipeline impact

- The pipeline is already **source-agnostic** (`GeometrySource` interface, `3D_DATA_PIPELINE.md`
  §8). Add a parallel **`SpectralSource`** concept feeding Stage 2/3: multispectral bands
  register onto the same mesh faces as thermal, producing per-face NDVI/NDRE.
- **Single-payload (Option B) is far easier here:** thermal + multispectral share camera
  poses → no cross-flight registration. **Two-aircraft (Option A) requires** aligning the
  M3M flight to the Autel flight via shared ground control points / the SfM mesh — doable
  (the mesh is the common frame, per CLAUDE.md §6 loose-sync), but it's real work in
  `thermal_registration.py`'s multispectral sibling.
- Irradiance normalization (DLS sensor on the M3M / 6X) matters: index values must be
  sun-corrected to be comparable across visits — essential for the soiling-rate model.

---

### 9. Open items before locking the decision

- [ ] Confirm budget envelope: Matrice 350 + 6X Thermal Pro quote (Option B) vs. M3M
      ~$5–6K (Option A).
- [ ] Decide capital appetite: buy the best now (B) or prove value cheap then upgrade (A→B).
- [ ] Confirm we keep/own the Autel EVO II 640T for the two-drone Option A path.
- [ ] Attorney: confirm what spectral claims we may make once multispectral is in the loop.
- [ ] On purchase: update CLAUDE.md §4 + §5, add `MULTISPECTRAL` to `models/zone.py`.
- [ ] Confirm Part 107 coverage for the added platform / any automated survey missions.

---

### 10. Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Initial analysis surfaced Option B (multispectral) as the max-capability path | Claude (advisory) | Superseded by Kevin's steer same day |
| 2026-07-06 | **Kevin's steer: thermal-forward, "doesn't need to be exact" → CLAUDE.md §5 Option A** (stay Autel thermal+RGB proxy; multispectral = future upgrade) | Kevin | See §5a. Recommend closing §5 as **Option A** once confirmed |

---

### Sources
- [DJI Mavic 3M specifications — DJI Ag](https://ag.dji.com/mavic-3-m/specs)
- [DJI Mavic 3 Multispectral — Advexure](https://advexure.com/products/dji-mavic-3-multispectral)
- [Sentera 6X Sensor](https://senterasensors.com/6x/)
- [MicaSense RedEdge-P — Wingtra](https://wingtra.com/mapping-drone-wingtraone/drone-sensors/micasense-rededge-p/)
- [Red-edge / chlorophyll-a algae detection — Frontiers in Remote Sensing](https://www.frontiersin.org/journals/remote-sensing/articles/10.3389/frsen.2025.1633491/xml)
- [Multispectral vs hyperspectral façade material classification — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0926580522000371)
- [Multispectral vs Hyperspectral imaging — Anvil Labs](https://anvil.so/post/multispectral-vs-hyperspectral-imaging-key-differences)
- [Aerial imaging-based solar PV soiling detection — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11821171/)

<a id="docsdecisionsbuildspec"></a>

---

# DEFINITIVE — the drone, the add-ons, and why

> **Source file:** `docs/decisions/BUILD_SPEC.md`

## DEFINITIVE — the drone, the add-ons, and why

> **Kevin:** *"Give me a definitive answer of what drone company we can use to integrate our tech
> stack… and what add-ons if we use a drone without cleaning — which might be the way to go.
> We can add on Foxtech."*
>
> **Answer: yes, buy a bare drone and add the cleaning yourself — but NOT a Foxtech kit.**
> Reason in §2, and it is a number, not an opinion. Screened 2026-08-16.

---

### 1. THE ANSWER

| Decision | Choice |
|---|---|
| **Flight OS** (commit here first) | **Auterion** — AuterionOS + Auterion SDK |
| **Drone company** | **Freefly Systems** — Alta X Gen2, **NDAA SKU** |
| **Aircraft cost** | **~$45,000** |
| **Cleaning add-on** | **Build a soft-wash payload. Do NOT buy a high-pressure kit.** |
| **Water** | **Ground-tethered.** Pump, regulator and chemistry stay on the ground |
| **Backup airframes** | Watts PRISM Sky · Inspired Flight IF1200A — both Auterion/PX4, both NDAA |

**Why Freefly specifically:** Auterion Enterprise PX4 on Skynode, MAVSDK control from the ground
*or* from a companion computer, an internal payload bay with **Ethernet + regulated power + LTE**,
15.9 kg payload, US-made. It is the largest-payload aircraft that runs the OS our software targets.

**Why Auterion first:** because Freefly, Watts and others all run it. Write the integration once,
and the airframe becomes re-sourceable. That is the structural fix for what Lucid did to you — no
vendor can switch you off.

---

### 2. ⭐ Why NOT Foxtech — the number that decides it

**Foxtech's AeroClean kits run 110–200 bar. Our own prescriptions run 1.8–7 bar.
We are a soft-wash system. They are a high-pressure system. It is a 20–30× mismatch.**

Our surface table (CLAUDE.md §9, `prescriptions/`):

| Surface | Our prescribed pressure |
|---|---|
| Solar panel | **1.8 bar** |
| Window glass | 2.2 bar |
| Stucco | 4.0 bar |
| Clay tile / shingle | 5.0–5.5 bar |
| Gutter | 6.0–7.0 bar |

Foxtech AeroClean T-M400C: **110–160 bar**. AeroClean P3 (T50): **20 MPa = 200 bar**.

**Buying that kit would be buying a tool that operates 30× above the ceiling our own safety layer
exists to enforce.** The entire point of `safety/checks.py` is that over-pressure destroys
surfaces. Bolting on a 200-bar rig to run a 1.8-bar solar prescription is not conservative
engineering — it is putting a fire hose on a job that needs a garden sprayer, and trusting
software to never make a mistake.

#### The second-order effect: jet reaction force

A spray jet pushes the aircraft backwards. Reaction ≈ `0.0745 × gpm × √psi` (lbf):

| Configuration | Reaction | % of Alta X 35 lb payload |
|---|---|---|
| **Our tile/shingle prescription** — 5.5 bar @ 4 gpm | **2.7 lbf (12 N)** | **8%** |
| Our solar prescription — 1.8 bar @ 4 gpm | 1.5 lbf (7 N) | 4% |
| Foxtech T-M400C — 160 bar @ 4 gpm | **14.4 lbf (64 N)** | **41%, horizontal** |
| Foxtech P3 — 200 bar @ 8 gpm | **32.1 lbf (143 N)** | **92%, horizontal** |

**This is the whole reason purpose-built high-pressure cleaning drones are hard.** Foxtech's own
marketing cites "flexible joints, adaptive balancing" — that is the engineering to fight 64–143 N
of continuous thrust trying to push the aircraft off the wall.

**At our pressures that problem substantially disappears.** ~12 N of reaction on a 15.9 kg-payload
airframe is a routine control-authority question, not a research programme.

> **That is the finding that makes self-integration realistic instead of a moonshot.** We are not
> trying to build a flying pressure washer. We are trying to build a flying *soft-wash* gun, and
> those are two very different engineering problems.

#### ✅ CONFIRMED — checked Foxtech's whole catalogue, not one model

Their **entire AeroClean line is high-pressure.** There is no soft-wash option:

| Foxtech model | Pressure | Mounts on |
|---|---|---|
| AeroClean **P1 (A2)** | **20 MPa = 200 bar** | DJI M300 RTK / M350 RTK |
| AeroClean **P2 (A30)** | high-pressure | DJI heavy-lift |
| AeroClean **P3 (T50)** | **20 MPa = 200 bar** | DJI M400 |
| AeroClean **T-M400C** | **110–160 bar** | DJI M400 |
| **P4H** cleaning version | **10 MPa = 100 bar** | DJI |
| AeroClean **F30** | 10 MPa | DJI FlyCart 30 |
| AeroClean **S2 / S4** (solar) | — | DJI T-series ag drones |

**Lowest pressure Foxtech sells is 100 bar. Our highest prescription is 7 bar.**
Even their gentlest product is **14× above** the most aggressive thing we ever ask for, and
**55× above** our solar prescription.

**And every single one is DJI-mount.** This is not "adaptable with effort" — it is the wrong
pressure class on the wrong airframe.

> **Verdict on Foxtech: no.** Not "probably not" — their catalogue contains nothing in our
> pressure class, on any airframe we can buy.

#### Three more reasons Foxtech is the wrong purchase

- **DJI-specified.** AeroClean P3 (T50) and T-M400C are built for M350/M400 mounting, power and
  comms. Foxtech advertises "in-depth custom development" but publishes **no non-DJI
  compatibility**. This would be a bespoke engineering engagement, not a purchase.
- **Country-of-origin risk.** Foxtech, EAUAV, ZJIEC and Jitian are all Chinese suppliers. We chose
  a US NDAA airframe specifically to keep federally funded and institutional work open
  (`GO_NO_GO.md`). **Whether a Chinese-made payload on a US airframe preserves that eligibility is
  a legal question we have not answered.** ⚠️ Counsel, before purchase.
- **It solves a problem we don't have.** High-pressure kits exist for concrete, industrial tanks
  and heavy soiling. Our differentiation is *not* damaging surfaces.

**Where Foxtech is still worth a call:** the *mechanical* parts — gimballed gun mounts, lightweight
high-pressure hose, tether management — are genuinely hard and they have solved them. Ask whether
they will supply components decoupled from DJI. That is a much smaller ask than a full kit.

---

### 3. The build — a bare drone plus add-ons

#### 3.1 Airborne (keep it stupid)

| # | Item | Why | Notes |
|---|---|---|---|
| 1 | **Freefly Alta X Gen2 (NDAA)** | The aircraft | ⚠️ NDAA SKU only — the stock Herelink radio is **not** compliant; the Doodle Labs variant is |
| 2 | **Companion computer** in the payload bay | Runs our onboard app | Bay supplies Ethernet, regulated power, LTE. Small ARM SBC class |
| 3 | **Soft-wash gun / lance**, gimbal-mounted | Directs the spray | Rated well above 7 bar. Light — this is the whole point |
| 4 | **Lightweight supply hose** | Water from the ground | Sized for ~4–8 gpm at low pressure. Weight and drag are the design drivers, not burst rating |
| 5 | **Solenoid valve** | Pump/flow on-off at the gun | Driven by a PX4 actuator output — `PUMP_CHANNEL` in `mavlink_mission.py` |
| 6 | **Nozzle selector (IHM)** | Per-surface nozzle without landing | `NOZZLE_CHANNEL`. **Phase 2** — fly fixed nozzles first and change by hand |
| 7 | **Downward/forward rangefinder** | Standoff hold, the safety-critical measurement | Standoff is in every prescription; it must be measured, not assumed |

**Airborne total is a gun, a hose, a valve and a small computer.** No tank, no pump, no
high-pressure electronics, no 143 N thrust to fight.

#### 3.2 Ground (where the IP lives)

| # | Item | Why |
|---|---|---|
| 8 | **Soft-wash pump**, ~4–8 gpm to ~10–20 bar | Standard soft-wash equipment. Commodity, cheap, well understood |
| 9 | **Electronic pressure regulator / VFD** | **This IS the PSM** from `DYNAMIC_PRESSURE_HARDWARE.md` — it just doesn't fly |
| 10 | **Firmware pressure ceiling on the regulator** | The independent guarantee. **Must refuse an over-ceiling command in hardware**, not trust software |
| 11 | **Chemical injector / proportioner** | `chemical_mix_ratio` per zone, ground-side |
| 12 | **DI water stage** | Solar is DI-only, non-negotiable |
| 13 | **Hose reel + tether management** | The unglamorous part that decides whether a job takes 4 hours or 6 |
| 14 | **Containment / recovery** | Regulated discharge in California (`FIELD_OPERATIONS.md` §1.3) |

#### 3.3 Software — what already exists

| Layer | Status |
|---|---|
| Mission + actuator emission | ✅ `execution/mavlink_mission.py` — already the standard PX4 pattern |
| Per-surface prescription + safety gate | ✅ `planning/`, `safety/` |
| Per-face grime layer | ✅ `fusion/scan_pipeline.py` |
| MAVSDK connection | ⚠️ documented seam in `mavlink_transport.py` |
| **Onboard AuterionOS app** | ❌ **the new build** — and the differentiator (`PLATFORM_VENDOR_CHOICE.md` §1) |
| Ground pump controller | ❌ new, and buildable on a bench today |

---

### 3.4 ⭐ Where the add-ons actually come from: the agricultural sprayer ecosystem

This is the answer to "what add-ons," and it is a different industry than the one we were looking in.

**We were shopping in *facade cleaning*, which is a high-pressure industry. We should be shopping
in *agricultural spraying*, which is a low-pressure, high-flow, open-architecture industry.**

Why it fits, point for point:

| Ag sprayer property | Why it matches us |
|---|---|
| **Low pressure by design** | Ag spraying is a few bar — the same class as our 1.8–7 bar table |
| **Airframe-agnostic components** | Sold as pumps, nozzles, valves and flow sensors, **not** as a kit welded to one drone model |
| **Native flight-stack support** | **ArduPilot ships a Sprayer library** (ArduCopter 4.0+); PX4 treats sprayers as generic MAVLink actuators. Pump control is a first-class citizen, not a hack |
| **Mature and cheap** | Brushless IP67 pumps, diaphragm pumps, Y-nozzles, centrifugal and pressure nozzles, quick-connect fittings, anti-drip control — commodity parts |
| ⭐ **Ground-speed-compensated flow** | Ag spray controllers already **govern pump speed in real time from GPS ground speed to hold a constant application rate** |

#### That last row is the important one

Ag controllers solve — in shipping hardware — the problem of applying a **uniform dose while the
aircraft's speed varies**. That is exactly what `planning/coverage_path.py` needs: our
`traverse_speed_mps` and `dwell_seconds` only produce an even clean if delivered volume tracks
actual ground speed, not commanded speed.

**We were going to have to build that. We can adopt it instead**, and spend the effort on the
per-surface prescription that nobody else has.

#### The synthesis with a ground tether

An onboard ag pump is ~5 L/min (~1.3 gpm) — fine for chemicals, **thin for rinsing a building**.
But we are not carrying a pump:

- **Volume comes from the ground pump** over the tether — 4–8 gpm, commodity soft-wash equipment.
- **The airborne parts reduce to ag components**: a valve, a nozzle (or the IHM selector), and a
  flow sensor for closing the loop.
- **The ag control logic moves to the ground controller**, where it modulates the regulator.

**Airborne bill of materials, final: a gun, a hose, a valve, a nozzle, a flow sensor, a
rangefinder, a small computer.** Every one of those is off-the-shelf, and none of them is a
bespoke integration with a Chinese facade-cleaning vendor.

---

### 4. Why this beats buying a cleaning drone

| | Buy a cleaning drone (Sherpa / Foxtech kit) | Bare drone + our add-ons |
|---|---|---|
| Pressure range | Fixed at the vendor's design point | **Matched to our surface table** |
| Our code in the loop | ❌ / limited | ✅ onboard app + ground controller |
| Pressure IP | Vendor's | **Ours, on ground equipment we own** |
| Airframe swappable | ❌ | ✅ any Auterion aircraft |
| Vendor can cut us off | ✅ | ❌ |
| Airworthiness | Vendor's | **Ours** ⚠️ |
| Time to first clean | Weeks | Months |

The last two rows are the honest cost. **You are trading speed and vendor-backed airworthiness for
control and differentiation.** Given `GO_NO_GO.md` concluded the services layer is commoditising
and the intelligence layer is the business, that is the right trade — but it is a real trade.

---

### 5. Sequence — capital last

| Step | Cost | Proves | Aircraft needed? |
|---|---|---|---|
| 1 | **Ground rig**: pump + regulator + gun on a stand | low four figures | Per-surface pressure control + firmware ceiling. **The core IP.** | ❌ |
| 2 | **Auterion Skynode Developer Program + Virtual Skynode** | subscription | Onboard app, flown against the reference house in simulation | ❌ |
| 3 | **Scan-only revenue** with the Autel | Autel only | That anyone pays for the intelligence | ❌ |
| 4 | **Vendor quotes** — Freefly, Watts, Inspired Flight | free | Who supports a liquid spray payload at all | ❌ |
| 5 | **Buy the Alta X and integrate** | ~$45K + integration | The whole loop | ✅ |

**Steps 1–4 need no aircraft.** If step 3 fails, you spent a few thousand dollars and a
subscription — not forty-five thousand and an integration programme.

---

### 6. Questions that must be answered before capital

**To Freefly (and Watts, and Inspired Flight):**
1. Warranty and airworthiness position on a **customer-integrated liquid spray payload**? ⚠️ *This
   is the disqualifying question.*
2. AuterionOS version, and will you support a third-party onboard app?
3. Payload-bay power budget, actuator outputs available, and Ethernet spec?
4. Real endurance **with a tether attached and a gun running** — not the datasheet payload figure?

**To Auterion:**
5. Skynode Developer Program cost, terms, and **commercial-product licensing**?
6. Does the app sandbox permit **actuator/payload commanding**, or only motion commands?

**To Foxtech / EAUAV:**
7. Will you supply **gun, gimbal mount and hose as components**, decoupled from DJI — and do you
   have anything in the **soft-wash (< 20 bar) range** rather than high-pressure?

**To counsel:**
8. Does a **Chinese-manufactured payload on a US NDAA airframe** preserve federal-contract
   eligibility? ⚠️ This may rule out Foxtech and EAUAV entirely.

**To an insurer:**
9. Premium for a **self-integrated spray drone** versus a vendor-supported one? *Still the number
   most likely to decide this, and still unasked.*

> `TODO(PROPWASH): needs Kevin + Freefly + Auterion + counsel + insurer before capital.`

---

### 7. One-line summary

**Freefly Alta X Gen2 (NDAA) on Auterion, with a soft-wash gun on a ground tether — not a Foxtech
high-pressure kit, because we prescribe 1.8–7 bar and they build 110–200 bar.**

<a id="docsdecisionscleaningmethods"></a>

---

# Cleaning methods beyond spraying — and what "Raptor" actually is

> **Source file:** `docs/decisions/CLEANING_METHODS.md`

## Cleaning methods beyond spraying — and what "Raptor" actually is

> *"Explore other drones like the Raptor drone — is this something we utilize for cleaning the
> surfaces we want to clean, other than spraying?"*
>
> Screened 2026-08-16. Two separate questions, answered separately.

---

### 1. "Raptor" — it isn't a cleaning drone

**No cleaning drone called Raptor surfaced in any search.** The near-certain referent is
**Raptor Maps**, and it matters — but not as hardware.

**Raptor Maps is a solar asset-management analytics platform.** It builds **geospatial digital
twins of solar facilities**, fusing drone imagery, thermal inspection, SCADA and maintenance
records; runs AI thermal analytics to find module-, string- and combiner-level defects; and drives
technician workflow through a field app.

#### ⚠️ Why this is worth your attention

**Raptor Maps is the closest thing that exists to PROPWASH's intelligence layer — for solar farms.**
Digital twin, thermal analytics, issue prioritisation, defect localisation, O&M workflow.

And their own description says they automate in-field O&M "through analytics, issue prioritisation,
**and robotics**."

That is the same closing-gap risk as Lucid, approaching from the opposite direction:

| | Has | Missing |
|---|---|---|
| **Lucid** | The robot | The intelligence |
| **Raptor Maps** | The intelligence | The robot |
| **PROPWASH** | Both — for **mixed-surface buildings** | Scale, data, revenue |

**The defensible read:** Raptor Maps is deep in **utility-scale PV**, where the asset is uniform,
fixed and SCADA-instrumented. Our claim has to be **heterogeneous building envelopes** — roof,
stucco, glass, panel, gutter on one structure, each needing different treatment. That is a
different problem, and it is the one our per-surface model actually solves.

**It also reinforces `GO_NO_GO.md`:** do not pitch "AI thermal analytics for solar." That is taken,
and by a well-funded incumbent.

---

### 2. Non-spray cleaning — three real categories

#### 2.1 Contact tools on a drone (brush / squeegee) — ❌ the industry moved away

It was tried. There is even a **US patent (9,963,230)** for an aerial drone cleaning device using
a **rubber squeegee blade in sliding contact** to remove sprayed solution.

But **early prototypes used brushes and scrubbers; modern systems are touchless.** Lucid markets
the Sherpa explicitly as having *"no squeegees, brushes, or contact points that could scratch or
dent surfaces."*

**Why contact from a hovering aircraft is genuinely hard:**

- **Reaction force.** Pressing a tool against a wall pushes the aircraft off it. Same physics as
  the jet-reaction problem in `BUILD_SPEC.md` §2, but now the force is a *contact constraint* the
  flight controller must fight continuously, not a steady thrust it can trim out.
- **Ground effect near a vertical surface.** Rotor wash reflects off the wall and destabilises the
  aircraft precisely where you need it steadiest.
- **Scratch risk is the failure you least want.** On glass and solar — our two most sensitive
  surfaces — a scratch is unrecoverable. Our whole positioning is *not damaging surfaces*.

> **Verdict: no.** Contact cleaning contradicts both the physics and the brand. If a surface truly
> needs mechanical contact, that is a job for a ground robot or a human, not a drone.

#### 2.2 Waterless robotic cleaning — ✅ real, proven, and **not a drone**

**Ecoppia** is the significant one, and the numbers are serious:

| | |
|---|---|
| Method | **Rotating soft microfiber + controlled airflow. No water at all** |
| Mounting | **Permanently installed** on a frame that traverses the array |
| Power | **Self-powered** — each robot carries its own PV |
| Removal | ~99% of dust build-up |
| Deployed | **35+ utility-scale sites, 15.7 billion panels cleaned, ~1.8 billion gallons of water saved** |

**This is the dominant answer at utility scale, and it is not a drone.** Any drone-based utility
solar cleaning play competes with a permanently-installed, self-powered, water-free robot that
never needs a pilot.

**But its constraint is also its boundary:** it must be **installed on the array**. That only pays
on large, fixed, uniform installations. It cannot do a commercial rooftop with HVAC and skylights,
a mixed-surface building, or anything varied.

> **Verdict: don't compete at utility scale.** Ecoppia owns it. Our ground is **commercial rooftop
> solar and mixed-surface buildings** — too small and too varied for a permanent install, too
> heterogeneous for a pure solar robot.

#### 2.3 ⭐ Dry / low-water methods on OUR aircraft — the idea worth keeping

Here is the part of the Ecoppia insight that transfers.

**Microfiber and airflow remove 99% of *dust*.** No water. Which means: **for dry soiling, water is
not the active ingredient — it is just the carrier.**

That splits our problem in two:

| Soil type | What removes it | Water needed? |
|---|---|---|
| **Dust, pollen, mineral spotting** | Rinse, or airflow | Little — or none |
| **Moss, algae, lichen, biofilm** | **Chemistry + dwell** (15–20 min) | Yes, unavoidably |

And this maps directly onto geography: **desert solar is a dust problem; coastal roofs are a
biological problem.** Different soil, different method — not just different pressure.

---

### 3. ⭐ The real consequence: prescribe METHOD, not just parameters

Today a prescription carries **pressure, chemistry, dwell, nozzle, standoff**. It assumes the
method is always *spray*.

**It shouldn't.** Method should be the first thing prescribed, and the pipeline **already computes
the signal that decides it.**

`scan_pipeline.py` produces **`grime_proxy` and `moisture_index` separately.** Moisture comes from
the thermal differential — damp surfaces evaporate and read cooler. Dry dust does not hold water
and does not read cool.

**So the two axes are already there:**

| Grime | Moisture | Soil type | Method |
|---|---|---|---|
| High | **High** | Biological growth | **Chemistry + long dwell + rinse** |
| High | **Low** | Dry dust / mineral | **Rinse only — or dry** |
| Low | Low | Clean | Skip |

On the reference house the separation is already visible in the exported data:

```
zone            grime  moisture   reads as
SOL-ROOF         0.46      0.07   dry / dust      → rinse, no chemistry
RF-S             0.33      0.17   mostly dry
WIN-S1           0.25      0.00   dry
```

**A dirty-but-dry solar array does not need detergent. It needs DI water and a pass** — which is
exactly what the solar prescription already says, but arrived at by surface *type* rather than by
observed soil *state*.

#### Why this is genuinely differentiating

Everyone else picks method by **surface**. This picks method by **what is actually on the surface,
per patch, measured**.

It also directly attacks the biggest operational costs in `FIELD_OPERATIONS.md`:

- **Water volume** — a rinse-only pass on dry soiling uses a fraction of a full treatment
- **Containment** — less water and no detergent means far less regulated discharge
- **Dwell** — no chemistry means no 15–20 minute dwell, which is most of the job clock
- **Chemical cost and landscaping risk** — you stop applying detergent where it does nothing

> `TODO(PROPWASH): add "method" to the prescription model — dry | rinse_only | soft_wash — keyed on
> the grime × moisture quadrant. The inputs exist; nothing new needs sensing.`
> **Needs field calibration before it drives real jobs — the moisture proxy is uncalibrated.**

---

### 4. Verdict

| Method | For us? | Why |
|---|---|---|
| **Soft-wash spray** | ✅ **Primary** | Right for mixed surfaces; matches 1.8–7 bar table; touchless |
| **Rinse-only / low-water** | ⭐ **Add** | Dry soiling doesn't need chemistry. Cheaper, faster, less discharge |
| **Dry (microfiber/airflow)** | 🔬 Research | Proven by Ecoppia — but as a fixed installation, not from a drone |
| **Brush / squeegee on a drone** | ❌ **No** | Industry abandoned it. Reaction force, wall ground-effect, scratch risk |
| **Fixed rail robots (Ecoppia class)** | ❌ Not our market | Owns utility scale. We take commercial rooftop + mixed-surface |
| **High-pressure (100–200 bar)** | ❌ Not airborne | Hardscape only — ground robot's job |

**Nothing found changes the aircraft recommendation.** Skydio X10D + Inspired Flight IF1200A still
stand. What changes is that **the prescription should choose the method**, and the data to do it is
already in the pipeline.

<a id="docsdecisionscomputeinfrastructure"></a>

---

# Decision Note — Compute Infrastructure (Hybrid Local + Cloud)

> **Source file:** `docs/decisions/COMPUTE_INFRASTRUCTURE.md`

## Decision Note — Compute Infrastructure (Hybrid Local + Cloud)

> **Status:** RECOMMENDED — awaiting Kevin's purchase.
> **Type:** Infrastructure decision record. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `IP_PROTECTION.md` §3 (data moat) · `docs/3D_DATA_PIPELINE.md` §7 (data
> sovereignty) · `CLAUDE.md` §2 (tiered safety), §12 (stack).

Goal: run PROPWASH **internally** on hardware Kevin controls, keeping the trade-secret
data in-house, **without** overpaying Apple for storage or pretending Claude can run
locally (it can't — §2).

---

### 1. The one-paragraph decision

Buy a **Mac Studio, M4 Max chip, 64 GB unified memory, 2 TB internal SSD** as the internal
box. It runs photogrammetry, computer vision, the backend, the databases, local open-weight
models, and stores the crown-jewel data — all on hardware you own. Use **cloud Claude**
(via the API with commercial terms + zero-retention, or inside your own AWS Bedrock / Google
Vertex tenant) for the hard reasoning, because **Claude cannot run locally.** For bulk data,
**do not pay Apple's SSD prices** — put the growing imagery/point-cloud/dataset archive on
**external Thunderbolt 5 NVMe + a RAID NAS**, which costs a fraction per terabyte.

---

### 2. Can Claude run locally? No. (Settle this first.)

**Anthropic does not release Claude's weights.** Claude runs only on Anthropic's
infrastructure or approved clouds (AWS Bedrock, Google Vertex AI). There is no
downloadable / offline / on-prem Claude. So:

| You want | Reality |
|---|---|
| Claude's reasoning quality | **Cloud only** — API call over HTTPS |
| Something running on the Mac Studio | **Open-weight models** (Llama, Qwen, DeepSeek) — *not* Claude, weaker at hard reasoning |

"Local Claude" is a contradiction. Choose per-workload (§3).

#### Data sovereignty without local Claude
Protecting the data does **not** require Claude on your hardware. Three levels:

1. **Anthropic API, commercial terms** — Anthropic does **not** train on your API
   inputs/outputs by default.
2. **Zero Data Retention (ZDR)** — for qualifying customers, prompts/outputs aren't
   stored after the response.
3. **Claude in your own cloud tenant (AWS Bedrock / Google Vertex)** — Claude runs inside
   your VPC boundary; data stays in your account, not sent to Anthropic directly. Closest
   thing to "private Claude."

*(Confirm current Anthropic terms/ZDR eligibility before relying on them.)*

---

### 3. The hybrid architecture — what runs where

```
┌──────────────────────────────────────────────────────────────┐
│  MAC STUDIO (M4 Max, 64 GB) — your internal box, data at home │
│                                                                │
│  • Photogrammetry (OpenDroneMap SfM)                           │
│  • Computer vision (SAM / PyTorch via Metal)                   │
│  • Backend: FastAPI + PostgreSQL/PostGIS + Redis               │
│  • Tier-1 SAFETY LAYER (deterministic — always local)          │
│  • Tier-2 orchestrator (~1 Hz)                                 │
│  • Local open-weight model (Ollama) for quick/offline tasks    │
│  • CROWN-JEWEL DATA storage + the labelled dataset             │
└───────────────┬──────────────────────────────────────────────┘
                │  advisory reasoning only (API over HTTPS)
                ▼
┌──────────────────────────────────────────────────────────────┐
│  CLOUD CLAUDE (API / Bedrock / Vertex) — Tier-3 agents         │
│  • Mapping · Fusion · Supervisor · Cleaning · Post-Clean       │
│  • The hard reasoning where quality matters ("be brilliant")   │
│  • Protected by commercial terms + ZDR, or your own tenant     │
└──────────────────────────────────────────────────────────────┘
                ▲
                │  (optional) air-gapped local open model for any
                │  workload that must never touch a network
```

**Why this is safe to depend on cloud for Tier 3:** per CLAUDE.md §2, the **safety layer
(Tier 1) and orchestrator (Tier 2) are local and deterministic.** The cloud agents are
**advisory only.** If the network drops, safety and orchestration still function — only the
advisory reasoning degrades. Cloud dependency never sits in a safety loop.

---

### 4. Chip binning + memory — exact recommendation

**M4 Max, 16-core CPU / 40-core GPU, 64 GB unified memory.** Reasoning:

#### The chip bin is not optional — it's tied to the memory
Apple bins the M4 Max in two ways, and memory is gated by the bin:

| M4 Max bin | Max unified memory |
|---|---|
| 14-core CPU / 32-core GPU | **36 GB only** |
| **16-core CPU / 40-core GPU** | 36 / 48 / **64 GB** |

**To get 64 GB you *must* select the 16-core / 40-core chip** — the base 14/32 bin caps at
36 GB. So the "should I upgrade the cores?" question is already answered by the memory
decision: yes, and there's no 64 GB build without it.

#### The bigger chip also helps PROPWASH's heaviest local jobs
Even independent of memory, the upgrade speeds up exactly what this box does:
- **16 CPU cores** → faster **photogrammetry** (OpenDroneMap SfM is CPU-bound; this is the
  slowest pipeline step, so cores directly cut survey→model time).
- **40 GPU cores** → faster **computer vision** (SAM/PyTorch via Metal) and faster **local
  LLM** token generation (Ollama's Metal backend uses the GPU).

There is no sensible PROPWASH build on the 14/32 bin.

> ⚠️ **Photogrammetry-speed caveat (see `3D_DATA_PIPELINE.md` §2b).** The Mac Studio runs
> **Agisoft Metashape** (native Apple-Silicon GPU accel) fast enough for building-scale
> models (~30 min–2 h each). But the *fastest* engines — **RealityCapture, DJI Terra** —
> are **Windows + NVIDIA only** and **cannot run on the Mac Studio at all.** If job volume
> or near-real-time turnaround ever demands max speed, that's a **separate small NVIDIA GPU
> box** (RTX 4090/5090-class, ~$2–3K) for the reconstruction step only — not a Mac upgrade.
> Start Mac-only with Metashape; add the NVIDIA box later if speed becomes the constraint.

#### Memory sizing
- Unified memory is soldered — **you cannot upgrade it later.** Buy the right amount once.
- **Get 64 GB, not 36 GB.** The 36→64 GB jump is the single most important AI upgrade here.
- 64 GB comfortably runs photogrammetry + CV + backend + databases **simultaneously**, plus
  a local ~70B open model (4-bit ≈ 40 GB) when you want one.
- The M4 Max **caps at 64 GB** — going higher forces the M3 Ultra (96 GB, ~$1,500 more,
  ~800 GB/s bandwidth). **Only worth it if fast local LLM becomes a *primary* workload.**
  Since the heavy reasoning is cloud Claude here, the M4 Max 64 GB is the cost-smart pick.

| Option | Memory | When |
|---|---|---|
| ⭐ **M4 Max, 64 GB** | 64 GB cap | **This build** — hybrid, cloud does heavy LLM |
| M3 Ultra, 96 GB | 96 GB, faster | Only if running large local models fast is core |
| M4 Max, 36 GB | avoid | Too tight for concurrent AI + CV workloads |

---

### 5. Storage — internal vs external (where the real money is saved)

**Apple's internal SSD upgrades are extremely overpriced** — maxing internal storage can add
**thousands of dollars.** Don't. Split storage by how hot the data is:

#### 5a. Internal SSD — keep it modest: **2 TB**
Holds the OS, apps, local model weights (a couple of 70B models), the active databases, and
current-job working data. 2 TB is the sweet spot — 1 TB fills fast once you add local models;
4 TB+ internal is where Apple's pricing gets abusive. **Pay Apple for 2 TB, no more.**

#### 5b. Fast external (hot bulk) — **Thunderbolt 5 NVMe, ~4 TB**
The M4 Max Mac Studio has **Thunderbolt 5** (up to 120 Gb/s). A TB5 external NVMe enclosure
hits ~5–6 GB/s — fast enough to process imagery and point clouds directly off it. ~4 TB for
a few hundred dollars vs. Apple charging ~$1,000+ for the same internal bump.

#### 5c. Archive + the data moat (cold bulk) — **RAID NAS**
The **accumulating labelled dataset is the trade-secret moat** (IP_PROTECTION.md §3). It
needs redundancy and backup, not raw speed:

- A **Synology / RAID NAS** (e.g., 4-bay) gives many TB with **RAID redundancy** — a drive
  can fail without data loss. This is the permanent home for the growing dataset.
- Follow **3-2-1 backup**: 3 copies, 2 media types, 1 offsite (an encrypted cloud bucket or
  a rotated external drive).
- **Encrypt at rest** (FileVault on the Studio; encrypted volumes on the NAS) — the moat
  checklist from IP_PROTECTION.md §4.

#### Storage strategy summary

| Tier | Hardware | ~Size | ~Cost | Holds |
|---|---|---|---|---|
| Internal (hot) | Apple SSD | 2 TB | (Apple bump) | OS, apps, models, DBs, active job |
| External fast | TB5 NVMe | 4 TB | ~$300–500 | Imagery/clouds being processed |
| Archive (cold) | RAID NAS | scalable | ~$800–1,500+ | The labelled dataset moat + backups |

**Money saved vs. maxing Apple internal SSD: easily $1,500–3,000+**, redirected to the PSM
prototype / IP filings.

---

### 6. Indicative build + cost

| Item | Spec | ~Cost (verify) |
|---|---|---|
| Mac Studio | **M4 Max (16-core CPU / 40-core GPU), 64 GB, 2 TB SSD** | ~$3,000 |
| External fast storage | TB5 NVMe enclosure + 4 TB drive | ~$400 |
| Archive/backup | 4-bay RAID NAS + drives | ~$1,000–1,500 |
| Cloud Claude | API usage (pay-as-you-go) | usage-based |
| **One-time hardware total** | | **~$4,400–4,900** |

vs. a maxed M3 Ultra (512 GB former config, 16 TB internal) at **~$14,000** — for capability
this hybrid doesn't need, since cloud Claude does the heavy reasoning.

---

### 7. Guardrails

1. **Claude is never local.** Don't design any component assuming an on-prem Claude (§2).
2. **Safety stays local + deterministic.** Tier 1/2 run on the Mac Studio; cloud agents are
   advisory only (CLAUDE.md §2). Network loss must never disable safety.
3. **Encrypt the data moat** at rest + in transit; least-privilege access (IP_PROTECTION.md §4).
4. **Confirm Anthropic data terms** (no-training / ZDR / Bedrock-Vertex) before sending any
   sensitive job data to cloud Claude.
5. **Unified memory can't be upgraded** — get 64 GB up front.

---

### 8. Open items

- [ ] Confirm current Mac Studio configurator (M4 Max 64 GB / 2 TB) pricing + Thunderbolt 5.
- [ ] Choose NAS (Synology model + drive count) sized for expected job volume.
- [ ] Confirm Anthropic commercial terms + ZDR eligibility (or decide Bedrock/Vertex).
- [ ] Pick the local open model for offline tasks (Llama 3.3 70B / Qwen class).
- [ ] Set up FileVault + NAS encryption + 3-2-1 backup before first real customer data lands.

---

### 9. Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Recommend **M4 Max (16-core/40-core) / 64 GB / 2 TB** + TB5 external + RAID NAS; cloud Claude for Tier-3; Claude confirmed **not** locally runnable | Claude (advisory) | Awaiting Kevin's purchase — status RECOMMENDED |
| 2026-07-06 | Clarified: 64 GB requires the 16-core CPU / 40-core GPU bin (base 14/32 caps at 36 GB); upgrade also speeds photogrammetry + CV + local LLM | Claude (advisory) | Closes gap in §4 |

<a id="docs3ddatapipeline"></a>

---

# PROPWASH — 3D Data Pipeline Deep Dive

> **Source file:** `docs/3D_DATA_PIPELINE.md`

## PROPWASH — 3D Data Pipeline Deep Dive

### From raw drone capture → surface model → asset segmentation → cleaning flight path

> ⚠️ **Engineering strategy, not legal advice.** Where this touches FAA flight
> automation, see §9 and CLAUDE.md §7/§10 — the cleaning drone stays operator-piloted.
> The flight path this system produces is a **guidance overlay for the operator**, not
> an autonomous command stream, until Lucid + FAA pathways say otherwise.

---

### 0. The honest starting point (read this before anything else)

**The Autel EVO II 640T has NO LiDAR.** It is a **thermal (640×512 radiometric) + RGB**
platform. There is no laser rangefinder producing a point cloud directly.

So when we say "3D data" and "point cloud," we mean it comes from **photogrammetry —
Structure from Motion (SfM)** — reconstructing 3D geometry from overlapping 2D RGB
photos, **not** from LiDAR returns. This matters for three reasons:

1. **Accuracy:** SfM gives ~2–5 cm geometry on a well-flown building. LiDAR gives
   ~1–2 cm and works through partial vegetation and in low light. For cleaning
   prescription, SfM is *sufficient* — we need surface classification and standoff
   distance, not survey-grade precision.
2. **Cost:** SfM needs no new hardware. A LiDAR payload (e.g., DJI Zenmuse L2 on a
   Matrice) is $10K+ and a different aircraft. **We do not need it for Year 1.**
3. **Honesty (CLAUDE.md §5):** Don't write specs or patent claims that say "LiDAR"
   while the Autel is the only sensor. If we add LiDAR later, it's an explicit
   hardware decision (§8).

**Decision:** Year 1 = SfM photogrammetry from Autel RGB, thermal registered on top.
LiDAR is a documented future option (§8), not a current dependency.

---

### 0b. ⚠️ Laser Rangefinder ≠ LiDAR (a specific trap — read this)

There is a **newer Autel option, the EVO MAX 4T**, and it is easy to assume it "does
LiDAR." **It does not.** Its four-sensor payload (the "4T") is:

| Sensor | Approx. spec | Role |
|---|---|---|
| Wide camera | 50 MP | RGB imagery |
| Zoom camera | up to ~160× hybrid | Detail inspection |
| Thermal | 640×512 radiometric | Temperature |
| **Laser Rangefinder (LRF)** | ~5–1200 m | Distance to **one point** |

The fourth sensor is a **Laser Rangefinder**, which is **not** LiDAR. The difference is
fundamental to this pipeline:

- **Laser Rangefinder (what the MAX 4T has):** fires one beam and returns the distance
  to **a single aimed point** — "that wall is 47.3 m away." One number. It does **not**
  produce a point cloud and it does **not** build a 3D model.
- **LiDAR (what the MAX 4T does NOT have):** a *scanning* laser sweeping thousands–
  millions of points per second into a dense 3D **point cloud** directly — no
  photogrammetry required. That's a Matrice + Zenmuse L2 class payload (§8).

#### What this means for us

**Whether we fly the EVO II Dual 640T (current, CLAUDE.md §4) or the EVO MAX 4T, the 3D
reconstruction is still photogrammetry (SfM), not LiDAR.** Neither Autel produces a
laser point cloud. Stage 1 is unchanged by the MAX 4T.

What the MAX 4T's LRF *would* add if we upgraded:

1. **Better scale/georeferencing.** Single-point laser distances give SfM ground-truth
   measurements to lock the mesh scale — more accurate dimensions → more accurate
   standoff and area (feeds Stage 5 and the ROI report).
2. **Live standoff during the clean.** The LRF can stream a real-time "distance to
   surface" number, useful to the Tier-1 safety layer and the operator overlay (§5, §9).

Neither of those changes the fact that the **point cloud comes from RGB photogrammetry.**

#### Honesty rule (CLAUDE.md §5) — same trap as multispectral

Do **not** write "LiDAR" in any spec, patent claim, pitch deck, or marketing copy while
the sensor is a **rangefinder**. It is the exact same overclaim risk as calling the
thermal+RGB grime score "multispectral biofilm detection." A laser rangefinder is a
distance sensor, not a mapping sensor. If we want to *say* LiDAR, we have to *fly* LiDAR
(§8). Until then: "photogrammetry, optionally laser-rangefinder-assisted for scale."

---

### 1. The pipeline in one picture

```
   AUTEL SURVEY FLIGHT
   ├─ RGB frames (JPEG, geotagged: lat/lon/alt + gimbal angle)
   ├─ Radiometric thermal frames (R-JPEG / TIFF, per-pixel °C)
   └─ Flight log (GPS track + IMU + camera poses)
            │
     ┌──────┴───────────────────────────────────────────┐
     │  STAGE 1 — PHOTOGRAMMETRY (SfM)   [BUY]            │
     │  RGB frames → point cloud + textured mesh + ortho │
     │  Tools: OpenDroneMap / Pix4D / Metashape          │
     └──────┬───────────────────────────────────────────┘
            │  point cloud (.las), mesh (.obj), orthomosaic (.tif), DSM
            ▼
     ┌──────────────────────────────────────────────────┐
     │  STAGE 2 — THERMAL REGISTRATION   [BUILD]         │
     │  Project thermal °C onto each mesh face           │
     │  Our code: thermal_registration.py                │
     └──────┬───────────────────────────────────────────┘
            │  thermographic mesh (per-face temp + RGB texture)
            ▼
     ┌──────────────────────────────────────────────────┐
     │  STAGE 3 — SURFACE / ASSET SEGMENTATION [BUILD*]  │
     │  Classify every face: solar / window / tile /     │
     │  stucco / gutter / roof / EXCLUSION               │
     │  Our model + off-the-shelf CV backbones           │
     └──────┬───────────────────────────────────────────┘
            │  labelled zones (the ZoneSignature set)
            ▼
     ┌──────────────────────────────────────────────────┐
     │  STAGE 4 — PRESCRIPTION   [BUILD — TRADE SECRET]  │
     │  Per zone: pressure, chemical, nozzle, dwell      │
     │  Supervisor agent + calibrated surface table      │
     └──────┬───────────────────────────────────────────┘
            │  prescriptions
            ▼
     ┌──────────────────────────────────────────────────┐
     │  STAGE 5 — FLIGHT / COVERAGE PATH   [BUILD]       │
     │  Per zone: standoff surface, sweep lines,         │
     │  approach order, keep-out volumes → operator      │
     │  guidance overlay (NOT autonomous cmd, §9)        │
     └──────────────────────────────────────────────────┘
```

`[BUILD*]` in Stage 3 = we build the *labelling logic and training data* (secret), but
we stand it on off-the-shelf CV backbones (open source). See §4.

---

### 2. Stage 1 — Photogrammetry (BUY, don't build)

**Do not write our own SfM engine.** Structure-from-Motion + Multi-View Stereo is a
mature, 20-year-deep research field (bundle adjustment, feature matching, dense depth).
Building it would burn a year and never beat the incumbents. This is pure commodity
infrastructure — buy or use open source.

#### The realistic options

| Tool | Model | Cost | Runs on our servers? | Best for us? |
|---|---|---|---|---|
| **OpenDroneMap (WebODM)** | Open source (AGPL) | Free (self-host) | ✅ Yes | ⭐ **Primary choice** |
| **Agisoft Metashape** | Commercial, perpetual license | ~$3.5K one-time | ✅ Yes | Strong backup — best mesh quality |
| **Pix4Dmatic / Pix4Dmapper** | Commercial SaaS/desktop | ~$350/mo | Desktop yes | If ODM quality falls short on complex roofs |
| **DroneDeploy** | Cloud SaaS | ~$330/mo+ | ❌ Data leaves us | Avoid — data sovereignty (§7) |
| **RealityCapture** | Commercial (Epic) | PPI / sub | ✅ Yes | Fast, Windows-only |
| **Scanifly** | Cloud SaaS (solar-specialized) | subscription (contact) | ❌ Cloud | ⭐ Fast solar-focused start — see §2c |

**Recommendation: OpenDroneMap self-hosted.** It is Docker-deployable, runs on our own
GPU box or a cloud instance, keeps sensor data on our infrastructure (critical for the
trade-secret data moat, §7), and outputs everything we need:

- `odm_georeferencing/odm_georeferenced_model.laz` — the point cloud
- `odm_texturing/odm_textured_model_geo.obj` — the textured mesh
- `odm_orthophoto/odm_orthophoto.tif` — the top-down orthomosaic
- `odm_dem/dsm.tif` — digital surface model (heights)

> **Why AGPL matters:** OpenDroneMap's license (AGPL) has network-copyleft
> implications *if we distribute a modified ODM as a service to third parties*. For
> internal use processing our own jobs, we're fine. If we ever sell processing as a
> hosted service, get counsel to review — or use Metashape (perpetual license, no
> copyleft) for the commercial path. **Flag for attorney if we productize processing.**

#### What we DON'T buy from them

The SfM tool gives us geometry. It knows *nothing* about cleaning — no surface types, no
grime, no pressure. **Everything from Stage 2 onward is ours.** That's the boundary:
buy the geometry, build the intelligence.

---

### 2b. ⚡ Speed & the "seamless, fast" engine choice (READ if turnaround matters)

The §2 default (OpenDroneMap) is **free but slow** — it's the most CPU-bound option. If the
priority is a **fast, seamless survey→model turnaround** (survey in the morning, clean plan
by afternoon — or eventually near-real-time), the engine choice changes, and it collides
with the Mac Studio decision (`COMPUTE_INFRASTRUCTURE.md`). Here's the honest picture.

#### The hard tension: the fastest engines are NVIDIA/Windows, the Mac Studio is not

| Engine | Speed | Platform | Runs on Mac Studio? |
|---|---|---|---|
| **RealityCapture** (Epic) | ⭐ Fastest — **5–20× faster** than Metashape | **Windows + NVIDIA GPU only** | ❌ No |
| **DJI Terra** | Fast; ~30–40% faster than Metashape on DJI data | **Windows + NVIDIA only** | ❌ No |
| **Agisoft Metashape** | Good; **native Apple-Silicon GPU accel (M1–M4)** | Win / Mac / Linux | ✅ **Yes** |
| **OpenDroneMap** | Slowest (free) | Win / Mac / Linux (Docker) | ✅ Yes |

Reference point: a 1,000-photo project ≈ RealityCapture **2–4 h** vs Metashape **6–12 h** on
comparable hardware. **But a single house/small commercial is only ~150–400 photos**, so
Metashape does one building in roughly **30 min–2 h** depending on quality settings — which
is *plenty* for a same-day workflow. The huge RealityCapture gap matters at *volume*.

#### The decision, tied to the Mac Studio

**→ Path 1 (recommended start): Mac Studio + Metashape.** One box, everything stays in-house
(data-sovereignty moat intact), Metashape is the *only* pro engine with native Apple-Silicon
GPU acceleration, and it's **fast enough for building-scale**. Swap it in as the Stage-1
engine (buy the ~$3.5K perpetual license — no copyleft either, which also solves the AGPL
concern in §2). This is the simplest seamless pipeline.

**→ Path 2 (if speed becomes the constraint): add a small NVIDIA GPU box for Stage 1 only.**
If you scale to many buildings/day or want near-real-time, a dedicated NVIDIA workstation
(RTX 4090/5090-class, ~$2–3K) running **RealityCapture** or **DJI Terra** does the SfM in
minutes, then hands the mesh to the Mac Studio for our Stage 2–5 (thermal overlay,
segmentation, twin). Data still never leaves your hardware. This is the **max-speed** path;
CUDA simply beats Apple Silicon at photogrammetry. It's a second machine, not a Mac upgrade —
the Mac Studio can't run these engines at all.

> **Net:** start Path 1 (Mac Studio + Metashape) — fast enough, one box, data at home.
> Add Path 2's NVIDIA+RealityCapture box **only when job volume or near-real-time demands
> it.** Don't buy the NVIDIA box on day one. (This revises the §2 "OpenDroneMap primary"
> default: **Metashape is the better pick once speed matters** — keep ODM only as the
> free fallback.)

#### Gaussian Splatting / NeRF — a visual layer, NOT the measurement engine
Neural reconstruction (3D Gaussian Splatting) trains in **minutes** and looks
photorealistic — tempting for speed. **But its geometric error is ~7.8 cm vs 1–3 cm for
photogrammetry.** That's too loose for standoff distance, area, and prescription math, and
it needs an NVIDIA RTX 4090. **Verdict:** optionally use GS later as a gorgeous
*customer-facing* twin visualization, but **not** as the measurement/geometry source that
feeds Stages 3–5. Measurement stays photogrammetry.

#### Where "seamless" actually comes from (this part is ours to build)
No off-the-shelf tool chains capture → reconstruction → thermal overlay → surface
segmentation → cleaning plan into **one automated job.** That orchestration glue — kick the
engine via its CLI/API, auto-ingest the mesh, run our Stage 2–3, emit the twin, no manual
handoffs — **is our code, and it's where the "seamless, fast pipeline" is won or lost.** The
engine is bought; the *seamlessness* is built. See `propwash/backend/geometry/` +
`fusion/` in §11.

---

### 2c. Scanifly as a solar-specialized starting point (worth doing — with eyes open)

**Yes, Scanifly is a reasonable way to START Stage 1** — arguably better-aligned to your
solar wedge than the generic engines, as long as you understand exactly what it does and
does NOT do. Here's the honest split.

#### What Scanifly gives you (the geometry canvas) ✅
- **Proprietary photogrammetry + AI → a to-scale 3D model within inches**, from geo-tagged
  drone photos. This is precisely the Stage-1 reconstruction we said to *buy, not build*.
- **Works with any drone that shoots geo-tagged images** — your Autel included, no lock-in.
- **Solar-specialized**: roof planes, pitch/azimuth, obstructions, and the only drone-based
  **shade analysis approved by US regulators/lenders**. That pedigree matches your market.
- **Export + API**: 3D models export to CAD; API integrations push data to solar partners
  (Unirac, IronRidge, Pegasus). So data *can* come out — but see the caveat below.

#### What Scanifly does NOT do — this stays PROPWASH's proprietary layer ❌
- **No dirt / grime / "mold" / condition map.** Scanifly is a solar *design* tool (geometry
  + shading), not a *condition* tool. The grime layer is **yours** — thermal + RGB fusion
  (Stages 2–3). Scanifly gives the canvas; you paint the condition on it.
- **No thermal.** It's RGB photogrammetry. Your thermal registration (Stage 2) is unaffected
  and still entirely ours.
- **"Identifies mold" — no, and neither does any RGB tool.** Same honesty rule as everywhere
  (CLAUDE.md §5): what you produce is a grime/biofilm **PROXY**, not spectral mold detection.
  Scanifly won't change that; don't let its marketing imply it does.
- **Material classification beyond roof/obstructions is limited.** It gives roof planes +
  obstructions + checklist-captured structural data — not a full solar/window/siding/stucco/
  tile segmentation. Your Stage-3 segmentation still does that classification.

#### The two real caveats before committing
1. **Cloud = data-sovereignty tradeoff (§7).** Imagery and models live in Scanifly's cloud,
   not on your hardware. Your crown-jewel *condition* data (thermal + grime) never goes there
   — only the geometry does — but weigh this against the self-hosted OpenDroneMap/Metashape
   path. Acceptable early for speed; revisit as the data moat grows.
2. **Confirm you can pull the raw mesh into YOUR pipeline.** Scanifly's export is
   CAD/partner-oriented (built to feed racking vendors, not a custom cleaning pipeline). You
   need the **3D mesh / point cloud in a form Stage 2 (thermal_registration) can consume**.
   Verify this with Scanifly before relying on it — it's the make-or-break integration point.
   The `GeometrySource` interface (§8) already anticipates a `ScaniflySource` adapter here.
3. **You're paying for solar-*design* features you won't use** (racking, BOM, plan sets).
   Fine as a fast start; just know the pricing is built for installers designing new PV
   systems, not for cleaners assessing existing roofs.

#### Verdict (revised — see §2d)
Scanifly is solar-specialized and accurate, but its export is built to feed *racking
vendors*, not a custom pipeline — which makes it a **worse fit than OpenDroneMap/Metashape
for the "build geometry → layer our data → pipe it" goal you actually have.** Keep it as a
possible fast trial, but §2d is the real recommendation for a pipeline front-end.

---

### 2d. ⭐ The right front-end for "scout collects → engine builds → pipeline runs"

Your actual requirement isn't "a solar design tool" — it's an engine that **automatically
turns scout-drone imagery into clean, exportable geometry your own pipeline consumes.** That
selection filter has a clear winner.

#### The requirement, stated plainly
```
Scout drone flies → geotagged RGB (+ thermal) images
        → [ENGINE builds the 3D geometry, automatically]
        → standard mesh/point-cloud/ortho export
        → OUR pipeline layers dirt/mold/material/cleaning data on top (Stages 2–5)
```
The engine must: (a) reconstruct accurately, (b) run **hands-off via an API/CLI**, and
(c) export **open, standard formats** (OBJ/PLY mesh, LAS/LAZ cloud, GeoTIFF ortho/DSM) —
not lock the geometry inside a design app.

#### Best fit: **OpenDroneMap via NodeODM (self-hosted REST API)**
- **Purpose-built for exactly this loop**: "drone lands → images upload → processing starts
  → outputs push." NodeODM is a REST API you script; PyODM is the Python client. This is the
  automated ingest→build→export pipeline you described, out of the box.
- **Standard open exports** — `odm_texturing/*.obj`, `*.laz` point cloud, `odm_orthophoto/
  *.tif`, `odm_dem/dsm.tif` — which our Stage 2 (`thermal_registration`) already expects.
- **Self-hosted → data-sovereignty moat intact** (§7). Imagery never leaves your box.
- **Free** (AGPL — fine for internal processing; §2 caveat only if you resell processing).

#### Premium alternative: **Agisoft Metashape (Python SDK)**
- **Full batch automation via a Python API/SDK** — scriptable end to end, higher-quality
  meshes than ODM, native Apple-Silicon GPU (§2b), standard exports. ~$3.5K perpetual, no
  copyleft. Buy this if ODM's mesh quality isn't good enough on complex roofs.

#### Also-ran for a custom pipeline
- **Pix4Dengine** — real SDK/API, but pricier and more cloud-tied.
- **RealityCapture / DJI Terra** — fast but Windows+NVIDIA and less pipeline-native (§2b).
- **Scanifly / DroneDeploy** — cloud, design/partner-oriented export → **not ideal for a
  custom pipeline** despite being polished.

#### ⚠️ The honest limit: glass & solar panels do NOT reconstruct "perfectly"
No photogrammetry engine — ODM, Metashape, Scanifly, any of them — reconstructs **windows or
solar panels perfectly.** Smooth glass shows no trackable features; glossy panels throw
specular reflections; both produce **holes and noise** in the mesh. This is physics
(optically smooth glass yields no trackable features), not a tool weakness — well-established
in the photogrammetry literature.

**But you don't need perfect glass geometry — and the pipeline is already designed around
this:**
- We don't mesh the reflective *surface*; we **locate and classify the region** (window /
  panel) from RGB + thermal + the surrounding wall/roof **plane** geometry, then treat it as
  a **planar classified zone**. Stage 3 (`geometry_rules` + `fusion_decision`) already does
  exactly this — a window is a planar region in a vertical plane, a panel is a planar region
  on a roof plane. Their *extent and location* reconstruct fine; only their glossy surface
  detail doesn't, and we don't need it.
- **Capture technique mitigates the rest**: shoot at varied angles, avoid direct-sun glare
  off panels/glass, more overlap. The EVO MAX 4T's **laser rangefinder** (decision note:
  `SENSOR_PLATFORM_SHORTLIST.md`) also gives hard distances where SfM is weak.
- Gaussian Splatting looks great on glass but is metrically too loose (~7.8 cm, §2b) — visual
  only, not the measurement source.

**Takeaway:** "reconstruct everything perfectly" is the wrong bar for glass/panels — the
right bar is *locate + classify + get the plane*, which photogrammetry does well. Build for
that, and the reflective-surface problem stops being a problem.

#### Recommendation
Make **OpenDroneMap/NodeODM the Stage-1 front-end** (self-hosted REST API, standard exports,
data stays yours), with **Metashape's Python SDK** as the paid upgrade if you need better
meshes. Wire it behind the `GeometrySource` interface as the concrete `SfmSource` (§8, §11);
everything from Stage 2 on — the dirt/mold/material/cleaning intelligence — stays your
proprietary, in-house layer.

---

### 3. Stage 2 — Thermal registration (BUILD — this is ours)

The SfM tool used only the **RGB** frames (thermal isn't good for feature matching). So
after we have the mesh, we must **paint the thermal data onto it ourselves.** No
off-the-shelf tool does this well for cleaning — this is our code.

#### The algorithm

For each radiometric thermal frame:

1. **Recover the thermal camera pose.** The Autel's thermal and RGB cameras are
   rigidly mounted with a known offset (extrinsic calibration — a one-time
   measurement per airframe). Given the RGB pose from the SfM bundle adjustment,
   compute the thermal pose by applying the fixed extrinsic transform.
2. **Ray-cast each thermal pixel onto the mesh.** Using the thermal camera intrinsics
   (focal length, principal point — from a one-time checkerboard calibration) and the
   pose, project each pixel and find which mesh triangle it hits (Open3D raycasting or
   a BVH from `trimesh`).
3. **Accumulate per-face temperature.** Each face is seen by many frames from many
   angles. Store a running weighted mean (weight by view angle — a face seen head-on is
   more reliable than one at a grazing angle) + variance (variance flags inconsistent
   faces = possible occlusion/reflection artifacts).
4. **Handle thermal reflections.** Glass and solar panels reflect sky/sun IR. A face
   whose temperature variance across frames is high is flagged `THERMAL_UNCERTAIN` —
   the fusion layer down-weights grime confidence there. (This is a real, non-obvious
   problem worth a trade-secret note.)

#### Tools we lean on (libraries, not products)

- **Open3D** (BSD license) — mesh I/O, raycasting, point-cloud ops. Free, commercial-OK.
- **trimesh** (MIT) — mesh geometry, ray-triangle intersection, face areas/normals.
- **OpenCV** (Apache 2.0) — camera calibration, undistortion, frame handling.
- **NumPy / SciPy** — the math.
- **PDAL** (BSD) — point cloud translation/filtering if we work at cloud level.
- **rasterio / GDAL** — read the orthomosaic + DSM GeoTIFFs.

All permissively licensed. All commercial-safe. **None of them know anything about
cleaning — the registration logic is 100% ours and is a trade secret** (the view-angle
weighting, the reflection-rejection heuristic, the extrinsic calibration constants).

#### Repo home
```
propwash/backend/fusion/
  sfm_ingest.py            # read ODM/Pix4D outputs into our data structures
  thermal_registration.py  # THE core build — project thermal onto mesh
  reflection_filter.py     # glass/solar IR reflection rejection (trade secret)
  twin_builder.py          # assemble the DigitalTwin (already have the model)
```

---

### 4. Stage 3 — Surface & asset segmentation (BUILD the labels, BUY the backbone)

This is the question the user really asked: **how do we identify solar panels vs.
windows vs. roof tiles vs. gutters from the drone data?** Three complementary signals,
fused:

#### Signal A — RGB semantic segmentation (the workhorse)

Run a **semantic segmentation neural network** on the orthomosaic / textured mesh that
labels each pixel/face with a surface class. We do **not** invent a new architecture —
we fine-tune a proven one:

| Backbone / framework | License | Role |
|---|---|---|
| **Segment Anything (SAM / SAM 2, Meta)** | Apache 2.0 | Zero-shot region proposals — segments objects without training; we then classify the regions |
| **Ultralytics YOLO-seg** | AGPL (⚠) | Fast instance segmentation; watch the AGPL license for commercial |
| **DeepLabv3+ / SegFormer (HuggingFace)** | Apache/MIT | Fine-tune on our labelled roof dataset |
| **Detectron2 (Meta)** | Apache 2.0 | Mask R-CNN instance seg — solar panels, skylights as instances |

**The pattern:** SAM proposes regions (it's remarkably good at outlining solar arrays,
windows, roof planes with zero training). Our classifier head — trained on **our own
labelled data** — assigns each region a PROPWASH surface class. The classifier and the
labelled dataset are the trade secret; the backbone is off-the-shelf.

- **Solar panels:** highly regular dark rectangular grid, low thermal variation across
  the array, strong straight-line edges → very distinctive, easy class.
- **Windows / skylights:** specular RGB highlights + thermal edge ring (glass is a
  thermal boundary) + planar vertical (window) or planar-in-roof (skylight).
- **Roof tiles (clay/concrete/composite):** texture frequency + color + the roof plane
  orientation from the mesh; tile vs. shingle distinguished by texture periodicity.
- **Stucco:** the vertical façade planes, characteristic matte texture.
- **Gutters:** thin elongated features at roof-plane perimeters (geometric rule on the
  mesh, not just RGB).
- **EXCLUSION zones (chimneys, HVAC, vents, people):** protrusions in the mesh +
  thermal signature; these get *no spray*, they get flagged.

#### Signal B — Geometry from the mesh (deterministic, no ML)

The 3D mesh gives us facts ML can't hallucinate:

- **Plane segmentation** (RANSAC on the point cloud, via Open3D / PDAL) → separates
  roof planes, walls, ground. Each plane's **normal vector** gives true pitch angle
  (fixes the Fusion agent's current SfM-inference approximation).
- **Perimeter/edge detection** → gutters, roof edges, parapets → standoff constraints.
- **Height above ground** (from DSM) → distinguishes ground-level windows from
  second-story, feeds the operator's approach planning.

Geometry rules are **deterministic and auditable** — exactly what we want feeding the
safety layer. A solar panel misclassified by RGB but sitting on a 5° roof plane at
roof height is cross-checked by geometry before we ever prescribe DI-water-only.

#### Signal C — Thermal (condition, not identity)

Thermal doesn't identify the *surface* so much as its *condition* — the grime/moisture
proxy (CLAUDE.md §5). But it also disambiguates: a warm rectangular blob that RGB
thinks is a solar panel but that's 45°C uniform and rigid is probably an **HVAC unit**
→ exclusion, not a panel.

#### The fusion decision

```
final_zone_class = fuse(
    rgb_semantic_label,      # what the CV model thinks it is
    geometry_constraints,    # what the mesh plane/normal/height allow
    thermal_signature,       # condition + HVAC/vent disambiguation
)
# Conflicts resolve CONSERVATIVELY: if any signal says "could be solar or glass",
# treat as the most pressure-sensitive class (lowest ceiling). Safety over coverage.
```

That conservative-fusion rule is a **trade secret** and a safety principle — it's the
same philosophy as the deterministic safety layer.

#### Build vs. buy verdict for Stage 3
- **BUY (open source):** SAM/SAM2, the segmentation backbone, Open3D RANSAC, OpenCV.
- **BUILD (ours, secret):** the labelled training dataset of San Diego roofs, the
  classifier head, the geometry rule set, the three-signal conservative fusion, the
  exclusion-zone logic. **This is defensible IP** — a competitor can download SAM too,
  but they can't download our labelled dataset or our fusion rules.

---

### 5. Stage 5 — Flight / coverage path generation (BUILD)

Once each zone is classified and prescribed, we generate **how the cleaning drone
should cover it.** This is a **coverage path planning (CPP)** problem — a known robotics
field we can borrow algorithms from, but the *cleaning-specific* constraints are ours.

#### What "flight path" means here (critical framing, §9)

Per CLAUDE.md §7/§10, the Sherpa is **operator-piloted**. So the output of this stage
is **NOT an autonomous flight command stream.** It is an **operator guidance overlay**:
the app shows the operator the recommended standoff surface, sweep lines, coverage
order, and keep-out volumes — the operator flies it and stays in command. If/when Lucid
exposes an API and FAA waivers permit (Path B/C), the *same computed path* can feed more
automation behind a feature flag. We compute the path either way; we don't assume we
get to fly it autonomously.

#### The computation, per zone

1. **Offset surface (standoff).** Take the zone's mesh faces, offset outward along the
   surface normal by the prescribed `standoff_m` (e.g., solar = 0.8 m). This defines the
   surface the nozzle should travel on — a "shell" parallel to the building.
2. **Coverage pattern → toolpath.** Map the prescribed `coverage_pattern` (e.g.,
   `sweep_ns`, `sweep_ew`) onto that shell as **boustrophedon (back-and-forth) sweep
   lines**, spaced by the nozzle's effective spray width at that standoff and pressure.
   Boustrophedon decomposition is textbook CPP (we implement it; we don't buy it).
3. **Dwell & speed.** Convert prescribed `dwell_seconds` + spray width into a **traverse
   speed** along each sweep line. This is the number the operator (or Path-B controller)
   actually needs.
4. **Keep-out volumes.** Every EXCLUSION zone (chimney, HVAC, window we're not cleaning,
   the operator's own position, detected people) becomes a **no-fly / no-spray volume**
   the path routes around. This feeds the deterministic safety layer.
5. **Zone ordering.** Sequence zones to minimize repositioning and respect physics:
   **solar first** (before any detergent is anywhere near it), gravity-fed dirt runoff
   top-down (roof before façade), gutters last. This ordering logic is a trade secret
   (it's calibration-informed).
6. **Emit dual output:**
   - **Operator overlay** (always): sweep lines + order + keep-outs rendered in the app
     over live video / the twin.
   - **Structured path** (Path B/C, flagged off): waypoint + speed + pressure setpoint
     list the Cleaning agent *could* hand to a controller once legally cleared.

#### Tools we lean on
- **Open3D / trimesh** — normal offsetting, mesh boolean for keep-outs.
- **Shapely** (BSD) — 2D polygon ops for per-plane boustrophedon decomposition.
- **NetworkX** (BSD) — zone-ordering as a routing/TSP-ish graph problem.
- **NumPy** — the geometry.
- (Optional later) **OMPL / MoveIt** concepts for 3D motion planning if we go full Path C.

#### Repo home
```
propwash/backend/planning/
  offset_surface.py        # standoff shell from zone faces
  coverage_path.py         # boustrophedon sweep generation
  keep_out.py              # exclusion volumes (feeds safety)
  zone_ordering.py         # solar-first / top-down sequencing (trade secret)
  operator_overlay.py      # render guidance for the app
  path_export.py           # structured path (Path B/C, feature-flagged)
```

---

### 6. Build-vs-buy summary (the whole pipeline)

| Stage | Build or Buy | What | Why |
|---|---|---|---|
| 1. SfM photogrammetry | **BUY** (OpenDroneMap) | RGB → mesh/cloud/ortho | Commodity, 20-yr-deep field, don't reinvent |
| 2. Thermal registration | **BUILD** | Paint °C onto mesh | No good off-the-shelf tool; it's our IP |
| 3a. CV segmentation backbone | **BUY** (SAM, DeepLab) | Region proposals | Open, world-class, free |
| 3b. Surface classifier + dataset | **BUILD** (secret) | Label regions as our surface classes | The defensible IP |
| 3c. Geometry rules | **BUILD** | Plane/normal/edge logic | Deterministic, safety-feeding |
| 4. Prescription | **BUILD** (secret) | Cleaning parameters | The crown-jewel trade secret |
| 5. Coverage path | **BUILD** | Sweep/standoff/order | Cleaning-specific; borrow CPP algorithms |
| — | **BUY** (libraries) | Open3D/OpenCV/Shapely/PDAL | Permissive, commercial-safe |

**The rule:** buy the commodity math (geometry reconstruction, CV backbones, mesh
libraries). Build — and keep secret — everything that encodes *how to clean*: thermal
registration for grime, the surface dataset + classifier, the prescription tables, the
zone ordering, the calibration learning loop. **That boundary is the IP boundary from
`IP_PROTECTION.md`: buy the choreography's stage, own the choreography.**

---

### 7. Data sovereignty (why self-hosted matters)

Every stage that touches customer sensor data should run on **our infrastructure**, not
a third-party cloud, because:

- The **accumulated labelled dataset** of roofs + thermal + outcomes is the trade-secret
  data moat (`IP_PROTECTION.md §3`). If it flows through DroneDeploy's cloud, we've
  handed our moat to a vendor whose terms may claim rights to it.
- Self-hosting (OpenDroneMap + our pipeline on our own GPU box or a locked-down cloud
  account) keeps the crown jewels behind our access controls.
- **Action:** review every SaaS tool's data-rights terms before it touches a real job.
  Prefer the self-hosted open-source path even at some convenience cost.

---

### 8. Do we ever add LiDAR? (documented future option, not now)

**Not for Year 1.** SfM from the Autel is sufficient for cleaning prescription.
Remember (§0b): **no Autel option gives us LiDAR** — the EVO II Dual 640T has thermal+RGB,
and the EVO MAX 4T adds a *laser rangefinder* (single-point distance), not a scanning
LiDAR. True LiDAR means leaving the Autel platform entirely. Add it only if a concrete
need appears:

- **When it'd help:** heavy tree occlusion around a property; survey-grade geometry for
  very tall/complex commercial structures; night/low-light capture; faster turnaround
  (LiDAR needs less overlap than SfM).
- **What it'd cost:** a different aircraft + payload (e.g., DJI Matrice 350 + Zenmuse
  L2, ~$15–20K all-in) and a second processing path (LiDAR → point cloud is direct, no
  SfM needed; our Stage 2–5 code stays the same because it already consumes a point
  cloud + mesh).
- **The cheaper middle step first:** if the motivation is just *better scale/accuracy*,
  the **EVO MAX 4T's laser rangefinder** (§0b) improves SfM scale for a fraction of the
  cost of a LiDAR aircraft — same photogrammetry pipeline, tighter dimensions. Try that
  before jumping to a Matrice + L2.
- **Architecture note:** because Stage 2+ consumes a **point cloud + mesh abstraction**,
  swapping the *source* from SfM to LiDAR is a Stage-1 change only. Keep Stage 1 behind
  a `GeometrySource` interface (`SfmSource`, `SfmWithLrfSource`, `LidarSource`) — mirror
  the swappable `ExecutionTransport` pattern. **Don't hard-code SfM assumptions into
  Stage 2+.**

Do **not** claim LiDAR in any spec/patent/marketing until it's actually in the loop
(CLAUDE.md §5 honesty rule). A laser rangefinder is **not** LiDAR (§0b) — do not conflate
the two in any external claim.

---

### 9. The flight-automation boundary (safety + legal — do not blur)

The path planner (§5) is powerful, and it's tempting to feed it straight to the drone.
**Do not** — not as a technical taboo but a legal/safety one (CLAUDE.md §2, §7, §10):

- The computed path is **operator guidance by default.** Operator stays in command
  (Part 107). More automation requires Lucid API access **and** the appropriate FAA
  pathway/waiver, gated behind `PROPWASH_ENABLE_PATH_B/C`.
- Keep-out volumes and the human-detection safety check are **Tier 1 deterministic** —
  they can veto any path. The Claude agents (Tier 3) that help plan **never** override
  them.
- Never build a path whose premise is concealing automation from Lucid or circumventing
  Part 107. Transparent integration + proper waivers only.

---

### 10. Concrete tech stack (add to CLAUDE.md §12 stack)

**New pipeline dependencies (all permissive / commercial-safe except where noted):**

```
# Geometry / point cloud
open3d            # BSD  — mesh raycasting, RANSAC planes, cloud ops
trimesh           # MIT  — mesh geometry, ray-triangle, normals, areas
pdal              # BSD  — point cloud translate/filter (optional)
laspy             # BSD  — read .las/.laz point clouds

# Imagery / geo
opencv-python     # Apache-2.0 — calibration, undistort, frame ops
rasterio          # BSD  — read orthomosaic/DSM GeoTIFFs
gdal              # MIT/X — geo backend
shapely           # BSD  — 2D polygon ops for coverage decomposition
pyproj            # MIT  — coordinate transforms

# CV segmentation (model weights pulled at deploy)
segment-anything  # Apache-2.0 — SAM region proposals
transformers      # Apache-2.0 — SegFormer/DeepLab fine-tune (HuggingFace)
torch             # BSD  — inference
# NOTE: ultralytics YOLO is AGPL — review before commercial use

# Planning
networkx          # BSD  — zone ordering / routing

# External TOOL (not a pip dep): OpenDroneMap via Docker (AGPL — see §2 caveat)
```

**License watch-list for counsel:** OpenDroneMap (AGPL, if we ever host processing for
third parties), Ultralytics YOLO (AGPL). Everything else is permissive.

---

### 11. Suggested repo layout (extends CLAUDE.md §13)

```
propwash/backend/
  geometry/
    source.py              # GeometrySource interface (SfM now, LiDAR later)
    sfm_source.py          # wrap OpenDroneMap output          [Stage 1]
    lidar_source.py        # future — flagged off               [Stage 1]
  fusion/
    sfm_ingest.py          # read cloud/mesh/ortho              [Stage 2]
    thermal_registration.py# project °C onto mesh (SECRET)      [Stage 2]
    reflection_filter.py   # glass/solar IR rejection (SECRET)  [Stage 2]
    twin_builder.py        # assemble DigitalTwin
  segmentation/
    region_proposer.py     # SAM wrapper                        [Stage 3a]
    surface_classifier.py  # our head + dataset (SECRET)        [Stage 3b]
    geometry_rules.py      # plane/normal/edge (deterministic)  [Stage 3c]
    fusion_decision.py     # conservative 3-signal fuse (SECRET)[Stage 3]
  planning/
    offset_surface.py      # standoff shell                     [Stage 5]
    coverage_path.py       # boustrophedon sweeps               [Stage 5]
    keep_out.py            # exclusion volumes → safety         [Stage 5]
    zone_ordering.py       # solar-first/top-down (SECRET)      [Stage 5]
    operator_overlay.py    # app guidance render                [Stage 5]
    path_export.py         # Path B/C structured path (flagged) [Stage 5]
  datasets/                # LABELLED ROOF DATA — crown jewel, access-controlled
```

---

### 12. Build roadmap for the pipeline

#### Phase 1 — Geometry online (weeks 1–3)
1. Stand up **OpenDroneMap** (Docker) on a GPU box / cloud instance.
2. Process one real Autel survey → confirm we get cloud + mesh + ortho + DSM.
3. Build `sfm_source.py` behind a `GeometrySource` interface.
**Milestone:** raw Autel flight → 3D model on our servers, no third-party cloud.

#### Phase 2 — Thermal twin (weeks 3–6)
4. One-time **camera calibration** (thermal intrinsics + RGB↔thermal extrinsics).
5. Build `thermal_registration.py` — project °C onto mesh faces (Open3D raycast).
6. Build `reflection_filter.py`; assemble the `DigitalTwin`.
**Milestone:** thermographic digital twin renders in the visor (already built).

#### Phase 3 — Segmentation (weeks 6–12)
7. Wire **SAM** for region proposals; label a starter dataset of ~30–50 San Diego roofs.
8. Train the surface classifier head; add `geometry_rules.py` + `fusion_decision.py`.
9. Feed labelled zones into the existing Fusion → Supervisor → safety chain.
**Milestone:** upload a survey → auto-labelled zones (solar/window/tile/…) with
conservative fusion + exclusion zones.

#### Phase 4 — Coverage path (weeks 12–16)
10. Build offset-surface + boustrophedon `coverage_path.py`; `keep_out.py`;
    `zone_ordering.py`.
11. Render the **operator guidance overlay** in the visor over the twin.
12. Emit the structured path behind `PROPWASH_ENABLE_PATH_B` (flagged off).
**Milestone:** full survey → labelled zones → prescriptions → operator-flyable
coverage plan, end to end, no hardware autonomy assumed.

---

### 13. The one-paragraph answer to the user's question

We **buy the geometry and the CV muscle, and build the intelligence.** OpenDroneMap
(self-hosted) turns the Autel's RGB photos into a 3D point cloud + mesh via
photogrammetry — there's **no LiDAR** on any Autel we'd fly (the EVO II Dual 640T is
thermal+RGB; the EVO MAX 4T adds a *laser rangefinder*, i.e. single-point distance, not
a scanning point cloud — §0b), and we don't need LiDAR for Year 1.
Our own code then paints the thermal data onto that mesh (Stage 2), and a segmentation
model built on open-source backbones like **SAM**, but trained on **our private San Diego
roof dataset** and cross-checked against **deterministic mesh geometry**, identifies
every asset — solar arrays, windows, skylights, tile, stucco, gutters, and no-spray
exclusion zones (Stage 3). From there our prescription tables (trade secret) set the
cleaning parameters, and a coverage-path planner turns each zone into standoff sweep
lines with keep-out volumes — delivered as an **operator guidance overlay**, not an
autonomous flight command, because the pilot stays in command under Part 107. The
off-the-shelf tools are commodity and swappable; the defensible IP is the thermal
registration, the labelled dataset + classifier, the prescription tables, and the
zone-ordering — none of which a competitor can download.

<a id="docsthermallayeringpipeline"></a>

---

# Deep Dive — Layering Thermal onto the 3D Model (precisely)

> **Source file:** `docs/THERMAL_LAYERING_PIPELINE.md`

## Deep Dive — Layering Thermal onto the 3D Model (precisely)

> How captured imagery becomes a 3D model with thermal painted onto it, per-surface,
> accurately enough to drive per-surface pressure decisions.
>
> Companion to `3D_DATA_PIPELINE.md` (which picks the engine) — this doc is the **precision
> procedure** for the thermal overlay specifically.

---

### 0. The headline

**Agisoft Metashape supports exactly this workflow natively, via its multi-camera system
feature — and the Autel EVO MAX 4T V2's co-registered sensors are what make it clean.**

The documented procedure:

1. Import RGB + thermal **as a multi-camera system** — Metashape automatically recognises each
   RGB/IR image group as **co-registered in space**, which greatly simplifies alignment.
2. Set the **RGB images as master**, align, and build a **high-resolution mesh from depth maps**.
   (RGB carries the texture detail SfM needs; thermal cannot feature-match — see §2.)
3. Then set the **IR images as master** and **project the thermal information as a texture onto
   that detailed mesh**.

That is precisely "3D model with the thermal layered on top," and it's a supported path — not
something we have to invent.

---

### 1. Why the Autel 4T V2 makes this work

Multi-camera mode depends on the sensors being rigidly co-mounted and triggering together.
On the 4T V2 the wide, zoom, thermal and laser rangefinder share **one gimbal**, so every
capture is a genuine RGB/IR group: same position, same attitude, same instant, differing only
by a fixed boresight (`geometry/autel_ingest.py`).

**Contrast with a two-aircraft rig:** you'd be solving cross-flight alignment for every frame —
different times, different poses, different lighting/thermal state. The co-registered payload
turns that alignment problem into a **constant**. This is the single strongest technical
argument for the 4T V2 as the scout.

---

### 2. Why RGB must drive the geometry

Photogrammetry works by matching visual features between overlapping images. **Thermal imagery
is low-resolution (640×512), low-contrast, and its "features" move with temperature** — a warm
patch is not a stable landmark. Trying to build geometry from thermal produces poor meshes.

So: **RGB builds the shape; thermal supplies the values.** Every serious thermal-3D workflow
follows this order, and it's why our `SurveyCapture.rgb_paths` feeds photogrammetry while
`thermal_paths` is held for the overlay step.

---

### 3. Two different thermal outputs — we need BOTH

A distinction that matters and is easy to conflate:

| Output | What it is | Produced by | Used for |
|---|---|---|---|
| **Thermal texture** | thermal painted onto the mesh as an image | Metashape (multi-camera) | the **visual** twin — visor, customer report |
| **Per-face radiometric values** | °C per mesh face, with confidence | **our** `fusion/thermal_registration.py` | the **analysis** — grime proxy, per-surface pressure |

Metashape gives you a beautiful thermal-textured model. It does **not** give you
view-angle-weighted, reflection-rejected per-face temperature with a confidence score — that's
our Stage-2 code, and it's where the defensible IP sits (`IP_PROTECTION.md` §2).

**Use Metashape for the picture; use our registration for the decision.**

---

### 4. The precision chain — where accuracy is won or lost

Precision is cumulative. Each link below either preserves or destroys it.

| Link | Risk | Mitigation |
|---|---|---|
| **Capture geometry** | thin overlap → weak/holed mesh | 70–80% overlap; multiple altitudes; orbit + nadir passes |
| **Scale/georeference** | metric drift → wrong standoff & area | **RTK module** ⭐; laser rangefinder ground truth; GCPs on critical jobs |
| **Sensor sync** | mismatched RGB/IR pair → thermal on the wrong surface | co-registered gimbal + timestamp pairing with a **window**, never force-matched |
| **Boresight calibration** | constant angular offset → thermal shifted a few cm | one-time checkerboard calibration per airframe; store as `Boresight` |
| **Thermal reflection** | glass/solar mirror sky IR → false cold/hot | **variance-based rejection** (`reflection_filter`), flag `THERMAL_UNCERTAIN` |
| **Grazing-angle faces** | oblique views read unreliably | **view-angle weighting** (cos θ) in per-face aggregation |
| **Occlusion** | a face textured from a camera that couldn't see it | visibility test during projection; multi-frame agreement |
| **Thermal drift** | sensor warms over a flight → values drift | fly consistently; treat *relative* differentials as primary, not absolute °C |

> **The honest precision statement:** we are precise about **where** a surface is (cm-level with
> RTK) and about **relative** thermal differentials across it. Absolute temperature accuracy is
> ±2–5 °C on an uncooled microbolometer — which is fine, because the grime proxy is built on
> *differentials*, not absolute values (CLAUDE.md §5).

---

### 5. Timing — the biggest free accuracy win

Thermal contrast is a *physics* problem before it's a software problem:

- **Best:** early morning or ~1–2 h after sunset. Surfaces are shedding heat; moisture and
  soiling show as clear differentials.
- **Worst:** midday full sun. Solar loading swamps the differentials you're trying to read and
  glass/panels throw specular IR.
- **Avoid:** immediately after rain (everything reads wet), high wind (convective washing-out).
- **Repeat visits:** capture at a **similar time of day** so the delta-comparison in the living
  digital twin is meaningful.

**Scheduling surveys for thermal quality costs nothing and improves every downstream number.**

---

### 6. The concrete pipeline (what we run)

```
Autel 4T V2 survey  (RGB + thermal, one gimbal, geotagged)
        │
        ├─ autel_ingest.py ── pair frames, derive poses (boresight)        ✅ built
        │
        ├─ Metashape multi-camera ── RGB master → align → high-res mesh
        │                            IR master  → thermal TEXTURE          [buy]
        │        (or NodeODM for mesh only, free — see 3D_DATA_PIPELINE §2d)
        │
        ├─ thermal_registration.py ── per-face °C, view-angle weighted,
        │                             reflection-rejected, confidence      ✅ built
        │
        ├─ segmentation/ ── surface class per face (solar/glass/tile/…)    ✅ built
        │                   + EXCLUSION zones
        │
        └─ scan_pipeline.py ── ScannedZone: surface + grime proxy + temp   ✅ built
                    ↓
            per-surface pressure prescription (safety-gated)               ✅ built
```

**Verdict on build-vs-buy for this step:** buy Metashape (~$3.5K perpetual) for the mesh +
thermal texture; keep the per-face radiometric analysis in-house. That split gives customer-
grade visuals *and* keeps the decision layer proprietary.

---

### 7. Open items
- [ ] Confirm Metashape multi-camera ingests Autel 4T V2 RGB/IR groups without manual pairing.
- [ ] Perform the one-time boresight calibration; store the `Boresight` constants per airframe.
- [ ] Price the Autel **RTK module** (biggest single precision upgrade).
- [ ] Define the standard survey pattern (overlap %, altitudes, orbit+nadir) as an SOP.
- [ ] Add thermal-optimal time-of-day windows to the scheduling engine.

### Sources
- [Agisoft — thermal, multispectral & LiDAR data in Metashape](https://www.agisoftmetashape.com/using-agisoft-metashape-with-thermal-multispectral-and-lidar-data/) · [Metashape Pro user manual 2.0 (PDF)](https://www.agisoft.com/pdf/metashape-pro_2_0_en.pdf)
- [MetaMosaic — RGB + thermal orthomosaics via Metashape/CloudCompare](https://github.com/s-du/MetaMosaic)
- [Metashape vs Pix4D comparison](https://vagon.io/blog/agisoft-metashape-vs-pix4d-which-photogrammetry-software-should-you-choose)

<a id="docsthermographicdigitaltwin"></a>

---

# PROPWASH — Thermographic Digital Twin + Human Presence Detection

> **Source file:** `docs/THERMOGRAPHIC_DIGITAL_TWIN.md`

## PROPWASH — Thermographic Digital Twin + Human Presence Detection

> ⚠️ **Not legal advice.** Engage counsel for patent filings, FAA regulatory review,
> and any claims about safety-critical detection systems before shipping.

---

### 0. What this is

A **thermographic digital twin** is a georeferenced 3D mesh of the property with
thermal data registered and projected onto every surface polygon — not just a flat
thermal image, but a *model* where every face of the roof, every façade panel, every
soffit has:

- A surface temperature value (from the Autel thermal sensor)
- A grime/moisture proxy score (from the Fusion agent)
- A surface classification (composite shingle, stucco, solar panel, etc.)
- A cleaning status (queued / done / failed)

This becomes the **single source of truth** for the job — what to clean, in what order,
with what parameters, and whether each zone actually passed.

The second capability this document covers is **human presence detection** — using the
thermal model to identify people on or near the work zone before any cleaning pass
executes. This is a safety feature, not an AI feature: it lives in the deterministic
safety layer (Tier 1), not in the Claude agents (Tier 3).

---

### 1. Why the 3D model matters more than a flat thermal image

Current state: the Fusion agent works from flat thermal + RGB frames and infers surface
geometry from photogrammetric structure (pitch angle, normals). That's enough to
prescribe cleaning parameters, but it has blind spots:

| Limitation | Consequence |
|---|---|
| Flat images don't know the surface faces away from the drone | Standoff distance calculation is wrong for pitched surfaces |
| Shadow zones appear cold on thermal — ambiguous with clean surfaces | False negatives in grime detection |
| Occlusions (chimneys, HVAC units, parapets) create gaps | Zones appear clean when they haven't been reached |
| No persistent model between the survey flight and the clean | Operator can't verify the drone reached the right zone |

The 3D model solves all of these. Once you have a mesh, you can:

- Project the thermal frame onto the mesh surface rather than the image plane
- Compute true standoff distance and approach angle per zone, not approximate
- Detect occlusions as mesh holes, flag them for manual attention
- Overlay cleaning status live on the model so the operator sees exactly what's been done

---

### 2. How to build it (the pipeline)

#### Step 1 — Survey flight (existing: Autel EVO II 640T)

The Autel flies a grid or orbit pattern. It already captures:
- **RGB frames** at high resolution
- **Radiometric thermal frames** (640×512, with per-pixel temperature values)

No new hardware needed for the 3D model. The Autel's dual camera provides exactly what
photogrammetry requires.

#### Step 2 — Structure from Motion (SfM) → 3D mesh

Feed the RGB frames into a photogrammetry pipeline:

| Tool | Type | Notes |
|---|---|---|
| **OpenDroneMap** | Open source | Best for self-hosted; WebODM is the UI; handles roofs well |
| **Pix4Dmapper** | Commercial | More accurate on complex geometry; $350/mo |
| **Metashape (Agisoft)** | Commercial | Strong on texture quality; one-time license |
| **DroneDeploy** | Cloud SaaS | Fastest turnaround; less control; data leaves your servers |

Output: a **georeferenced point cloud** (`.las` / `.ply`) + a **textured mesh** (`.obj`)
+ an **orthomosaic** (`.tiff`). The mesh is the canvas.

> **Data sovereignty note:** OpenDroneMap is the preferred choice — it runs on your
> own servers, sensor data never leaves your infrastructure, and it's the tool already
> referenced in CLAUDE.md §12. Use DroneDeploy only if turnaround time is critical and
> the customer contract permits third-party cloud processing.

#### Step 3 — Thermal registration onto the mesh

Project each radiometric thermal frame onto the 3D mesh using the camera pose (GPS +
IMU from the flight log):

1. For each thermal frame: compute which mesh polygons fall within the camera frustum.
2. For each visible polygon: compute the weighted average temperature from all frames
   that observed it (multi-frame averaging reduces noise).
3. Store the result as a per-face attribute on the mesh: `temp_celsius`, `grime_proxy`,
   `moisture_index`.

This is the thermographic digital twin — a mesh where every face has a temperature.

**Tech:** Open3D or trimesh (Python) for mesh manipulation; OpenCV for frame projection;
store the annotated mesh as a `.glb` (binary GLTF) for browser rendering.

#### Step 4 — Zone segmentation on the mesh

The Mapping Agent already segments zones. On the 3D model, zones become **mesh
sub-regions** (groups of faces) rather than flat polygons. Each zone inherits:
- Surface type (from RGB classification)
- Mean grime proxy score (from thermal overlay)
- Pitch angle (from face normals — directly from the mesh, no inference)
- True area in m² (from face areas — more accurate than 2D projections)

This fixes the pitch-angle estimation that currently relies on SfM inference in the
Fusion pipeline.

---

### 3. Human presence detection

#### What it detects

A human body at rest or in motion has a core skin temperature of **32–36°C** and a
distinctive **compact thermal blob signature** — roughly 0.4 × 1.8 m when viewed from
above, warmer than most roof surfaces in the morning, cooler than sun-heated dark
surfaces in the afternoon.

The detection task: before any cleaning pass executes, scan the target zone's thermal
mesh for any blob whose:
- Mean temperature is in the range [30°C, 40°C]
- Bounding box aspect ratio matches a human figure (tall and narrow, or compact if prone)
- Area is in the range [0.1 m², 1.5 m²] (filters out HVAC vents and small birds)

#### Where this lives in the architecture

This is **not a Claude agent task**. Human detection is a **deterministic safety check**
in the Tier 1 safety layer — the same layer that enforces the solar pressure ceiling.

```
Before any cleaning pass:
  SafetyChecker.check_human_presence(zone_thermal_frame)
    → if HUMAN_DETECTED: HALT, alert operator, block dispatch
    → if CLEAR: proceed to PSM setpoint dispatch
```

The Claude agents (Tier 3) never make the human detection decision. A threshold is set
in the safety layer; it never changes without a deliberate code change and review.
This is important for regulatory conversations with the FAA and for liability purposes.

#### Why thermal rather than RGB

| Detection method | Problem |
|---|---|
| RGB only | People in dark clothing on dark roofs are invisible; shadows mask figures |
| Thermal only | Can't distinguish a human from an HVAC unit at 35°C |
| **Thermal + shape filter (what we build)** | Temperature range + blob geometry together are highly reliable |

The Autel's dual camera gives you both channels simultaneously. The shape filter runs
on the thermal channel; the RGB channel provides a second confirmation (is there a
person-shaped object at the location flagged by thermal?). This dual-channel approach
is patentable — see §5.

#### Edge cases to handle

| Scenario | Handling |
|---|---|
| HVAC exhaust vents (35–45°C, compact) | Shape filter — vents are round, not elongated |
| Birds (small, 38–41°C) | Area filter — birds are < 0.05 m² from drone altitude |
| People in direct sun on a hot roof (surface temp 55°C+) | The person is *cooler* than the surface — detect as a cool blob, not a warm one |
| Shadow zones (anomalously cold in thermal) | Flagged as UNCERTAIN, not CLEAR — requires manual operator review |

---

### 4. Roof vs. structural features (the other classification)

Beyond human detection, the 3D thermal model enables a richer classification than the
current surface-type enum:

| Feature | How detected | Cleaning implication |
|---|---|---|
| **Solar panels** | Thermal uniformity + RGB panel grid pattern | DI water only, 2.0 bar ceiling |
| **HVAC units / vents** | Warm thermal blob, rigid rectangular shape | Avoid direct spray — flag for manual |
| **Skylights** | RGB glass signature + thermal edge ring | Treat as window glass — 2.0–2.4 bar |
| **Parapets / edges** | Mesh edge detection, vertical faces | Standoff constraint — flag near-edge zones |
| **Gutters** | Elongated horizontal features at roof perimeter | Separate zone type, different nozzle |
| **Chimneys / vents** | Vertical protrusions in mesh | Exclusion zone — don't spray directly |
| **People** | Thermal blob in human temp + shape range | HALT |

This richer classification feeds directly into the Supervisor Agent's prescription —
more precise zone typing means more precise cleaning parameters and fewer mis-cleans.

---

### 5. IP angles

#### 5a. The core patentable system

> *"A method of autonomous surface-cleaning prescription for unmanned aerial vehicles
> comprising: (a) generating a georeferenced three-dimensional mesh of a structure
> from RGB imagery captured by a survey drone; (b) projecting radiometric thermal
> sensor data onto said mesh to produce a per-face thermographic digital twin; (c)
> segmenting the mesh into cleaning zones by surface classification and thermal
> signature; (d) prior to each cleaning pass, executing a deterministic human-presence
> detection scan of the target zone using thermal blob geometry and temperature-range
> filtering, halting dispatch if a human signature is detected; and (e) prescribing
> cleaning parameters per zone based on surface type, thermal grime proxy score, and
> mesh-derived pitch angle."*

Every element of this is novel in combination for the cleaning-drone context.

#### 5b. Dependent claims worth adding

- The dual-channel confirmation (thermal blob + RGB shape co-registration)
- The per-face thermal averaging across multiple flight passes (reduces noise, improves
  prescription accuracy over repeat customers)
- The "cool blob on hot surface" human detection mode (afternoon sun scenario)
- Storing the thermographic digital twin as a persistent customer asset and using
  delta-comparison between visits to detect new soiling (predictive scheduling)

#### 5c. Trade secrets (do not put in patent claims)

- The specific temperature range thresholds used for human detection ([30, 40°C] above
  is an example — your field-tuned values are the secret)
- The blob shape filter parameters tuned for drone altitude and camera FOV
- The grime proxy calibration coefficients per surface type
- The multi-visit delta model that predicts when a zone will fail next (scheduling IP)

---

### 6. The persistent customer asset: the living digital twin

Each time PROPWASH cleans a property, it updates the thermographic digital twin:

```
Visit 1: baseline 3D model + thermal state
Visit 2: re-scan → delta comparison → new soiling map
Visit 3: delta again → soiling rate model per zone
        → predict when each zone will next exceed threshold
        → auto-generate scheduling recommendation
```

This turns a one-time service call into a **subscription relationship** — the digital
twin gets more valuable with every visit because it knows how fast each surface of this
specific building soils. You can then pitch the customer on a predictive maintenance
contract: "Your solar array typically exceeds our cleaning threshold every 6–8 weeks in
summer, 12–14 weeks in winter. We'll schedule automatically."

The digital twin archive is also an asset you own. A competitor who wins the next
cleaning contract for a building you've already serviced **starts from scratch** on the
model. You already know the building's soiling rates, surface quirks, and geometry.

---

### 7. Architecture changes

#### New modules

```
propwash/
  fusion/
    sfm_pipeline.py          # NEW: wrap OpenDroneMap/Pix4D, ingest .las/.ply output
    thermal_registration.py  # NEW: project thermal frames onto mesh faces
    twin_builder.py          # NEW: assemble the annotated .glb digital twin
    zone_segmentation_3d.py  # EXTEND: segment mesh faces into zones (replaces 2D poly)
  safety/
    human_detection.py       # NEW: deterministic thermal blob detector (Tier 1)
    checks.py                # EXTEND: add HUMAN_DETECTED check before every dispatch
  models/
    digital_twin.py          # NEW: Pydantic model for the twin metadata + zone refs
```

#### Data flow change

```
Before (current):
  Autel frames → Mapping Agent → flat zone polygons → Fusion Agent → signatures

After (new):
  Autel frames ──┬──▶ SfM pipeline → 3D mesh
                 └──▶ thermal frames
                         │
                  thermal_registration.py
                         │
                         ▼
                  thermographic 3D twin (per-face temp, grime proxy)
                         │
                  zone_segmentation_3d.py → 3D zone regions
                         │
                  Fusion Agent → zone signatures (now mesh-aware)
                         │
                  Before each pass: human_detection.py → CLEAR / HALT
```

#### New Pydantic model (sketch)

```python
class DigitalTwin(BaseModel):
    property_id: str
    captured_at: datetime
    mesh_ref: str            # object storage path to .glb
    orthomosaic_ref: str     # object storage path to .tiff
    zones: list[ZoneSignature]
    soiling_rate: dict[str, float] | None = None  # zone_id → weeks_to_threshold
    human_check_cleared_at: datetime | None = None
```

---

### 8. Build roadmap

#### Phase 1 — Flat-to-3D upgrade (no new hardware)
1. Wire OpenDroneMap into the existing survey pipeline; store `.las` + `.obj` outputs
   in object storage (S3-compatible).
2. Build `thermal_registration.py`: project thermal frames onto mesh using flight log
   GPS + IMU poses; output per-face temperature.
3. Extend `ZoneSignature` with `pitch_deg` from mesh face normals (remove the SfM
   inference approximation currently in the Fusion pipeline).
4. Render the thermographic twin in the operator React app — a 3D view using Three.js
   with a thermal color ramp (blue = cool/clean, red = hot/dirty).

**Milestone:** Operator can view a 3D thermal model of the property and see which zones
are prescribed for cleaning before the job starts.

#### Phase 2 — Human presence detection
1. Build `human_detection.py` with temperature-range blob detector; write unit tests
   covering the HVAC / bird / afternoon-sun edge cases.
2. Wire into `SafetyChecker` as a pre-dispatch check.
3. Add a `HUMAN_DETECTED` alert to the operator app — zone card shows a red banner
   with the thermal frame annotated with the detected blob location.
4. Log every human detection event to the audit table (liability protection).

**Milestone:** No cleaning pass can execute without a thermal human-clear check.

#### Phase 3 — Living twin + predictive scheduling
1. On each return visit, run a delta comparison between the new thermal scan and the
   stored baseline model.
2. Build the soiling rate model: fit a curve to the delta-per-zone over multiple visits.
3. Surface scheduling recommendations in the operator dashboard: "Zone SOL-ROOF
   predicted to exceed threshold in ~42 days — schedule next clean."
4. Add the persistent twin archive as a customer-facing report deliverable — the
   property owner can see their building's soiling history.

**Milestone:** PROPWASH can offer predictive maintenance contracts backed by real data.

---

### 9. What to do this quarter

1. **Stand up OpenDroneMap** on a local machine or cloud instance using the next survey
   flight — even just to see the output. Free, open source, Docker-deployable.
2. **Prototype thermal registration** in a Jupyter notebook: take one Autel flight's
   thermal frames + GPS log + ODM mesh, project temperatures onto faces, visualize.
3. **Write the human detection module** (`human_detection.py`) with unit tests against
   synthetic thermal frames. This can be done before you have real data.
4. **Add `DigitalTwin` Pydantic model** to `propwash/backend/models/`.
5. **Talk to a patent attorney** about adding the thermographic twin + human detection
   claim to the provisional — it strengthens the method patent considerably.

---

### 10. Mental model

```
The 3D thermal model is not a deliverable — it is the engine.
Every prescription comes from it. Every safety check runs against it.
Every repeat visit makes it more accurate. It compounds.

A competitor cleaning the same building doesn't have the model.
You've been building it since your first visit.
```

The digital twin is the PROPWASH data moat made *visible* — to you, to the operator,
and eventually to the customer. It is the thing that turns a cleaning company into a
building-intelligence company.

<a id="docsdynamicpressurehardware"></a>

---

# PROPWASH — Dynamic Pressure Control Hardware

> **Source file:** `docs/DYNAMIC_PRESSURE_HARDWARE.md`

## PROPWASH — Dynamic Pressure Control Hardware

> ⚠️ **Not legal advice.** Patent strategy, hardware regulation (FAA, EPA, OSHA), and
> product-liability law require licensed counsel. This document tells you what to think about
> before engaging them.

---

### 0. The short answer

**Yes, such devices exist — but they are generic, not cleaning-drone-aware.**
No product on the market closes the loop between a *computer-vision/thermal inspection result*
and a servo-controlled pressure regulator on a drone-mounted spray system.
That gap is PROPWASH's hardware IP opportunity.

---

### 1. What exists today (the competitive baseline)

#### 1a. General-purpose electronic pressure regulators (EPRs)

Electronic pressure regulators replace a manual pressure knob with a signal-driven valve.
Common examples:

| Manufacturer | Product | Pressure range | Control interface |
|---|---|---|---|
| Proportion-Air | QB1/QB2 series | 0–210 bar | 0–10 V, 4–20 mA, or serial |
| Marsh Bellofram | 900 series | 0–10 bar | 0–10 V / 4–20 mA |
| Bürkert | 2832 / 2872 | 0–20 bar | CAN, IO-Link, 0–10 V |
| Clippard | EV series | 0–7 bar | PWM, 0–10 V |
| SMC | ITV series | 0–9 bar | 0–10 V, RS-485 |

**What they do:** Accept an analog voltage or digital command and hold a set pressure.
**What they don't do:** Know anything about surfaces, grime, solar panels, or whether the
last zone passed verification. They are dumb actuators waiting for a setpoint.

#### 1b. Agricultural spray drones (closest analogue)

DJI Agras T40, XAG P100, and similar use electronically-controlled pump motors and
flow controllers to vary application rate across a field (variable-rate application, VRA).
These adjust **flow rate / volume**, not **pressure ceiling**, and they respond to
pre-loaded prescription maps — not to a live AI feedback loop.

**The key difference:** ag drones don't verify the *result* and adjust parameters in
response. They execute a static map. PROPWASH verifies and re-queues with pressure delta.

#### 1c. Industrial pressure-washing systems

Hotsy, Karcher, and others sell PWM-controlled pump bypass valves for commercial rigs.
These are ground-mounted, require 240V, and have no drone form factor.

#### 1d. Lucid Bots Sherpa

The Sherpa uses an onboard chemical tank with a variable-speed pump motor.
**No confirmed software-addressable pressure API exists** (CLAUDE.md §7).
The operator adjusts pressure via the controller. That manual step is precisely what
the device described in this document would automate.

---

### 2. The device PROPWASH could build — the PROPWASH PSM

**Name (working):** PROPWASH Pressure-Set Module (PSM)

#### What it is

A lightweight, drone-mountable electronics module that:

1. **Receives a target pressure setpoint** from the PROPWASH orchestrator (Tier 2) over
   a serial or CAN bus (not from an AI agent directly — the safety layer validates
   the setpoint first; see §4).
2. **Drives an electronic pressure regulator** (EPR) on the spray line between the pump
   and nozzle, holding actual pressure within ±0.1 bar of the setpoint.
3. **Reads actual line pressure** from a piezoelectric sensor at the nozzle manifold
   and streams it back to the orchestrator as telemetry.
4. **Enforces a hard pressure ceiling in firmware** — a per-surface-type limit that
   **cannot be overridden by any software command**, even a malformed one from the
   orchestrator. Solar ceiling: 2.0 bar. This is a firmware constant, not a config
   value. This is the device's core safety invariant.
5. **Has a physical pilot override button** on the controller that instantly drops
   pressure to idle and locks out the EPR until the pilot re-arms it.

#### Key components (BOM sketch)

| Component | Function | Off-the-shelf path |
|---|---|---|
| Miniature EPR | Hold line pressure to setpoint | SMC ITV0010 (0–1 MPa, 50 g) or Proportion-Air QB1 |
| Piezo pressure sensor | Measure actual nozzle line pressure | Honeywell MLH series |
| Microcontroller | Safety logic, PID loop, CAN/serial bridge | STM32G0 or RP2040 (50–100 g) |
| CAN transceiver | Isolated bus to orchestrator | MCP2562FD |
| Relay/mechanical shutoff | Pilot override — cuts pressure to zero | Latching relay |
| Enclosure | Dust/water ingress, vibration | IP65 ABS + vibration mounts |
| Total weight target | | < 250 g (including EPR) |

#### Weight reality check

The Sherpa carries ~10 kg of liquid plus spray hardware already. 250 g of electronics
is well within practical payload margin. Confirm with Lucid's payload specs before
committing to a specific target.

---

### 3. What makes this protectable IP

#### 3a. Utility patent — the method

The combination that is novel and non-obvious:

> **"A method of drone-borne surface cleaning comprising: sensing a surface zone with a
> thermal and visual imaging sensor; computing a residual-grime proxy score from said
> sensing; comparing said proxy score to a verification threshold; and, on failure,
> automatically commanding an electronic pressure regulator mounted on the spray drone
> to apply a prescribed pressure delta to a subsequent cleaning pass of said zone —
> wherein the pressure command is validated against a per-surface-type hard ceiling
> stored in regulator firmware before actuation."**

The core claim: **closed-loop, verification-driven, per-surface-aware pressure
adjustment via an onboard EPR on a spray drone.**

This is the same method patent discussed in `IP_PROTECTION.md` (§5), but now with a
hardware component that strengthens the claim — because you are not just describing
a software method, you are describing a specific hardware+software system that
*physically enforces* the prescribed pressure. Harder to design around.

Additional dependent claims to layer in with counsel:

- Firmware-enforced hard ceiling per surface type (solar, glass, stucco, etc.)
- Pilot physical override with lockout logic
- Telemetry streaming of actual vs. prescribed pressure for post-hoc deviation logging
- The specific combination of EPR + piezo feedback + CAN bus on a tethered spray drone

#### 3b. Trade secrets (keep these out of patent claims)

- The specific PID tuning parameters for pressure control under drone vibration
- The calibrated pressure-to-result lookup table that PROPWASH builds from field data
  (how much pressure delta is actually needed to re-clean a stucco wall vs. a clay tile)
- The firmware constants for each surface-type ceiling (beyond what patents require)
- Any novel vibration-compensation algorithm you develop for the EPR under drone flight

These are the brain. Patent the mechanism; keep the calibration as trade secret.

#### 3c. Industrial design / trademark

- The physical form factor of the PSM module (IP65 enclosure, mounting bracket design)
  can be protected as a design patent or trade dress once you have a production design.
- `PROPWASH PSM` or a variant could be trademarked as a hardware product sub-brand.

---

### 4. How PSM fits the PROPWASH architecture

```
PROPWASH orchestrator (Tier 2, ~1 Hz)
        │
        │  validated setpoint (already safety-gated by SafetyChecker)
        ▼
   PSM firmware (Tier 1 — NOT Tier 3)
   ┌────────────────────────────────────┐
   │ 1. Accept setpoint from Tier 2     │
   │ 2. Check vs. hard firmware ceiling │  ← cannot be bypassed by any software
   │ 3. Run PID loop → drive EPR        │
   │ 4. Stream actual pressure back     │
   │ 5. Pilot override → drop to idle   │
   └────────────────────────────────────┘
        │
        ▼
   Electronic pressure regulator → nozzle line
```

**Critical:** The PSM sits at **Tier 1** (deterministic, safety-authoritative), not Tier 3.
Claude agents (Tier 3) prescribe a target pressure. The orchestrator (Tier 2) validates it
with `SafetyChecker`. Only then does the validated setpoint reach the PSM. The PSM's
firmware ceiling is the last hardware-level guarantee before liquid leaves the nozzle.

This tiered design is important for two reasons:
1. It matches CLAUDE.md §2 — agents never sit inside a safety loop.
2. It makes the safety claim in your patent and in conversations with Lucid / FAA
   bulletproof: even a software bug in the orchestrator **cannot cause over-pressure**
   because the hardware enforces the ceiling independently.

#### What to add to `propwash/backend/safety/checks.py`

Add a check: `PSM_SETPOINT_EXCEEDS_FIRMWARE_CEILING` — when preparing a CAN message
for the PSM, confirm the setpoint ≤ the surface ceiling before the message is sent.
Belt-and-suspenders: firmware also checks, but the orchestrator should never send an
invalid setpoint in the first place.

---

### 5. The product business case — selling PSM to other operators

#### Who buys it

- Lucid Bots Sherpa operators who are not PROPWASH customers but want closed-loop
  pressure control for their own cleaning workflows
- Other commercial drone cleaning operators (not limited to Lucid hardware — any spray
  drone with an accessible pump line)
- Industrial inspection + cleaning service companies (bridges, cell towers, tanks)
- Potentially: rooftop solar O&M companies (large-scale utility solar farms need
  automated cleaning; this is a $1B+ global market)

#### Revenue model for PSM hardware

This becomes a **hardware product line** — separate from PROPWASH's service revenue.
Illustrative unit economics (validate before committing):

| Item | Estimate |
|---|---|
| BOM + manufacturing (contract manufacturer) | $400–600/unit |
| Target ASP | $1,800–2,500/unit |
| Gross margin | ~65–70% |
| Annual recurring: firmware updates / calibration subscription | $300–500/unit/yr |

A fleet of 100 PSM units at $2,000 ASP + $400/year = $200K hardware + $40K ARR.
Not the core business — but meaningful margin and a data-collection surface for
improving your own calibration tables.

#### The strategic reason to build it even if you don't sell many

Every PSM unit sold creates a data-collection endpoint: actual nozzle pressure vs.
prescribed pressure vs. verification result. That telemetry, aggregated across many
operators, accelerates PROPWASH's learning model faster than your own fleet alone.
This is the data flywheel extended to hardware.

**Important:** If you collect data from third-party PSM units, your customer contracts
for PSM must secure your right to use that telemetry for model improvement — same
principle as your service contracts (IP_PROTECTION.md §7).

---

### 6. Regulatory considerations before building hardware

- **FAA:** Adding electronics to a certificated drone is a **modification**. Under Part 107,
  this may require the operator to re-declare airworthiness. Work with Lucid to understand
  whether the PSM can be installed as an accessory within their airworthiness envelope,
  or whether you need to operate on hardware you own outright (Path C territory, §7).
- **EPA/state chemical applicator laws:** Varying spray pressure affects pesticide and
  chemical application rates. In some states, commercial chemical application is regulated.
  For DI water / degreaser on building exteriors this is typically low-risk, but verify
  with counsel for your California market.
- **UL/CE listing:** If you sell PSM as a product in commerce, you'll likely need UL
  recognition (US) or CE marking (EU). Factor this into your cost model. Budget $15–50K
  and 6–12 months for initial listing.
- **Product liability:** Hardware that controls pressure on a flying vehicle creates product
  liability exposure. Make sure the firmware-enforced ceiling and pilot override are
  documented, tested, and provable in court. Keep test logs.

---

### 7. Build roadmap for PSM

#### Phase 1 — Proof of concept (no drone required)
1. Buy an SMC ITV0010 EPR + piezo sensor + STM32 dev board.
2. Write firmware: receive setpoint via serial, run PID, stream actual pressure.
3. Validate pressure accuracy on a bench test rig (garden hose + pressure gauge).
4. Document the firmware hard-ceiling behavior with test logs — this is your IP evidence.

**Estimated cost:** ~$800 in parts. Timeline: 4–6 weeks (part-time).

#### Phase 2 — Drone integration
1. Work with Lucid (or on hardware you own) to tap the Sherpa spray line.
2. Mount PSM prototype, connect to a laptop running the orchestrator.
3. Run `sim/scenario.py` with `PSMTransport` (a new adapter) instead of `MockTransport`.
4. Fly controlled tests: did actual pressure match setpoint within ±0.1 bar under vibration?

#### Phase 3 — Miniaturization + enclosure
1. Contract a PCB layout shop to consolidate the prototype onto a 50×50mm board.
2. Design an IP65 enclosure + Sherpa-compatible mounting bracket.
3. Send to a contract manufacturer (JLCPCB, Tempo Automation) for small run (10–25 units).

#### Phase 4 — Patent + product launch
1. File the provisional **before** any public demo of the PSM (§5 of IP_PROTECTION.md).
2. Launch to beta operators. Collect telemetry data.
3. Convert provisional to utility within 12 months.

---

### 8. Near-future build: PROPWASH IHM (Integrated Head Module)

> **Phase 2 hardware — build after PSM is proven on-drone.**
> This is the stronger patent position and the device that eliminates manual nozzle swaps.

#### The problem PSM alone doesn't solve

With PSM, the operator still has to **land between surface types and manually swap the
nozzle tip** — a 25° narrow for solar, a 40° fan for stucco, a 45° fan for gutters.
Each swap takes 3–5 minutes and requires touching hardware on the drone. Across a
multi-zone job (solar array → façade → roof), that adds 10–15 minutes of dead time
per job and is a non-trivial source of human error (wrong tip installed for a zone).

#### What the IHM is

A servo-actuated nozzle-selector turret — a small revolver-style manifold holding
3–4 different nozzle tips — bolted directly to the spray arm, upstream of the exit point.
A single servo rotates the manifold to align the correct tip with the spray line.
Combined with the PSM, the orchestrator commands *both* parameters in a single message:

```
Zone: SOL-ROOF
  → IHM: rotate to tip slot 1  (25° narrow, 0.35 mm — solar safe)
  → PSM: set pressure 1.8 bar

Zone: STUCCO-N
  → IHM: rotate to tip slot 3  (40° fan, 0.6 mm — standard)
  → PSM: set pressure 4.0 bar

Zone: GUTTER-W
  → IHM: rotate to tip slot 4  (45° fan, 0.7 mm — heavy)
  → PSM: set pressure 6.5 bar
```

No landing. No manual swap. The system reconfigures itself between zones.

#### Key components (BOM sketch — IHM)

| Component | Function | Off-the-shelf path |
|---|---|---|
| Brushless servo (waterproof) | Rotate manifold to selected slot | Hitec D956WP or similar (35 g) |
| Stainless manifold body | 4-port nozzle carousel, splash-proof | Custom machined (SS or Delrin) |
| Position encoder / limit switches | Confirm correct slot aligned | Magnetic encoder (AS5600) |
| PSM microcontroller (shared) | Add IHM control to existing PSM firmware | No new MCU needed |
| Drip seal / O-ring set | Prevent cross-port leakage | Standard BSP O-ring kit |
| Total weight target | | < 180 g (excluding nozzle tips) |

The IHM shares the PSM's microcontroller and CAN bus — they are one integrated module
in the production version, two separate boards in the prototype phase.

#### Safety invariants for the IHM

Two rules enforced in firmware, same authority level as PSM pressure ceiling:

1. **Tip-pressure interlock:** The firmware stores a maximum pressure for each tip slot.
   If the orchestrator sends a pressure setpoint that exceeds the installed tip's ceiling,
   the firmware **clamps the pressure and logs a deviation** — it does not refuse the
   command outright (the zone still gets cleaned), but it protects the surface.
   Solar tip slot (slot 1): hard ceiling 2.0 bar regardless of commanded pressure.

2. **Rotation lockout under pressure:** The manifold servo will not rotate while line
   pressure is above 0.3 bar. Before switching tips, firmware drops pressure to idle,
   waits for sensor confirmation, then rotates. This prevents spray from the wrong
   orifice during transition.

#### Architecture — IHM added

```
PROPWASH orchestrator (Tier 2)
        │
        │  { tip_slot: 1, pressure_bar: 1.8 }  (validated by SafetyChecker)
        ▼
   PSM+IHM firmware (Tier 1)
   ┌──────────────────────────────────────────────┐
   │ 1. Accept { tip_slot, pressure } from Tier 2 │
   │ 2. Drop pressure to idle                     │
   │ 3. Rotate manifold → tip_slot                │
   │ 4. Confirm position via encoder              │
   │ 5. Ramp pressure to setpoint                 │
   │ 6. Check tip-pressure interlock              │  ← solar slot: hard 2.0 bar
   │ 7. Run PID loop, stream telemetry            │
   │ 8. Pilot override → pressure idle + lock     │
   └──────────────────────────────────────────────┘
```

#### The combined patent claim (PSM + IHM together)

This is the claim that matters most — file it as a dependent claim on the PSM
provisional, or as a separate continuation if IHM is proven after the provisional files:

> *"A spray system for an unmanned aerial vehicle comprising: (a) an electronic pressure
> regulator commanded by a surface-classification model output; (b) a servo-actuated
> multi-tip nozzle selector whose active tip is commanded by the same surface-
> classification model output; (c) firmware enforcing a per-tip-slot maximum pressure
> ceiling that cannot be exceeded by any software command; (d) a rotation interlock
> that prevents tip transition while line pressure exceeds an idle threshold; wherein
> pressure setpoint and nozzle geometry are co-prescribed in a single work-order message,
> validated against per-surface safety limits, and confirmed via onboard sensors before
> any cleaning pass commences."*

That is a very strong, very specific claim. Every element is novel in this combination.
Designing around it requires independently solving: (1) the closed-loop verification
feedback, (2) the per-surface ceiling enforcement, (3) the tip-pressure interlock, and
(4) the rotation lockout — all on a drone form factor. That's years of work.

#### What to trade-secret (not claim in the patent)

- The **tip-slot assignment** logic: which nozzle goes in which slot for a given job
  profile (based on the job's surface mix — this is a non-obvious optimization your
  data will calibrate over time).
- The **rotation timing model** under vibration: how long to wait for the manifold to
  settle before re-pressurizing (tuned from flight data, not derivable theoretically).
- The **per-surface deviation signatures**: what the pressure telemetry looks like when
  a nozzle is partially clogged vs. when the surface is absorbing more liquid than
  expected (early warning system for re-queue decisions).

#### Product positioning: PSM vs. PSM+IHM

| Product | What it replaces | ASP estimate | Target buyer |
|---|---|---|---|
| PSM only | Manual pressure knob adjustment | $1,800–2,500 | Any spray drone operator |
| PSM + IHM (integrated) | Manual pressure + manual nozzle swap | $3,500–5,000 | High-volume operators, solar O&M fleets |
| PSM + IHM + subscription | All of above + calibration updates, telemetry dashboard | $3,500 + $600/yr | Enterprise solar / commercial cleaning |

The IHM doubles the ASP without proportionally doubling the BOM cost (~$200 more in
parts for the servo + machined manifold + encoder). That's where the margin expansion lives.

#### Build roadmap for IHM

**Phase 1 (bench — no drone needed):**
1. 3D-print a 4-slot manifold prototype in PETG.
2. Mount a Hitec D956WP servo and AS5600 encoder.
3. Test rotation accuracy and the pressure-interlock logic on the PSM dev board.
4. Document with video + timestamped logs — invention evidence.

**Estimated cost:** ~$300 additional parts on top of PSM bench rig.
**Timeline:** 6–8 weeks after PSM bench phase completes (can overlap).

**Phase 2 (integration):**
1. Machine the production manifold in 316 stainless (corrosion resistance for chemical exposure).
2. Integrate IHM control into PSM firmware as a single unified module.
3. Mount on drone spray arm, run `sim/scenario.py` with `PSMIHMTransport`.
4. Fly multi-surface test job: solar → stucco → composite shingle, confirm no cross-zone contamination (DI water in solar slot, degreaser in stucco slot — manifold must not cross-contaminate).

**Phase 3 (production):**
1. PCB layout combines PSM + IHM control on one board.
2. IP65 enclosure designed to house EPR, servo controller, and manifold mounting interface.
3. File patent on PSM+IHM combined claim before first public demo.

---

### 10. What to do this quarter

**Now (PSM — the foundation):**
1. **Buy bench parts** (~$800: SMC ITV0010 EPR, STM32 Nucleo board, Honeywell pressure sensor)
   and validate the PID loop on a garden-hose rig. Dated test logs = invention evidence.
2. **Add `PSMTransport`** to `propwash/backend/execution/` behind `PROPWASH_ENABLE_PSM=true`.
3. **Talk to a patent attorney** this month about a hardware claim on the provisional.
4. **Ask Lucid** (outreach call, `docs/LUCID_OUTREACH.md`) whether PSM can be accessory-
   installed within their airworthiness envelope.

**Next quarter (IHM — the upgrade):**
5. **Add ~$300 in parts** to the bench rig: Hitec D956WP servo, AS5600 encoder, 3D-printed
   4-slot manifold prototype. Test rotation + pressure interlock logic.
6. **Extend PSM firmware** to handle tip-slot commands and rotation lockout.
7. **Add the combined PSM+IHM claim** to the patent application (or as a continuation)
   before any public demo of nozzle selection capability.
8. **Design the production manifold** in 316SS for chemical resistance.

---

### 11. Mental model

```
Patent the mechanism (EPR + feedback loop + firmware ceiling + pilot override).
Keep the calibration tables secret (what pressure delta fixes what surface — that's your data moat).
Sell the hardware to create more data endpoints.
Use the data to widen your calibration advantage over anyone who tries to copy you.
```

The PSM is not just a product — it is a *data-collection terminal* that accelerates the
flywheel described in `IP_PROTECTION.md §3`. Every unit sold by a third-party operator
is another sensor reporting back to PROPWASH's learning model.

<a id="docsflightsoftwarestack"></a>

---

# Deep Dive — Flight Software Stack (ROS 2 / PX4 / MAVLink / Auterion / Jetson)

> **Source file:** `docs/FLIGHT_SOFTWARE_STACK.md`

## Deep Dive — Flight Software Stack (ROS 2 / PX4 / MAVLink / Auterion / Jetson)

> The layer that decides whether PROPWASH's tech can actually **command** an aircraft.
> Directly answers Q1–Q10 of the Integration Qualification Questionnaire
> (`LAUNCH_PLAYBOOK.md` §1.0).
>
> ⚠️ **Regulatory line (CLAUDE.md §2, §7, §10):** everything below describes *technical*
> capability. Autonomous **flight** requires the appropriate FAA pathway/waiver with the
> operator in command. **Payload** control (pump/nozzle), gated by our Tier-1 safety layer, is
> the near-term target; flight autonomy is a separate, regulated step. No covert automation.

---

### 0. The headline

**On an open PX4 stack, all ten questions answer "yes" — and each is a documented,
off-the-shelf capability.** This is the strongest technical validation yet for the
open-platform direction (`decisions/OPEN_PLATFORM_INTEGRATION.md`).

| Your question | Open PX4 answer | Mechanism |
|---|---|---|
| 1. Public SDK/API? | ✅ Yes | MAVSDK (C++/**Python**/Swift/Kotlin), ROS 2, MAVLink |
| 2. Upload custom 3D flight paths? | ✅ Yes | **PX4 ROS 2 Waypoint Missions** / MAVSDK Mission API |
| 3. Command velocity/heading/altitude? | ✅ Yes | **Offboard Mode** (⚠️ FAA-gated — see §4) |
| 4. Real-time telemetry (pos/IMU/obstacle/range)? | ✅ Yes | uORB topics → ROS 2 (`px4_msgs`) / MAVLink streams |
| 5. Onboard Jetson/companion computer? | ✅ Yes, **officially supported** | Holybro Pixhawk **Jetson Baseboard**; Auterion Skynode |
| 6. Software pump/nozzle control by location? | ✅ Yes | **ActuatorServos / ActuatorMotors**; payloads triggerable **in missions** |
| 7. ROS 2 / MAVLink / PX4 / Auterion? | ✅ All four | native |
| 8. Customer-available or partner-gated? | ✅ **Open source** — no gate | PX4/Dronecode |
| 9. Warranty/certification impact? | ⚠️ You're the integrator | you own airworthiness (§5) |
| 10. Developer/OEM program? | ✅ Dronecode + Auterion partners | — |

**Compare:** Lucid Sherpa answers *no* to 1, 2, 6, 8. That contrast is the whole platform
argument in one table.

---

### 1. The layers (what each thing actually is)

| Layer | What it is | PROPWASH uses it for |
|---|---|---|
| **PX4** | Open-source flight-control firmware (the autopilot) | Tier 0 — flight stabilization. **We never touch this** (CLAUDE.md §2) |
| **MAVLink** | Lightweight open messaging protocol (drone ↔ GCS ↔ payload) | The wire protocol; vendor-neutral |
| **MAVSDK** | High-level SDK over MAVLink (**Python** bindings) | Simplest path: missions, telemetry, payload commands |
| **ROS 2** | Robotics middleware (nodes, topics, DDS) | Deeper integration: real-time control, sensor fusion |
| **Auterion OS / Skynode** | Commercial enterprise PX4 + mission computer in one module | Turnkey hardware+software; NDAA-compliant option |
| **Companion computer** (Jetson) | Onboard Linux computer running our code | Edge autonomy, CV, payload logic |

**Key relationship:** ROS 2 ↔ PX4 is bridged via **micro-RTPS / uXRCE-DDS**, exposing PX4's
internal uORB messages as ROS 2 topics (`px4_msgs`). Auterion has invested heavily in making
ROS 2 first-class for flying robots.

---

### 2. How PROPWASH's pipeline maps onto it (the important part)

Our Stage-5 output (`planning/coverage_path.py`) already emits waypoints + spray flags +
per-zone pressure. Here's the concrete mapping:

```
FlightPlan (ours)                    →  PX4/ROS 2 mechanism
────────────────────────────────────────────────────────────────
ZonePath.waypoints (x,y,z)           →  ROS 2 Waypoint Mission / MAVSDK Mission items
Waypoint.spraying (bool)             →  ActuatorServos setpoint (pump ON/OFF) at that item
Prescription.pressure_bar            →  ActuatorServos value → our PSM regulator setpoint
Prescription.nozzle_id               →  ActuatorServos → IHM turret position
traverse_speed_mps                   →  mission item cruise speed
KeepOut volumes                      →  geofence / mission planning exclusion
telemetry (actual pressure, pos)     →  uORB/ROS 2 topics → our deviation log + verify loop
```

**This is the "tech that communicates between them"** you've been describing — and on an open
stack it's a documented integration, not an R&D project.

#### Two implementation routes
- **MAVSDK-Python (recommended start).** Simplest; matches our Python backend; covers
  missions, telemetry, and actuator/payload commands. This is what `execution/
  mavlink_transport.py` should target first.
- **ROS 2 (later, if we need edge autonomy).** Deeper access, real-time control loops, and the
  natural home for on-aircraft CV — but heavier. Use if/when Tier-1 logic moves onboard.

---

### 3. Payload / pump control — how it actually works

The mechanism for Q6, and for PSM/IHM:

- **ActuatorServos / ActuatorMotors** let a companion computer or mission directly drive
  servo/motor outputs. A **pump, valve, or servo-driven nozzle turret is exactly this.**
- Payloads can be **triggered automatically within a mission** (i.e., spray ON at waypoint N),
  or commanded live via MAVLink/MAVSDK.
- So "spray at 4.0 bar along this sweep line, off during the repositioning leg" is a *native
  capability*, not a hack.

**Where our safety layer sits:** the Tier-1 `SafetyChecker` validates the pressure/nozzle
setpoint **before** any actuator command is emitted; the PSM firmware ceiling is the final
independent hardware guarantee (`DYNAMIC_PRESSURE_HARDWARE.md` §4). Agents never command an
actuator directly.

---

### 4. ⚠️ Offboard Mode — powerful, and the regulatory boundary

**Offboard Mode** is the PX4 flight mode where a companion computer commands
position/velocity/attitude — i.e., the software flies the aircraft. It's how Q3 is technically
answered "yes."

**But:**
- This is **autonomous flight**, which under Part 107 requires the operator in command and the
  appropriate FAA pathway/waiver for anything beyond that (CLAUDE.md §7, §10).
- It's also the highest-risk mode: a companion-computer fault becomes a flight-control fault.
  PX4 requires a continuous setpoint stream and fails safe if it stops.

**PROPWASH posture:** build the **payload** control path now (safe, useful, legal, and where
our IP lives). Treat Offboard flight control as a **later, waiver-gated** capability behind
`PROPWASH_ENABLE_PATH_C`. The coverage path remains **operator guidance** by default.

---

### 5. Hardware options for the companion computer

| Option | What it is | Notes |
|---|---|---|
| **Holybro Pixhawk Jetson Baseboard** | Pixhawk FC + NVIDIA **Orin** on one board | Officially documented in the PX4 guide; clean, integrated |
| **Auterion Skynode / Skynode S** | Flight controller + mission computer + video + networking + cellular, running Auterion OS (enterprise PX4) | Turnkey; **Skynode S is NDAA-compliant** → a real hedge against DJI regulatory risk |
| **Jetson Orin Nano/NX + separate FC** | DIY: Jetson + Pixhawk over serial/Ethernet | Cheapest, most flexible; you integrate it |

**Skynode is worth a serious look** — it collapses "flight controller + mission computer +
connectivity" into one supported module, and the NDAA compliance directly addresses the DJI
concentration risk flagged in `decisions/DJI_TWO_DRONE_ARCHITECTURE.md` §6.

---

### 6. What this changes strategically

1. **The open-platform path is technically de-risked.** Every capability PROPWASH needs is
   documented and supported on PX4 — no invention required at the integration layer.
2. **It sharpens the vendor comparison.** DJI = semi-open (PSDK, proprietary, vendor-gated).
   PX4/Auterion/Freefly = open (ROS 2 + MAVSDK + companion computers + actuator control, no
   gate). Lucid = closed. Score vendors against §1.0 with this in hand.
3. **It tells us what to build next in code:** implement `MavlinkPayloadTransport` against
   **MAVSDK-Python**, translating `FlightPlan` → mission items + `ActuatorServos` setpoints.
   The interface already exists and is flagged off.
4. **It's leverage with Lucid.** When you ask them Q1–Q10, you'll know exactly what an open
   platform provides — and can say so.

---

### 7. Open items
- [ ] Confirm MAVSDK-Python actuator API covers our pump/nozzle setpoint needs.
- [ ] Price Auterion Skynode / Skynode S; confirm NDAA status + partner terms.
- [ ] Decide MAVSDK-first vs ROS 2-first for `MavlinkPayloadTransport`.
- [ ] Spec the companion computer (Holybro Jetson baseboard vs Skynode vs DIY Orin).
- [ ] FAA: scope what a waiver would require before *any* Offboard-mode flight.

### Sources
- [PX4 Companion Computers](https://docs.px4.io/main/en/companion_computer/) · [PX4 ROS 2 Control Interface](https://docs.px4.io/main/en/ros2/px4_ros2_control_interface) · [PX4 ROS 2 Waypoint Missions](https://docs.px4.io/main/en/ros2/px4_ros2_waypoint_missions) · [PX4 Offboard Mode](https://docs.px4.io/main/en/flight_modes/offboard)
- [Holybro Pixhawk Jetson Baseboard](https://docs.px4.io/main/en/companion_computer/holybro_pixhawk_jetson_baseboard) · [Auterion Skynode (PX4 guide)](https://docs.px4.io/main/en/companion_computer/auterion_skynode)
- [Auterion — driving ROS 2 adoption](https://auterion.com/auterion-driving-ros-2-adoption-for-flying-robots/) · [Skynode S](https://auterion.com/product/skynode-s/) · [PX4 messages in ROS 2 (Auterion docs)](https://docs.auterion.com/app-development/app-framework/px4-messages-in-ros-2)

<a id="docscommunicationandautonomy"></a>

---

# Deep Dive — Communication Architecture & the Autonomy Ladder

> **Source file:** `docs/COMMUNICATION_AND_AUTONOMY.md`

## Deep Dive — Communication Architecture & the Autonomy Ladder

> How the two drones and PROPWASH actually talk, what happens when links fail, and how much
> autonomy is legally reachable — now and under the FAA's proposed **Part 108**.
>
> ⚠️ Regulatory content is **not legal advice** and Part 108 is a **proposed rule, not law**
> (NPRM comment period closed Feb 2026; final rule pending). Verify with an aviation attorney
> before operating on any assumption here.

---

### 0. The headline finding

**The FAA's proposed Part 108 would make BVLOS operations run *autonomously on pre-programmed
flight paths*, and would let a single "Flight Coordinator" supervise *multiple aircraft*.**

Read that against what we've built: `planning/coverage_path.py` **already generates
pre-programmed flight paths**, and `execution/mavlink_mission.py` **already translates them into
uploadable missions**. If Part 108 lands substantially as proposed, PROPWASH's architecture is
pointed directly at the regime the regulation creates — and the labor model in
`SCALING_TO_10M.md` (1 pilot per crew) becomes conservative.

**This is a tailwind, not a pivot.** But it is *proposed*, so plan for Part 107 today and
build so Part 108 is an unlock, not a rewrite.

---

### 1. The communication architecture (three independent links)

A common mistake is imagining one "connection." There are **three**, with different
requirements, and conflating them is how systems fail badly.

| Link | Carries | Rate | Loss tolerance |
|---|---|---|---|
| **C2 (command & control)** | flight commands, RC, heartbeat | 10–50 Hz | ❌ **Zero** — loss triggers failsafe |
| **Payload/telemetry** | pump/nozzle setpoints, actual pressure, position | 1–10 Hz | ⚠️ Low — degrade to safe state |
| **Data/imagery** | thermal + RGB frames, point clouds | bulk, offline | ✅ **High** — can be post-flight |

#### Why our loose-sync design is architecturally right (CLAUDE.md §6)
The scout and cleaner **never talk to each other** — they sync through *the plan*. That means:
- No real-time cross-aircraft link to fail.
- Survey data moves as **bulk transfer** (Link 3), where latency is irrelevant.
- The cleaner only needs Links 1–2, both local to its own operation.

This is the difference between a system that degrades gracefully and one that has a
single point of catastrophic failure. It was the right call and this research confirms it.

#### Bandwidth reality
- **Telemetry** is tiny (KB/s) — real-time is easy.
- **Imagery is enormous.** A survey is GBs of thermal + RGB. Do **not** design for live
  streaming of survey data to the cloud; **process locally** (Mac Studio, `decisions/
  COMPUTE_INFRASTRUCTURE.md`), transfer in bulk. This also protects the data moat.

---

### 2. Latency budget — which decisions can live where

Latency is what determines *where* a decision is allowed to run. Map it to CLAUDE.md §2 tiers:

| Tier | Decision | Budget | Where it MUST run |
|---|---|---|---|
| 0 | Flight stabilization | 2–20 ms | **On the flight controller.** Never us. |
| 1 | Collision avoid, geofence, pressure ceiling, **human-presence halt** | 30–100 ms | **On-aircraft / companion computer** — local, deterministic |
| 2 | Zone sequencing, work-order dispatch | ~1 s | Ground station / backend |
| 3 | Claude agents — planning, prescription, verification reasoning | seconds | Cloud; **advisory only** |

**The rule this enforces:** anything safety-critical must run where a dropped link cannot
delay it. That's why the safety layer is local and deterministic, and why Tier-3 agents are
advisory. A cloud round-trip (100–500 ms, unbounded on failure) is **categorically unsafe** for
a Tier-1 decision — this is the engineering reason behind the architectural rule, not just
policy.

---

### 3. Link failure — the failsafe ladder (the part that actually matters)

Design for the link failing, because it will. PX4 provides the mechanisms; we define policy.

| Failure | Detection | Required response |
|---|---|---|
| **Companion computer dies** | heartbeat timeout | **Pump OFF**, hold/return; flight controller unaffected (Tier 0 independent) |
| **C2 link lost** | RC/GCS timeout | PX4 failsafe: hold → RTL → land. **Pump OFF first.** |
| **Payload link lost** | setpoint stream stops | **PSM firmware fails to idle** — the independent hardware guarantee |
| **Offboard setpoint stream stops** | PX4 requires continuous stream | PX4 auto-exits Offboard → failsafe mode |
| **GPS degraded** | fix quality | Abort spray; no position = no valid coverage path |
| **Human detected mid-pass** | Tier-1 thermal check | **Immediate pump OFF + halt** (`safety/human_detection.py`) |

#### The invariant to hold everywhere
> **Any communication failure results in the pump going OFF and the aircraft entering a safe
> state. There is no failure mode in which spraying continues without positive control.**

Two independent mechanisms enforce this: (1) software failsafe policy, and (2) the **PSM
firmware ceiling + idle-on-signal-loss** (`DYNAMIC_PRESSURE_HARDWARE.md` §4). Defense in depth
— a software bug alone cannot cause uncontrolled spray.

**Build implication:** `mavlink_mission.py` already forces **pump OFF at the end of every
zone**. Extend that to a heartbeat/watchdog when the live transport is implemented.

---

### 4. The autonomy ladder — what's reachable, in order

Not binary. Five rungs, increasing capability *and* regulatory burden:

| Rung | Capability | Regulatory status | PROPWASH |
|---|---|---|---|
| **0** | Manual flight, manual spray | Part 107 today | Sherpa today |
| **1** | **Operator flies; software guides + controls the payload** (pressure/nozzle by position) | **Part 107 — legal now**, operator in command | ⭐ **Our near-term target** |
| **2** | Software flies pre-programmed paths, VLOS, pilot supervising | Part 107 (+ possible waiver) | Achievable on open stack |
| **3** | BVLOS autonomous on pre-programmed paths | Part 107 **waiver** today → **Part 108** if finalized | Where the economics improve |
| **4** | One coordinator, **multiple aircraft** | **Part 108 proposal** (Flight Coordinator + SUI) | The scaling unlock |

#### Rung 1 is the whole near-term game
**Payload autonomy is legal today** — the operator flies, our software sets pressure/nozzle by
location. That's where the PSM/IHM IP lives, it needs no waiver, and it delivers most of the
value (consistent, prescription-accurate cleaning + verification). **Build rung 1 now; don't
wait on regulation.**

#### What Part 108 would change (if finalized as proposed)
- Replaces today's case-by-case **Part 107 BVLOS waivers** with a standing framework.
- BVLOS conducted **autonomously on pre-programmed flight paths** — exactly our Stage-5 output.
- New roles: **Operations Supervisor** + **Flight Coordinator**; a coordinator may supervise
  **multiple aircraft** where manufacturer specs permit, with **Simplified User Interaction**
  reducing the human-in-the-loop burden.
- Shifts accountability toward the **organization**, not just the individual pilot.

**Business impact:** `SCALING_TO_10M.md` assumes one pilot per crew. Under rung 4, one
coordinator running several aircraft **breaks the linear labor↔revenue coupling** — the single
biggest constraint in the $10M model. Don't re-plan on it yet (proposed ≠ law), but note that
the current plan is the *conservative* case.

---

### 5. What to build now (so Part 108 is an unlock, not a rewrite)

1. **Rung 1, fully** — `MavlinkPayloadTransport` live: upload missions, drive
   ActuatorServos, read telemetry back. Operator flies. **No waiver needed.** ✅ translator done
2. **Watchdog/heartbeat** — pump OFF on any link or companion-computer timeout (§3).
3. **Keep Tier-1 local** — never let a safety decision depend on a cloud round-trip (§2).
4. **Keep the path machine-readable** — our `FlightPlan` → mission translation is already the
   artifact a Part 108 regime would want. Preserve that shape.
5. **Log everything** — Part 108 leans on organizational accountability; execution-vs-
   prescription logs and safety-event records become compliance evidence *and* feed the
   learning model. Dual-purpose.
6. **Track the rulemaking** — final rule pending. Revisit `SCALING_TO_10M.md` labor
   assumptions if rung 4 becomes real.

---

### 6. Open items
- [ ] Aviation attorney: current Part 107 posture + what a BVLOS waiver would require today.
- [ ] Confirm PX4 failsafe configuration matches the §3 ladder on the chosen airframe.
- [ ] Implement heartbeat/watchdog → pump-OFF in the live transport.
- [ ] Monitor Part 108 final rule; re-run the revenue model under a multi-aircraft coordinator.
- [ ] Confirm manufacturer specs on any platform re: multi-aircraft supervision (Part 108 gates
      this on "where manufacturer specifications permit").

### Sources
- [FAA Part 108 explained — Pilot Institute](https://pilotinstitute.com/part-108-explained/) · [Part 108 complete guide 2026 — UAVHQ](https://uavhq.com/blog/faa-part-108-complete-guide-bvlos-2026/) · [Part 108 vs Part 107 — DroneBundle](https://dronebundle.com/blog/part-108-vs-part-107)
- [New FAA BVLOS rules (Parts 108 & 146) — Skydio](https://www.skydio.com/blog/drones-faa-bvlos-waivers-new-rules) · [BVLOS: shift from waivers to Part 108 — Drone U](https://www.thedroneu.com/blog/bvlos-drone-operations-part-108/) · [Part 108 NPRM: what matters — DRONELIFE](https://dronelife.com/2025/08/08/matt-sloane-read-the-entire-faa-part-108-nprm-so-you-dont-have-to-heres-what-actually-matters/)
- [PX4 Offboard Mode](https://docs.px4.io/main/en/flight_modes/offboard) · [PX4 Companion Computers](https://docs.px4.io/main/en/companion_computer/)

<a id="docsfieldoperations"></a>

---

# PROPWASH — Field Operations, End to End

> **Source file:** `docs/FIELD_OPERATIONS.md`

## PROPWASH — Field Operations, End to End

> The realistic sequence for one job: **qualify → scout → map → prescribe → wash → verify → close**.
>
> Companion docs cover *what to build* (`3D_DATA_PIPELINE.md`, `THERMAL_LAYERING_PIPELINE.md`),
> *what to buy* (`docs/decisions/`), and *what to ask vendors* (`LAUNCH_PLAYBOOK.md`).
> **This doc is the day itself** — clock times, who does what, and where the process breaks.
>
> Timings marked ⏱ are computed by the planner on the reference house
> (`sim/export_house_3d.py`): **363 m² of surface, 20 cleanable zones, 980 m of flight path**.
> Everything else is an estimate to validate in the field.

---

### 0. What actually exists today — read this first

Do not plan a customer job around software that isn't written. Honest status:

| Stage | Built | Runs on real data? | Gap |
|---|---|---|---|
| Geometry ingest | ✅ `geometry/source.py` | ❌ synthetic only | `SfmSource` is a documented seam — needs the Metashape/ODM mesh reader |
| Thermal registration | ✅ `fusion/thermal_registration.py` | ⚠️ needs real R-JPEG parsing | radiometric extraction from Autel files not written |
| Surface classification | ✅ `segmentation/` | ⚠️ heuristic on RGB hints | real per-face texture sampling not written |
| Grime proxy | ✅ per-face layer | ⚠️ **uncalibrated** | constants are guesses (§5 of CLAUDE.md) |
| Prescription + safety gate | ✅ `planning/`, `safety/` | ✅ logic is real | pressure table is unvalidated defaults |
| Coverage paths | ✅ `planning/coverage_path.py` | ✅ emits real waypoints | no aircraft consumes them yet |
| Work-order dispatch (Path A) | ✅ | ❌ | **no confirmed Lucid API** |
| Direct flight/pump control (Path B/C) | ⚠️ translator only | ❌ | vendor answers outstanding |
| Verification loop | ✅ logic | ❌ | see the **dry-down problem**, §6 |

**Translation: today you can run the whole loop in the simulator, and you can fly a scout
mission and produce a customer-facing twin by hand. You cannot yet fly a prescription.**
Year-1 revenue comes from *operators executing our work orders*, exactly as CLAUDE.md §7 Path A
says — the software's job is to decide, not to fly.

---

### 1. Qualify the site — before anyone drives out

Roughly 30 minutes at a desk. Kills bad jobs cheaply.

**1.1 Airspace.** Check the address against the FAA UAS Facility Map. **Much of Carlsbad sits
under McClellan-Palomar (CRQ) controlled airspace**, which means LAANC authorization per flight,
with a ceiling that may be well below the height you want. Verify per address — do not assume
the base market is uncontrolled. If a site needs a ceiling LAANC won't grant, it needs a further
authorization and a different quote.

**1.2 Ground risk.** Schools, busy roads, HOA common areas, neighbouring pools, parked cars.
Part 107 prohibits flight over uninvolved people; a spray drone makes that stricter in practice,
because overspray reaches further than the aircraft.

**1.3 Water and runoff.** Two separate questions:
- **Supply** — is there a spigot with usable pressure and a place to stage the pump/tank? The
  recommended rig is *untethered flight, tethered water* (`decisions/CLEANING_DRONE_PLATFORM.md`
  §2), so a hose route matters.
- **Discharge** — wash water carrying detergent entering a storm drain is a **regulated
  discharge in California**. Confirm the applicable municipal BMP requirements and plan
  containment before quoting. This is a real compliance cost, not a footnote. *(Verify the
  current local rules — they change and vary by jurisdiction.)*

**1.4 Surfaces that change the price.** Solar (slowest and most constrained — §5.2), single-pane
or failing window seals, painted stucco in poor condition, anything already failing. Photograph
pre-existing damage. **Damage you didn't document is damage you caused.**

**1.5 Consent.** Property owner in writing. Neighbours notified if you'll be flying near a
shared boundary — cheaper than the complaint.

> **Gate:** airspace OK + water in and out solved + owner consent → schedule the scout.

---

### 2. Scout flight — capture

⏱ **On site 45–60 min.** One pilot (RPIC), Autel EVO MAX 4T V2.

**2.1 The weather window is narrower than you think.** The thermal grime proxy reads
*evaporative cooling* — surfaces that hold water read cooler than the dry surface around them
(`scan_pipeline.py`). That only works when:

- **Surfaces are dry and sun-loaded.** Coastal Carlsbad's morning marine layer flattens thermal
  contrast completely. Practical window: **~10:00–15:00**, no rain in the preceding ~24 h.
- **No wind driving overspray or shaking the airframe** — and wind also dries surfaces
  unevenly, which the proxy will read as grime.

**A scan in the marine layer is not a degraded scan, it is a useless one.** Reschedule.

**2.2 Flight pattern.** Two passes, both automated missions:
1. **Nadir grid** — camera straight down, ~70–80 % forward / ~65–70 % side overlap. Builds the
   roof and the overall structure.
2. **Oblique orbits** — camera at ~45°, flown around the building at two heights. Without these
   the walls reconstruct badly and the façades — half your billable area — come out as mush.

Capture RGB and thermal **as a co-registered pair on the same gimbal**. This is the single
biggest reason for the 4T V2: it turns cross-sensor alignment from a per-frame problem into a
fixed boresight constant (`THERMAL_LAYERING_PIPELINE.md` §1).

**2.3 Ground truth the pilot collects while there.** Ten minutes that save an hour later:
- Note the utility meter, gas line, AC condenser, satellite dish, skylights, vents — everything
  the classifier should exclude. The pipeline catches HVAC and roof protrusions; it will not
  catch a koi pond.
- Photograph any existing damage.
- Confirm the water spigot works and note the hose route.

**2.4 Known reconstruction failures — expect them.** Glass and solar panels are specular:
photogrammetry either drops them or produces noise. Windows and arrays often need to be placed
from the geometry around them rather than reconstructed directly
(`3D_DATA_PIPELINE.md` §2d). Budget for manual cleanup on those zones.

> **Gate:** enough coverage, in-window conditions, exclusions noted → leave site.

---

### 3. Process — and the latency that shapes the whole business

⏱ **1–3 hours of compute for a single-family house**, unattended, on the Mac Studio
(`decisions/COMPUTE_INFRASTRUCTURE.md`). Larger commercial sites: considerably longer.

Order matters and is not negotiable:

1. **RGB builds the geometry.** Align → dense cloud → mesh. Thermal cannot feature-match; its
   "landmarks" move with temperature (`THERMAL_LAYERING_PIPELINE.md` §2).
2. **Thermal supplies the values.** Re-project the IR set onto that mesh.
3. **Our Stage-2 registration** produces view-angle-weighted, reflection-rejected per-face °C
   with a confidence score. Metashape gives you a pretty thermal-textured model; it does **not**
   give you this, and this is what the decisions are made from.
4. **Classify + score** — per-face surface type and the per-face grime proxy.

#### ⚠️ This latency forces a two-visit model

You cannot scan at 09:00 and wash at 09:30. The realistic options:

| Model | How it works | Verdict |
|---|---|---|
| **Scan day / wash day** | Batch 4–6 properties in one scouting morning, process overnight, wash them over following days | ✅ **Recommended.** Amortises drive time, keeps the compute off the critical path, and the twin becomes a *sales asset* you show before the customer commits |
| Same day, long gap | Scan at 09:00, process on site or in the van, wash at 14:00 | Possible, but the crew is idle or must have a second job nearby — and 14:00 is the wrong window for solar |
| Scan-only product | Sell the inspection/twin as its own service | ✅ Worth testing — it's revenue with **no spray liability at all** |

The batching model is not a workaround. It is a better business: it separates a cheap,
low-risk, high-margin scouting operation from an expensive, liability-heavy wash operation, and
it lets you quote from data instead of from a walk-around.

---

### 4. Prescribe and review — the human gate

⏱ **10–20 min at a desk.**

The Supervisor agent produces a per-zone prescription; the deterministic safety layer gates it
(`safety/checks.py`). **A human reviews before anything is dispatched.** What the reviewer is
actually checking:

- **Every exclusion is correct** — and, more importantly, that nothing that *should* be excluded
  was missed. The classifier is conservative but it is a scaffold with an uncalibrated scorer.
- **Solar zones read DI-water-only, under the hard ceiling, in every phase.** This is the most
  failure-sensitive surface on the property; detergent residue cuts panel output and pressure
  cracks cells.
- **Grime scores pass a sanity check against the RGB.** If a zone reads 60 % grime and looks
  clean in the photo, the thermal was probably confounded — shade, a wet patch, a reflection.
- **The classifier's low-confidence zones.** Anything under ~50 % gets human eyes.

> **Gate:** reviewer signs the work order. This signature is also the audit-log entry
> (`safety/audit_log.py`) — it is what a waiver application or a liability claim will ask for.

---

### 5. Wash day

⏱ **Planner says 114 min of active spray time** for the reference house — 20 zones, 60 passes,
980 m of path. That is *airborne spray time only*. The real day:

| Block | ⏱ | Notes |
|---|---|---|
| Arrive, brief, walk the site | 20 min | re-verify nothing changed — cars moved, windows opened, dog outside |
| Set up water, pump, hose route, staging | 25 min | |
| Pre-flight, LAANC, weather check | 15 min | |
| **Spray passes** | **114 min** | planner output |
| Battery swaps | **20–40 min** | see §5.1 — this is not a rounding error |
| Nozzle changes, refills, repositioning | 20 min | |
| Pack down | 20 min | |
| **Realistic on-site total** | **≈ 4–4.5 h** | one house, one crew, one aircraft |

#### 5.1 Battery swaps are a first-class cost

A spray drone carrying water is heavy, and heavy means short. At 114 min of airborne time:

| Endurance | Flights | Swaps | Added time |
|---|---|---|---|
| 8 min | 14.3 | ~13 | +40 min |
| 12 min | 9.5 | ~9 | +26 min |
| 15 min | 7.6 | ~7 | +20 min |
| 20 min | 5.7 | ~5 | +14 min |

**Get the real endurance figure from the vendor *with a full tank*, not the marketing number.**
Then buy enough batteries and a fast charger that swapping never blocks the job. This is also
the strongest argument for a **water tether** — it removes the tank weight and buys endurance
back without grounding the aircraft.

#### 5.2 Ordering constraints the planner already enforces — and one it doesn't

The planner sequences solar-first and top-down (`planning/zone_ordering.py`): you wash top-down
so runoff never re-dirties finished work, and solar first because it's the most sensitive.

**What the planner does not know: solar panels must not be washed hot.** Cold water on
sun-loaded glass is a thermal-shock risk, and industry practice is early morning or evening.
That collides directly with §2.1:

> **The scan window (10:00–15:00, sun-loaded) and the solar wash window (early/late, cool) are
> mutually exclusive.** This is another reason scan day and wash day are different days.

*TODO(PROPWASH): encode a per-surface time-of-day constraint in the scheduler. Today it is the
crew's job to remember.*

#### 5.3 Treatment phases

Each zone gets pre-soak → chemical → **dwell** → rinse. Pre-soak and rinse are water-only by
construction. Dwell occupies no aircraft, which is why the scheduler can pipeline it — but on
this house deconfliction caps concurrency at **1 aircraft**, so there is nothing to pipeline
*into*. Multi-aircraft pays off on large commercial and solar sites, not compact residential.

#### 5.4 The operator stays in command

Part 107, always. The app says which nozzle to fit and when to begin; the operator confirms,
executes, monitors video plus the thermal overlay, and can abort at any moment. The system is
designed to reduce the *skill* required, never the *authority*.

---

### 6. Verify — and the problem nobody warns you about

#### ⚠️ The dry-down problem

**Our grime proxy reads wet as dirty.** Immediately after washing, every surface is soaked, so a
verification thermal scan run right away reports the whole building as maximally soiled. Worse,
a *drying* surface dries unevenly, so you get a confident, detailed, completely spurious grime
map.

This is not a bug in the code — it is a physical limit of inferring soiling from evaporative
cooling. Options, in order of preference:

1. **Dry-down window, then re-scan.** Correct, but the length is unknown — a function of sun,
   humidity, wind and material. Coastal afternoon: plausibly 30–90 min. Marine layer: possibly
   hours. **Needs field calibration before it can be promised to a customer.**
2. **RGB-primary same-day verification.** Visible staining is not confounded by water in the
   same way. Thermal demoted to secondary. Less sensitive, but honest and available now.
3. **Next-visit verification.** The pre-scan of the *next* service becomes the verification of
   the last one. Free, rigorous, and fits the recurring-contract model — but too slow to close
   out today's job.

**Recommendation:** ship RGB-primary same-day verification, run the thermal re-scan as a
research capture to calibrate the dry-down curve, and only promise thermal verification once
you have real data. Do not market thermal verification before then.

> **OPEN — needs Kevin + field data:** the dry-down curve per surface class. Until it exists,
> the post-clean thermal residual is not a number to put in front of a customer.

#### 6.1 The re-queue loop

Failed zones get adjusted parameters and re-queue. Under a same-day RGB verification the
adjustment is bounded — you can raise dwell or re-run a pass, but you cannot chase a thermal
residual you can't yet trust.

#### 6.2 The deviation log

Every job records prescribed-vs-actual: pressure, dwell, standoff, coverage, outcome. **This is
the flywheel.** The uncalibrated defaults in the surface table only become real numbers by
accumulating these deltas across jobs. Treat the log as the product, not as telemetry exhaust.

---

### 7. Close

⏱ **15 min, mostly automated.**

- Customer report: before/after twin, per-zone results, what was excluded and why.
- Invoice.
- Schedule the next service — and note that its pre-scan verifies this one (§6, option 3).
- Push the deviation log into the learning set.

The report is a genuine differentiator. Nobody else in exterior cleaning hands the customer a
3D model of their own building with the dirt mapped on it, before and after.

---

### 8. Failure modes, ranked by how much they cost you

| Failure | Cost | Mitigation |
|---|---|---|
| **Damage to solar panels** | Catastrophic — replacement plus reputation | Hard pressure ceiling in the safety layer, DI water only, never wash hot, never let an agent override |
| **Detergent into a storm drain** | Regulatory, fines, reputational | Containment plan before the quote (§1.3) |
| **Scan in the marine layer** | Wasted trip; worse, a *confident wrong* grime map | Weather gate before dispatch; refuse to process an out-of-window capture |
| **Verification run wet** | Wrong PASS/FAIL, wrong re-queue, customer dispute | §6 — RGB-primary until dry-down is calibrated |
| **Windows/solar reconstruct badly** | Manual cleanup, schedule slip | Expect it, budget the cleanup, oblique passes |
| **Battery logistics under-planned** | Job over-runs into a bad wash window | §5.1 — buy the batteries |
| **Flying without LAANC in CRQ airspace** | Certificate action | Per-address check in qualification, every time |
| **Uncalibrated grime scores quoted as fact** | Erodes the thing that makes you different | Label the proxy as a proxy, everywhere, including in customer copy |

---

### 9. Crew and kit

**Year 1: one crew of two.**

| Role | Does |
|---|---|
| **RPIC (Part 107)** | Flies both aircraft, owns the go/no-go, owns the abort |
| **Ground tech** | Water, hose, pump, batteries, nozzle changes, containment, customer contact |

The RPIC is the licensed, non-delegable role. The ground tech is trainable in days. That ratio
is what makes the model scale — and it is why the software's job is to remove *skill*
requirements, not authority.

#### Kit
Scout drone + spare batteries · cleaning drone + **enough batteries to never wait** · fast
charger · pump and hose · chemical stock, measured and labelled · nozzle set (see the IHM
concept in `DYNAMIC_PRESSURE_HARDWARE.md` for removing manual changes) · containment (berms,
vacuum, mats) · ground station laptop + LTE · cones, signage, PPE.

---

### 10. The honest summary

**Per house, scan day and wash day:**

| | Time | Who |
|---|---|---|
| Qualification | 30 min | desk |
| Scout flight | 45–60 min on site | RPIC |
| Processing | 1–3 h compute, unattended | machine |
| Prescription review | 10–20 min | human, mandatory |
| **Wash day** | **4–4.5 h on site** | crew of 2 |
| Verification | 15 min (+ dry-down window) | crew |
| Close | 15 min | mostly automated |

**Roughly one house per crew per wash day**, with scouting batched separately.

Three things decide whether this works, and none of them are the drone:

1. **Traverse speed.** Job time is path length ÷ speed. The current 0.2–0.35 m/s defaults are
   conservative guesses; at 2× the reference house drops from 114 to **57 min of spray time**.
   Every hour of field calibration that safely raises traverse speed is worth more than any
   hardware upgrade.
2. **The dry-down curve.** Until it's measured, the verification half of the closed loop —
   the defensible IP — cannot be sold as thermal.
3. **A vendor answering the integration questionnaire.** Until one does, the software prescribes
   and a human flies. That is a real business; it is just not the one the patent describes.

<a id="docslaunchplaybook"></a>

---

# PROPWASH — Launch Playbook

> **Source file:** `docs/LAUNCH_PLAYBOOK.md`

## PROPWASH — Launch Playbook

> One place for the *practical* launch essentials: **what to ask vendors**, the **open-source
> stack to build on**, the **steps to first revenue**, and an **index of everything already
> built** in this repo. Pairs with the decision notes in `docs/decisions/`.

---

### Part 1 — Questions to ask every vendor

#### ⭐ 1.0 THE INTEGRATION QUALIFICATION QUESTIONNAIRE (send this to EVERY manufacturer, before buying anything)

**The governing principle: integration capability matters more than PSI.** A drone that sprays
at 4,500 PSI but can't accept our flight paths or expose telemetry is a dead end for PROPWASH;
a weaker drone with an open SDK is a platform. Ask these *first*, of every vendor, in writing.

| # | Question | Why it decides the deal |
|---|---|---|
| 1 | **Do you provide a public SDK or API?** | Gate zero. No SDK = Path A work-orders only, forever. |
| 2 | **Can an external application upload custom 3D flight paths or waypoint missions?** | This is literally what our Stage-5 `coverage_path.py` emits. If they can't consume it, our flight-path IP can't reach their aircraft. |
| 3 | **Can we command velocity, heading, altitude, and standoff distance programmatically?** | Standoff + traverse speed *are* the prescription. Note: real-time flight command is FAA-gated (§7/§10) — ask to know the ceiling, deploy only within the waiver. |
| 4 | **Is there real-time telemetry — position, IMU, obstacle sensors, range data?** | Feeds verification, the deviation log, and the data flywheel. No telemetry = no learning loop. |
| 5 | **Can we run an onboard NVIDIA Jetson or companion computer?** | Whether Tier-1/edge logic can live on the aircraft (Path C). |
| 6 | **Can our software control the spray pump/nozzle based on location?** | The core of the closed loop + where PSM/IHM lives. The single most important hardware-IP question. |
| 7 | **Can we use ROS 2, MAVLink, PX4, or Auterion APIs?** | Open standards = portable, vendor-neutral integration (our `MavlinkPayloadTransport`). Proprietary-only = lock-in. |
| 8 | **Is the interface available to customers, or only internal/engineering partners?** | ⭐ The flush-out question. Many "yes we have an API" answers die here. |
| 9 | **Will custom software void the warranty or certification?** | Ask before spending $75K, not after. Ties to airworthiness + liability. |
| 10 | **Is there a supported developer or OEM partnership program?** | Whether this becomes a partnership or a fight. |

**Scoring (use it as a go/no-go):**
- **Open platform** — yes to 1, 2, 4, 7, 8 → viable for the full closed loop; hardware IP possible.
- **Semi-open** — yes to 1, 2, 4; no/partner-gated on 6–7 → good scout, limited cleaner.
- **Closed** — no to 1/2/8 → **Path A work orders only** (Lucid Sherpa sits here today).

> Send this verbatim. Get answers **in writing** — a sales "yes, we support integration" is not
> an answer to Q8. Record each vendor's replies in `docs/decisions/CLEANING_DRONE_PLATFORM.md`.

---

#### Vendor-specific follow-ups (after the Q1–10 baseline)

#### 1A. Lucid Bots (cleaning drone — Path A first)
Full list in `docs/LUCID_OUTREACH.md`. The five that matter most:
1. Does **Lucid Refresh** expose an API (REST/GraphQL/webhooks)? Can we **read** job status/
   telemetry and **push** structured work orders?
2. Any supported way to send **pump/pressure/dwell setpoints** (MAVLink or partner endpoint)? Roadmap?
3. Policy on **companion computers / third-party hardware** on an owned Sherpa — warranty impact?
4. **Who owns** the job/sensor data generated on a customer's Sherpa?
5. Partner/reseller economics — will Lucid **co-sell** to operators who want our intelligence layer?

#### 1B. DJI (scout + retrofit cleaning drone — the owned-stack path)
Ref `docs/decisions/DJI_TWO_DRONE_ARCHITECTURE.md`.
1. Confirm **Matrice 4T** price/lead-time + thermal spec vs the **Zenmuse H30T** for our needs.
2. Does **Cloud API (MQTT)** give us the telemetry/imagery ingest + mission dispatch we need?
3. Does **Payload SDK (PSDK v3)** support commanding a **pump/nozzle** payload (our PSM/IHM)?
4. Does mounting a third-party cleaning payload **void warranty**? What's the airworthiness stance?
5. NDAA/procurement exposure for US commercial use — any restrictions we should plan around?

#### 1C. Retrofit cleaning-payload vendors — Foxtech / drone-payload
Ref `docs/decisions/CLEANING_DRONE_PLATFORM.md`.
1. **Price** of the AeroClean (P3/T50, T-M400C) or RT-AP3 kit — the biggest unknown in the model.
2. Which **DJI airframes** are supported (M350 / M400)? Tethered vs untethered water?
3. **Max pressure / flow / reach**, and per-hour coverage (m²/h)?
4. Can we integrate **our own pressure/nozzle control** (PSM/IHM) or is the payload closed?
5. Warranty, support, spares, and lead time.

#### 1D. Open-platform (if going owned/vendor-neutral) — Freefly / PX4
Ref `docs/decisions/OPEN_PLATFORM_INTEGRATION.md`.
1. Freefly **Astro** price + **Smart Dovetail / Payload Bus** power+data specs for a cleaning payload.
2. Does **MAVSDK** expose the payload control (pump/nozzle setpoints) we need?
3. FAA waiver scope for any beyond-operator automation on this platform.

#### 1E. Photogrammetry / processing (the geometry engine)
Ref `docs/3D_DATA_PIPELINE.md` §2d.
1. **OpenDroneMap/NodeODM** self-host (free) vs **Metashape** (~$3.5K, Python SDK) — mesh quality on roofs?
2. Can we get the raw **mesh/point cloud export** (OBJ/LAZ/GeoTIFF) into our pipeline?
3. **Scanifly** (solar-specialized) — does its export feed a custom pipeline, or only racking partners?

#### 1F. Anthropic / cloud (the AI layer)
1. Commercial API **data terms** (no-training), **Zero-Data-Retention** eligibility, or **Bedrock/Vertex** tenant.
2. (Ref `docs/decisions/COMPUTE_INFRASTRUCTURE.md` — Claude runs cloud-side; data stays yours via terms.)

---

### Part 2 — The open-source & off-the-shelf stack (what to build on)

**Rule (from the pipeline doc): buy the commodity, build & keep-secret the intelligence.**

| Layer | Tool | License / cost | Role |
|---|---|---|---|
| **Photogrammetry** | **OpenDroneMap / NodeODM** | Open (AGPL) / free | scout images → mesh + point cloud + ortho (REST API) |
| ” (paid upgrade) | Agisoft **Metashape** | ~$3.5K perpetual | higher-quality meshes; Python SDK automation |
| **3D geometry** | **Open3D**, **trimesh**, **PDAL**, **laspy** | BSD/MIT | mesh raycasting, planes, point clouds |
| **Imagery/geo** | **OpenCV**, **rasterio**, **GDAL**, **Shapely**, **pyproj** | permissive | calibration, ortho/DSM, 2D geometry |
| **CV segmentation** | **Segment Anything (SAM/SAM2)** + **SegFormer/DeepLab** (HF) | Apache/MIT | region proposals + surface classifier backbone |
| **Backend** | **FastAPI**, **Uvicorn**, **Pydantic** | MIT | API + WebSocket telemetry + typed models |
| **Data** | **PostgreSQL + PostGIS**, **Redis** | open | properties/jobs/geometry + live queue |
| **Object storage** | **S3-compatible / MinIO** | open | orthomosaics, meshes, imagery |
| **Frontend** | **React + Vite** | MIT | the operator visor / dashboard |
| **AI agents** | **Anthropic API** (Claude) | usage-based | mapping/fusion/supervisor/cleaning/post-clean |
| **Open flight (optional)** | **PX4 / ArduPilot + MAVSDK** | BSD | vendor-neutral drone control (open platform) |
| **Local models (optional)** | **Ollama** + Llama/Qwen | open | offline/privacy tasks on the Mac Studio |

**Est. software cost to start: ~$0–3.5K** (mostly free/open) + cloud API usage. The money is in
hardware (drones) and, later, the PSM/IHM prototype — not the software stack.

---

### Part 3 — The 90-day path to first revenue (owner-operated)

**Weeks 1–3 — legal + platform**
- [ ] Form the LLC; get **FAA Part 107**; general-liability + drone/aviation insurance; CA business license.
- [ ] Buy the **scout** (DJI Matrice 4T ~$7.8K, or keep Autel) and start the **Sherpa subscription** ($2,950/mo, Path A) — see cost/payback models.
- [ ] Lock **IP basics**: NDAs + IP-assignment for anyone who touches it; talk to a patent attorney about the provisional (before any public demo). Ref `docs/IP_PROTECTION.md`.

**Weeks 3–6 — pipeline live**
- [ ] Stand up **OpenDroneMap/NodeODM** (self-host); process one real survey → mesh/ortho.
- [ ] Wire the real `SfmSource` reader; run the scan → plan → flight-path pipeline on real geometry (the code exists + is tested).

**Weeks 6–10 — first customers**
- [ ] Target Carlsbad **HOAs, solar owners, property managers**; lead with the **ROI report** (before/after, energy recovered).
- [ ] Run 3–5 paid jobs; capture thermal+RGB+outcome data (this is the moat — start the flywheel).

**Weeks 10–13 — prove & tune**
- [ ] Feed real outcomes back into the surface/pressure table (calibration).
- [ ] Generate ROI reports for every customer; ask for referrals + recurring contracts.
- [ ] Decide crew #2 vs. deepen tooling using the revenue/payback models.

**In parallel (low cost):** bench-prototype the **PSM** (~$800) so the hardware IP advances without airframe risk.

---

### Part 4 — What's ALREADY built in this repo (your asset base)

#### Working software (79 tests passing)
- **Drone-scan pipeline** — `propwash/backend/geometry/`, `fusion/`, `segmentation/`: scan →
  3D model → surface types + grime proxy + exclusion zones. Demo: `python -m sim.scan_demo`.
- **Scan → plan** — `planning/scan_to_plan.py`: classified zones → safety-gated work orders.
  Demo: `python -m sim.scan_to_plan_demo`.
- **Flight path (Stage 5)** — `planning/coverage_path.py`: standoff sweeps + keep-outs, solar-
  first ordering. Demo: `python -m sim.flight_plan_demo`.
- **Safety layer** — `safety/`: deterministic pressure ceilings + human-presence detection.
- **Execution transports** — `execution/`: Path A active; DJI/MAVLink/companion seams flagged off.
- **The visor** — `samples/propwash_visor_artifact.html` (hosted Artifact) + `frontend/`.

#### Business & strategy
- `docs/BUSINESS_PLAN.md`, `docs/SCALING_TO_10M.md` — the plan + path to $10M.
- Revenue/cost models — `propwash/backend/reports/`: `revenue_model.py`,
  `drone_platform_cost.py`, `platform_payback.py`, `roi_report.py`.
- `docs/IP_PROTECTION.md`, `docs/DYNAMIC_PRESSURE_HARDWARE.md` — the moat + hardware IP.

#### Decisions (in `docs/decisions/`)
Sensor platform · spectral sensing · compute infra · cleaning-drone platform · DJI two-drone
architecture · open-platform integration.

#### Vendor outreach
- `docs/LUCID_OUTREACH.md` — full Lucid question set + partnership framing.
- Part 1 above — DJI, retrofit, open-platform, processing, and cloud question sets.

---

**The honest one-liner:** most of what a "business plan chat" would hand you as bullet points
already exists here **as working code, tested models, and decision records** — this playbook is
the index + the practical next steps to turn it into a running company.

<a id="docsregulatorystrategy"></a>

---

# Regulatory Strategy — How to Get Maximum Autonomy, Legitimately

> **Source file:** `docs/REGULATORY_STRATEGY.md`

## Regulatory Strategy — How to Get Maximum Autonomy, Legitimately

> ⚠️ **Not legal advice.** Verify everything here with an aviation attorney before operating.
> Regulations change; Part 108 is proposed, not final.
>
> **Position:** PROPWASH does not evade or circumvent FAA regulation — that path ends in
> certificate revocation, uninsurability, and no commercial customer will contract with an
> operator carrying an FAA enforcement record. **We don't need to.** This document shows how
> much autonomy is *already legal*, and the real mechanisms to get more.

---

### 0. The finding that changes the picture

**Autonomous, pre-programmed flight is ALREADY LEGAL under Part 107. No waiver required.**

The FAA's own guidance (AC 107-2) explicitly contemplates it:

> *"An autonomous operation is generally considered an operation in which the remote pilot
> inputs a flight plan into the control station, which sends it to the autopilot onboard the
> small unmanned aircraft. During automated flight, flight control inputs are made by
> components onboard the aircraft, not from a control station."*

The condition is **not** manual flying. It's that the Remote Pilot in Command (RPIC):
- remains **the final authority** for the operation (107.19), and
- retains the ability to **change routing/altitude or command an immediate landing**.

**So "the operator stays in command" ≠ "the operator flies manually."** The operator can
absolutely upload a PROPWASH-generated flight path and let the aircraft fly it — as long as
they can intervene. That's the entire basis of your tech stack, and **it's legal today.**

Most competitors don't know this. **Regulatory sophistication is itself a moat.**

---

### 1. What's legal NOW vs. what needs a waiver

| Capability | Rule | Status |
|---|---|---|
| **Pre-programmed autonomous flight paths** | AC 107-2 / 107.19 | ✅ **Legal now** (RPIC must be able to intervene) |
| **Software-controlled payload** (pump/pressure/nozzle by position) | not restricted by 107 | ✅ **Legal now** |
| **Automated survey missions** | AC 107-2 | ✅ **Legal now** |
| Night operations | 107.29 | ✅ Legal with anti-collision lighting |
| **BVLOS** | **107.31** | ⚠️ **Waiver required** (→ Part 108) |
| **One RPIC, multiple aircraft** | **107.35** | ⚠️ **Waiver required** (→ Part 108 Flight Coordinator) |
| Over people | 107.39 | ⚠️ Waiver or Operational Category compliance |
| Above 400 ft AGL | 107.51 | ⚠️ Waiver (or within 400 ft of a structure — see §2) |

#### The two that actually bind PROPWASH
Everything core to your tech is already permitted. Only **two** constraints limit scaling:
1. **107.31 (VLOS)** — the operator must see the aircraft.
2. **107.35 (one aircraft per pilot)** — the linear labor↔revenue coupling in `SCALING_TO_10M.md`.

Both are **waiverable**, and both are what Part 108 is designed to replace.

---

### 2. The useful exemption most operators miss: 107.51(b)

**You may fly higher than 400 ft AGL if you stay within a 400-ft radius of a structure, and no
higher than 400 ft above that structure's uppermost limit.**

For a company that exclusively flies *around buildings*, this is significant — tall commercial
work is often achievable without an altitude waiver at all. Confirm applicability with counsel
for each site.

---

### 3. The legitimate ladder to more autonomy (in order)

#### Rung 1 — Exploit what's already permitted *(do this now, costs nothing)*
- Fly **pre-programmed missions** generated by `coverage_path.py`. Legal today.
- Run **software payload control** (PSM/IHM setpoints by position). Legal today.
- **Design for intervention**, because that's the actual legal requirement:
  - always-live **Abort/Override** (already in the operator app ✅)
  - immediate **land/hold** command
  - the **watchdog** cutting the pump on loss of control (built ✅)
- This alone delivers most of the value: consistent, prescription-accurate cleaning + verification.

#### Rung 2 — Waivers *(the real "surpass" mechanism)*
Apply through **FAA DroneZone**. Waivers are granted on **demonstrated safety mitigation** —
which is exactly what PROPWASH's architecture produces as a byproduct:
- deterministic Tier-1 safety layer + **hard pressure ceilings**
- **keep-out/geofence volumes** auto-generated from the scan
- **human-presence detection** halting dispatch
- **watchdog** failsafe with no auto-resume
- complete **execution-vs-prescription logs** (evidence of control)

> **Your safety engineering is your waiver application.** Most applicants write prose; you can
> submit an architecture with test coverage. That's a genuine competitive edge.

Target waivers, in priority order:
1. **107.35** (multiple aircraft per RPIC) → breaks the labor↔revenue coupling
2. **107.31** (BVLOS) → larger sites, campuses, solar farms
3. **107.39** (over people) → only if job types demand it

#### Rung 3 — Part 108 *(position now, don't wait)*
If finalized as proposed: BVLOS conducted **autonomously on pre-programmed flight paths**, with
a **Flight Coordinator supervising multiple aircraft** (Simplified User Interaction), and
accountability shifting to the **organization**. Preparation that pays off either way:
- keep flight paths **machine-readable and auditable** (already the shape of our output)
- build **organizational** safety documentation — SOPs, training records, maintenance logs
- keep **immutable safety-event logs** (compliance evidence *and* learning-model input)

#### Rung 4 — Shape the rules
Comment on NPRMs, join industry groups (AUVSI, Commercial Drone Alliance), and talk to your
FAA FSDO. Operators who engage get better outcomes than operators who hide.

---

### 4. Why compliance *is* the competitive strategy

| Path | Outcome |
|---|---|
| Evade the rules | Enforcement, certificate revocation, uninsurable, no commercial contracts — company over |
| Fly manual only | No moat; anyone with a drone competes |
| **Autonomy-within-the-rules + waivers** | Legal moat competitors lack, insurable, contractable, Part 108-ready ⭐ |

Commercial customers (property managers, REITs, solar operators) **require** proof of
compliance and insurance. Regulatory standing is a *sales asset*, not overhead. And waivers are
a **defensible advantage**: they take effort, evidence, and time — exactly the kind of barrier
a competitor can't shortcut.

---

### 5. Build/ops checklist (turn architecture into approvals)

- [x] Pre-programmed path generation (`coverage_path.py`)
- [x] Mission translation for open stacks (`mavlink_mission.py`)
- [x] Deterministic Tier-1 safety layer + hard ceilings
- [x] Human-presence detection halting dispatch
- [x] Watchdog: pump OFF on loss of positive control, no auto-resume
- [x] Always-live operator Abort/Override in the app
- [ ] Immediate **land/hold** command surfaced in the operator app
- [ ] Immutable safety-event + execution log (waiver evidence *and* learning input)
- [ ] Written SOPs, pilot training records, maintenance logs (Part 108 organizational posture)
- [ ] Part 107 certificate + registration + insurance
- [ ] Aviation attorney review; then file **107.35** waiver first

---

### 6. Open items
- [ ] Attorney: confirm AC 107-2 autonomous-flight posture for our exact concept of operations.
- [ ] Attorney: confirm 107.51(b) structure exemption applies to our typical job sites.
- [ ] Draft the 107.35 waiver using the safety architecture as the mitigation evidence.
- [ ] Track Part 108 final rule; re-run `SCALING_TO_10M.md` under a multi-aircraft coordinator.

### Sources
- [14 CFR Part 107 (eCFR)](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107) · [107.19 Remote pilot in command](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107/subpart-B/section-107.19) · [Part 107 Subpart B operating rules](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107/subpart-B)
- [FAA AC 107-2 — sUAS Advisory Circular](https://www.faa.gov/documentlibrary/media/advisory_circular/ac_107-2.pdf) (autonomous-operation guidance)
- [Rupprecht Law — 107.19 RPIC](https://jrupprechtlaw.com/section-107-19-remote-pilot-in-command/)

<a id="docswaiver10735"></a>

---

# FAA Waiver Package — 14 CFR 107.35 (Multiple sUAS, One RPIC)

> **Source file:** `docs/WAIVER_107_35.md`

## FAA Waiver Package — 14 CFR 107.35 (Multiple sUAS, One RPIC)

> **Draft working document — NOT a filed application.** Have an aviation attorney review and
> finalize before submitting via **[FAADroneZone](https://faadronezone.faa.gov/)**.
> `[Bracketed]` fields must be completed with real operational data.
>
> **Why this waiver first:** 107.35 is the single constraint that breaks the linear
> labor↔revenue coupling in `SCALING_TO_10M.md`. Every other core capability we need is
> already legal under Part 107 (`REGULATORY_STRATEGY.md` §0–1).

---

### 1. What 107.35 says and what we're asking

**The rule:** *"A person may not manipulate flight controls or act as a remote pilot in command
or visual observer in the operation of more than one unmanned aircraft at the same time."*

**Our request:** authorize **one RPIC to supervise up to [N] sUAS simultaneously** during
exterior-cleaning operations, supported by visual observers, where each aircraft flies a
**pre-programmed, pre-validated flight path** and the RPIC retains the ability to intervene on
any aircraft at any time.

**Note:** autonomous/pre-programmed flight itself already complies with Part 107 (FAA AC 107-2)
— this waiver addresses *only* the one-pilot-one-aircraft limitation.

---

### 2. Concept of operations (ConOps)

| Element | Description |
|---|---|
| Operation | Exterior cleaning of buildings/solar arrays at a fixed, surveyed site |
| Airspace | [Class G / controlled w/ LAANC auth]; [altitude], within 400 ft of the structure per **107.51(b)** |
| Aircraft | [N] × [make/model], each [weight] |
| Flight profile | Pre-programmed coverage paths generated from a site survey; low speed ([~0.2–0.35 m/s]), short standoff, confined to the property |
| Crew | 1 RPIC + [4] Visual Observers (VOs) + [1] ground crew |
| Site | Private property, access-controlled during operations |
| Duration | [X] hours per job |

**Risk-reducing characteristics inherent to this operation:** aircraft fly *slowly*, at *low
altitude*, in *close proximity to a structure*, on *fixed pre-validated paths*, over *private
property under our control* — a materially lower-risk profile than free-flight or BVLOS survey.

---

### 3. Safety mitigations (the core of the application)

> Each mitigation below is **implemented and tested in software** — not aspirational. Test
> counts refer to the automated suite (117 passing).

#### 3.1 Pre-validated flight paths
- Paths are generated from a 3D site survey, not improvised (`planning/coverage_path.py`).
- Every path is computed at a fixed standoff from the surface, at bounded speed.
- **Keep-out volumes** are auto-generated around obstacles (chimneys, HVAC, vents) and the path
  is checked against them before flight (`KeepOut`, verified 0 violations in test).
- Paths are reviewed on the ground before upload (`mavlink_transport.build_mission()` runs with
  hardware disconnected).

#### 3.2 Deterministic safety layer (cannot be overridden by software agents)
- Hard **pressure ceilings** per surface, enforced independently of any AI output.
- An unsafe parameter causes the work order to be **rejected, not adjusted** — no mission is
  emitted at all (`safety/checks.py`; test: over-pressure request is blocked).
- AI components are **advisory only** and sit outside the safety path (CLAUDE.md §2 tiering).

#### 3.3 Human-presence detection
- Thermal detection halts dispatch when a human signature is detected in a work zone
  (`safety/human_detection.py`), independent of operator attention.

#### 3.4 Loss-of-control watchdog
- Independent heartbeat monitoring of companion computer, C2 link, payload link, and telemetry.
- **Any** loss of positive control cuts the spray and commands a safe state.
- **Fail-closed:** a channel that has never reported is treated as failed.
- **Latching, no auto-resume:** a restored link does not resume operations; explicit human
  re-arm is required (`safety/watchdog.py`; 13 tests incl. every-channel coverage).

#### 3.5 Tamper-evident audit logging
- Hash-chained, append-only record of every safety decision and execution event
  (`safety/audit_log.py`; 12 tests covering alteration, deletion, reordering, and forgery).
- Produces a verifiable **compliance export** — the FAA or a customer can confirm no record was
  edited after the fact.

#### 3.6 Positive RPIC control of every aircraft
- RPIC ground station displays, per aircraft, **live position, altitude, attitude, groundspeed,
  and battery state**.
- RPIC can, for any individual aircraft at any time: **hold**, **change routing/altitude**,
  **command immediate landing**, and **cut the spray**.
- Always-available **Abort/Override** in the operator application.
- Aircraft are **visually separated** by assigned work zones so their paths cannot intersect.

---

### 4. Crew, roles, and training

#### Roles
| Role | Responsibility |
|---|---|
| **RPIC** | Final authority for all [N] aircraft; monitors telemetry; intervenes; sole authority to arm spraying |
| **Visual Observers ([4])** | Maintain VLOS on assigned aircraft; scan for intruding aircraft/persons; report to RPIC on continuous comms |
| **Ground crew** | Site security, chemical/water handling, no flight duties |

#### Communication
All crew on continuous two-way radio. Standard call-outs for: intruder aircraft, person entering
the site, aircraft anomaly, and **ABORT** (any crew member may call an abort).

#### Training (before any waiver operation)
Each RPIC and VO completes documented training covering:
1. Part 107 regulations
2. **The specific limitations and conditions of this waiver**
3. Proper visual scanning techniques
4. PROPWASH system operation, failsafes, and abort procedures
5. Emergency and lost-link procedures

Each completes a **written test ([20] questions)**; records retained and available to the FAA.

---

### 5. Emergency & contingency procedures

| Scenario | Response |
|---|---|
| Lost link (one aircraft) | Aircraft enters programmed failsafe (hold → RTL → land); spray cut automatically; RPIC announces; remaining aircraft continue or are held per RPIC judgment |
| Multiple aircraft anomaly | RPIC commands **all** aircraft to hold/land; operation suspended |
| Manned aircraft intrusion | VO calls out; RPIC immediately descends/lands all aircraft |
| Person enters operating area | Any crew member calls abort; spray cut; aircraft hold/land |
| Watchdog trip | Spray cut automatically; aircraft holds; requires human re-arm to resume |
| Adverse weather | Operations suspended below [minimums]; pre-flight weather check documented |

---

### 6. Proposed waiver conditions (we volunteer these)

Offering conditions strengthens an application:
1. Maximum **[N]** aircraft per RPIC.
2. Minimum **[4]** VOs; operations cease if VO staffing drops below minimum.
3. Operations only over **private property under operator control**, with public access excluded.
4. All aircraft on **pre-programmed paths** with pre-flight keep-out validation.
5. Aircraft assigned to **non-overlapping work zones**.
6. Daylight VLOS only [unless separately waived].
7. Documented crew training + testing retained and available on request.
8. Audit logs retained for **[24] months** and available to the FAA on request.

---

### 7. Application checklist

- [ ] FAADroneZone account created
- [ ] Part 107 certificate(s) current; aircraft registered
- [ ] Aircraft make/model/weight/performance documented
- [ ] Site(s) and airspace class identified; LAANC authorization if controlled
- [ ] ConOps finalized (§2) with real numbers
- [ ] Safety mitigations documented (§3) — attach architecture + test evidence
- [ ] Crew training curriculum + written test drafted (§4)
- [ ] Emergency procedures documented (§5)
- [ ] Insurance in place
- [ ] **Aviation attorney review**
- [ ] Submit; expect **[60–90+] days**; be responsive to FAA questions

---

### 8. Why this application should be strong

Most 107.35 applications are prose descriptions of intent. This one can attach:
- a **deterministic safety architecture** that structurally prevents unsafe operation,
- **117 automated tests** demonstrating those safeguards function,
- **tamper-evident logs** proving compliance in operation, and
- a **low-risk flight profile** (slow, low, fixed paths, private property).

That is a materially different quality of evidence — and it is the competitive moat: a
competitor cannot copy a waiver, and cannot quickly build the evidence to earn one.

---

### 9. Follow-on waivers (after 107.35)
1. **107.31 (BVLOS)** — larger campuses and solar farms; heaviest lift; Part 108 may supersede.
2. **107.39 (over people)** — only if job types require it.
3. Track **Part 108** — may replace this waiver path entirely with a standing framework
   (`COMMUNICATION_AND_AUTONOMY.md` §4).

### Sources
- [14 CFR 107.35 (Cornell)](https://www.law.cornell.edu/cfr/text/14/107.35) · [FAA — certificated remote pilots / waivers](https://www.faa.gov/uas/commercial_operators) · [FAADroneZone](https://faadronezone.faa.gov/)
- [Sample 107.35 waiver — Pilot Institute](https://pilotinstitute.com/multiple-drones-waiver/) · [Sample 107.35 application — Rupprecht Law](https://jrupprechtlaw.com/sample-107-35-waiver-application-swarming-drones/) · [FAA AC 107-2](https://www.faa.gov/documentlibrary/media/advisory_circular/ac_107-2.pdf)

<a id="docsipprotection"></a>

---

# PROPWASH — How to Protect Your IP (so it can't be copied)

> **Source file:** `docs/IP_PROTECTION.md`

## PROPWASH — How to Protect Your IP (so it can't be copied)

> ⚠️ **This is founder strategy, NOT legal advice.** Patents, trademarks, and trade-secret
> enforcement are jurisdiction- and fact-specific. **Engage a registered patent attorney and an IP
> attorney before filing or relying on any of this.** (CLAUDE.md §11.) This doc tells you *what to
> protect and how to think about it* so your conversation with counsel is fast and cheap.

---

### 0. The honest headline

**Nothing is 100% theft-proof.** Anyone telling you otherwise is selling something. What you *can*
build is **layered protection** where each layer covers a different attack, so copying you becomes
slow, expensive, legally risky, and — most importantly — **always one data-cycle behind.** That last
part is the real moat. Read §2 carefully.

---

### 1. The five kinds of IP and how each maps to PROPWASH

| IP type | Protects | Lasts | Your PROPWASH asset | Strength here |
|---|---|---|---|---|
| **Trade secret** | Secret, valuable info | Forever (while secret) | Grime/fusion scoring model, calibrated surface/pressure table, learning model, verification thresholds | ⭐⭐⭐⭐⭐ **Your #1** |
| **Utility patent** | A novel, non-obvious *method* | ~20 yrs | The closed loop: sense→fuse→prescribe→execute→verify→**re-queue with adjusted params** | ⭐⭐⭐⭐ |
| **Copyright** | Code & written expression | Life+ / 95 yrs | The codebase, ROI reports, docs | ⭐⭐⭐ (automatic) |
| **Trademark** | Brand identifiers | Forever (while used) | The name **PROPWASH**, logo | ⭐⭐⭐ |
| **Contracts** | Relationships/people | Per contract | IP assignment, NDAs, customer data rights | ⭐⭐⭐⭐ (the glue) |

---

### 2. The genius move: patent vs. trade secret (you can't do both for the same thing)

A patent **requires public disclosure** — you teach the world how it works in exchange for ~20 years
of exclusivity. A trade secret is the opposite: it's protected **only as long as it's secret.** So
the strategic question for *each* piece of IP is: **can a competitor figure this out by watching your
product work?**

- **If YES (observable / reverse-engineerable) → patent it.** A drone flying a sense→clean→re-scan→
  re-clean loop in a customer's backyard is *observable*. Someone will see the method. Patenting the
  **method** (especially "verification-driven parameter adjustment" — re-cleaning failed zones with
  automatically-adjusted pressure/chemistry) stakes your claim before a competitor can.
- **If NO (hidden inside your servers) → keep it a trade secret.** Your **grime-scoring model, the
  calibrated surface/pressure numbers, the learning weights, the verification thresholds** never leave
  your backend. Nobody can see them by watching a drone. Patenting them would just *teach competitors
  your secret sauce.* **Keep these as trade secrets — possibly forever.**

> **Rule of thumb:** Patent the *choreography*. Keep the *brain* secret.

This split is exactly what CLAUDE.md §11 already intends — this doc just makes the reasoning explicit.

---

### 3. The strongest moat isn't legal — it's the data flywheel

Patents and secrets are defense. The **data flywheel** is offense, and for an AI/ML business it's
usually more defensible than either:

```
more jobs → more thermal+RGB+outcome data → better-calibrated prescriptions
→ higher first-pass PASS rate → cheaper, better cleans → win more jobs → (repeat)
```

A competitor who copies your *method* still starts at **zero data**. Your surface/pressure table and
learning model are calibrated on every real job you've ever run (your trade secrets, §11). They can't
replicate that without running the same volume of jobs — which takes years. **Protect the data itself:**

- Lock the database (encryption at rest + in transit, least-privilege access, audit logging).
- In customer contracts, secure **your right to use job/sensor data** to improve your models.
- Treat the accumulated dataset as a crown-jewel trade secret: need-to-know access only.

---

### 4. Trade-secret protection — the checklist (this is where 80% of your moat lives)

Trade-secret law (e.g. the US Defend Trade Secrets Act + state UTSA) **only protects you if you took
reasonable steps to keep it secret.** Do these, and document that you did:

- [ ] **Mark it.** Label the model code, prescription tables, and thresholds `CONFIDENTIAL — PROPWASH TRADE SECRET`.
- [ ] **Access control.** Need-to-know only. Separate the secret model/data from the rest of the repo; restrict who can read it.
- [ ] **Encrypt** secrets at rest and in transit; no secrets in public repos, screenshots, or marketing.
- [ ] **NDAs** with every employee, contractor, advisor, investor (mutual), and vendor (incl. Lucid before deep talks).
- [ ] **IP assignment** in every employee/contractor agreement (see §7) — so what they build is *yours*.
- [ ] **Offboarding.** Revoke access immediately; exit interview reminding of continuing obligations.
- [ ] **Don't publish the secret sauce.** No patent, blog, talk, or pitch deck that reveals the scoring model, calibration numbers, or thresholds. (Reinforces CLAUDE.md §5/§11: also don't *overclaim* — honesty protects you legally too.)
- [ ] **Vendor/cloud hygiene.** Review that your cloud/API providers don't acquire rights to your data.

---

### 5. Patent strategy — concrete steps

1. **Document invention dates now.** Your git history + dated design notes establish when you invented
   what. Keep them.
2. **Don't publicly disclose before filing.** Public demos, sales pitches, or posts can start clocks or
   destroy novelty in some countries. **File before you broadly disclose.** (The US has a limited
   1-year grace period; many countries have *none* — so file first if you want international rights.)
3. **File a provisional** on the *method* (sense→fuse→prescribe→execute→verify→re-queue, with
   verification-driven parameter adjustment). Low cost, gives ~12 months + "patent pending," sets a
   priority date. **Verify current USPTO fees** and have an attorney draft/scope claims.
4. **Within 12 months**, convert to a full **utility** application once the method is field-proven.
5. **Consider international** (PCT) only if you'll operate/license abroad — it's expensive.
6. **Be honest in claims (§11).** Don't claim "multispectral detection" (you have thermal+RGB only, §5)
   or "fully autonomous" (operator in command, §7). Overclaiming can invalidate a patent and create
   liability. Honest, narrow, defensible claims beat broad fragile ones.

> A provisional is a **priority placeholder, not enforceable protection by itself.** It buys you time
> and a date. Real protection comes from the granted utility patent.

---

### 6. Copyright & trademark — cheap, do them

- **Copyright** is automatic the moment you write the code/reports. For stronger enforcement (and
  statutory damages in the US), **register** key works with the Copyright Office — inexpensive.
- Put a copyright notice + a `LICENSE` (keep the repo **private/proprietary** — no open-source license).
- **Trademark PROPWASH**: search first (USPTO TESS + common-law), then file in likely classes —
  **37** (cleaning/maintenance services) and **42** (software/SaaS), per §11. Use the ™ symbol now; ®
  only after registration. You trademark the **brand**, never "the idea."

---

### 7. Contracts — the glue that makes the rest enforceable

This is where founders lose IP without realizing it. Get these in place **before** anyone touches the code or data:

- **Employee/contractor IP assignment + invention assignment:** everything they create for PROPWASH
  belongs to PROPWASH. *Especially critical for any contractor/freelancer* — absent this, a contractor
  may *own* what they build for you.
- **Confidentiality / NDA** for everyone with access.
- **California note (important — you're in San Diego):** California generally **bans non-compete
  agreements** (Bus. & Prof. Code §16600). So **do not rely on non-competes.** Rely instead on
  trade-secret law, IP-assignment agreements, NDAs, and access control. This is a real constraint —
  confirm with counsel.
- **Customer contracts:** secure your right to capture and use job/sensor data for model improvement;
  clarify data ownership.
- **Founder IP assignment:** if PROPWASH is/becomes a company, **assign your own pre-formation IP to
  the entity** so the company (not you personally) owns it — investors will require this anyway.

---

### 8. Operational security (don't get robbed the dumb way)

- Private repos; 2FA everywhere; least-privilege cloud roles; secrets in a vault, never in code.
- Separate the trade-secret model/data behind tighter access than the rest of the codebase.
- Be careful what goes in pitch decks, demos, and conference talks — assume anything shown publicly is public.
- Background-check key technical hires; stagger access to crown-jewel data.

---

### 9. What to do THIS QUARTER (priority order)

1. **IP assignment + NDA** for yourself and anyone who has touched this (cheap, urgent, prevents the worst losses).
2. **Lock down trade secrets** (§4 checklist) — especially separating the scoring model/calibration data.
3. **Talk to a patent attorney** about a provisional on the method **before** any public demo/pitch.
4. **Trademark search** on PROPWASH; file classes 37 + 42.
5. **Register copyright** on the core codebase.
6. **Secure data rights** language in your first customer contracts.

---

### 10. The mental model to remember

- **Patent** the loop a competitor can *see*.
- **Keep secret** the brain a competitor *can't* see.
- **Out-run** everyone with the **data flywheel** they can't replicate without your job history.
- **Contract** every human so the IP is unambiguously yours.
- **Stay honest** in every claim — overclaiming is itself a legal risk (§5, §7, §11).

Layered like this, copying PROPWASH means: reinventing the method (you patented it), guessing the
models (you kept them secret), AND collecting years of field data from scratch (your flywheel) —
all while you keep pulling further ahead. That's as close to "can't be stolen" as a real business gets.

<a id="docsvendoroutreach"></a>

---

# Vendor Outreach — draft letters

> **Source file:** `docs/VENDOR_OUTREACH.md`

## Vendor Outreach — draft letters

> Send the **Integration Qualification Questionnaire** (`LAUNCH_PLAYBOOK.md` §1.0) to every
> manufacturer. These are the cover letters, tuned per vendor.
>
> **Rules for all outreach (CLAUDE.md §5, §7, §10):**
> - Be **transparent** — we integrate *with* vendors and *within* FAA Part 107. Never imply
>   covert automation or a plan to circumvent regulation.
> - **Don't overclaim** — no "fully autonomous," no "multispectral/mold detection." We say
>   thermal + RGB proxy, operator in command.
> - Ask for answers **in writing**. A verbal "we support integration" isn't an answer to Q8.
> - Replace `[bracketed]` fields before sending. Keep it short — busy people skim.

---

### 1. Lucid Bots — *partnership-first* (they're closed; we want them to open)

**Subject:** Integration partnership — AI verification layer for Sherpa operators

> Hi [Name],
>
> I'm [Kevin Weinstein], founder of [COMPANY] in Carlsbad, CA. We've built an AI orchestration
> and **verification** layer for exterior cleaning: we survey a property with a sensing drone,
> build a 3D thermal model, classify every surface (solar, glass, tile, stucco, gutter), and
> generate a per-zone cleaning prescription — then re-scan after the clean to produce a
> measured before/after result for the customer.
>
> We're planning to operate Sherpas ourselves, and our goal is to make each one more valuable:
> better-targeted jobs, documented outcomes, and an ROI report the building owner can act on.
> In short, we'd like to **drive more Sherpa utilization**, not compete with your autonomy work.
>
> Could we get 30 minutes with someone on the Refresh / partnerships side? I'd like to
> understand your integration surface. Specifically:
>
> 1. Does Lucid Refresh expose an API (REST/GraphQL/webhooks)?
> 2. Can we **read** job data programmatically — status, telemetry, completion, location?
> 3. Can we **push** structured work orders / job packets for an operator to execute?
> 4. Is the interface available to customers, or only to internal engineering partners?
> 5. Who owns the job and telemetry data generated on a customer's Sherpa?
> 6. Is there a developer, OEM, or reseller partnership program?
> 7. Longer term: any supported path for software-set pump/pressure parameters — under a
>    partnership, with the operator in command and the appropriate FAA pathway?
>
> Happy to sign an NDA and demo what we've built.
>
> Thanks,
> [Kevin] · [email] · [phone]

**Note:** Q7 is deliberately last and framed as *partnership + operator-in-command + FAA
pathway*. Never frame it as wanting to bypass their system.

---

### 2. DJI Enterprise — *developer program*

**Subject:** Payload SDK / Cloud API access — commercial exterior-cleaning application

> Hi [Name],
>
> I'm [Kevin], founder of [COMPANY] (Carlsbad, CA). We're building an AI system for commercial
> exterior cleaning: a survey drone maps a building in thermal + RGB, our software produces a
> per-surface condition model and cleaning plan, and we verify results with a post-clean re-scan.
>
> We're evaluating DJI for **both** roles — a Matrice 4T as the survey aircraft, and an
> M350/M400 with a third-party cleaning payload for execution. Before we commit, I'd like to
> confirm the developer surface:
>
> 1. Does Cloud API support programmatic ingest of imagery and real-time telemetry
>    (position, IMU, obstacle sensors, laser rangefinder)?
> 2. Can an external application upload **custom 3D flight paths / waypoint missions**?
> 3. Via Payload SDK, can our software control a third-party spray pump/nozzle — including
>    setpoints tied to position along a planned route?
> 4. Can we run an onboard companion computer (e.g., NVIDIA Jetson)? Supported mounting/power?
> 5. Do you support MAVLink or ROS 2 interoperability, or is integration PSDK-only?
> 6. Is PSDK/Cloud API access open to customers, or gated to partners? What's the approval path?
> 7. Does a third-party payload or custom software affect warranty or airworthiness?
> 8. Is there a developer/OEM partner program we should apply to?
>
> What's the right path to get these answered — a developer account, or a call with your
> enterprise/solutions team?
>
> Thanks,
> [Kevin] · [email] · [phone]

---

### 3. Foxtech / drone-payload (cleaning payloads) — *specs + price*

**Subject:** Quote + integration specs — AeroClean payload for M350/M400

> Hi [Name],
>
> I'm [Kevin] with [COMPANY] (Carlsbad, CA). We're speccing a drone-based exterior cleaning
> system for commercial buildings and solar arrays, and your [AeroClean P3 (T50) / T-M400C /
> RT-AP3] looks like a strong fit.
>
> Could you send pricing and lead time, plus answers to a few technical questions? Our software
> generates per-surface cleaning plans, so **programmatic control of the payload** is the
> deciding factor for us:
>
> 1. **Price and lead time**, and which airframes are supported (M350 RTK / M400)?
> 2. Pressure range, flow rate, hose length, max working height, coverage rate?
> 3. Is there a **control interface** (serial/CAN/MAVLink/PSDK) for our software to set
>    pressure or pump state — including varying it during a flight?
> 4. Can we read back **actual** pressure/flow telemetry?
> 5. Could we integrate our own electronic pressure regulator / nozzle module into the
>    payload's water path? Any spec or support for that?
> 6. Tethered vs. onboard-tank configurations available?
> 7. Warranty terms, and whether third-party integration affects them?
> 8. Do you support integrators/OEM customers, and is there documentation we can review?
>
> Thanks,
> [Kevin] · [email] · [phone]

---

### 4. Freefly Systems — *open platform / US-made*

**Subject:** Astro + Smart Dovetail — custom cleaning payload integration

> Hi [Name],
>
> I'm [Kevin], founder of [COMPANY] (Carlsbad, CA). We build AI software for commercial
> exterior cleaning — 3D surface mapping, per-surface cleaning plans, and post-clean
> verification. We're evaluating platforms where our software can be a first-class integration,
> and Astro's open approach (Smart Dovetail, Pixhawk Payload Bus, MAVSDK) is exactly the
> architecture we want. US-made is a plus for us.
>
> Questions:
>
> 1. Astro pricing/availability, and payload capacity for a liquid-delivery payload?
> 2. Smart Dovetail / Payload Bus specs — power, data, mounting envelope?
> 3. Via MAVSDK, can we command a custom payload (pump/valve setpoints) and read telemetry?
> 4. Can an external app upload **custom 3D flight paths / waypoint missions**?
> 5. Can we run an onboard companion computer (Jetson-class)? Supported power/data?
> 6. ROS 2 support or reference integrations?
> 7. Does a custom payload affect warranty or certification?
> 8. Is there a developer/OEM partner program, and can we get SDK docs to review?
>
> Would love 30 minutes with your solutions team.
>
> Thanks,
> [Kevin] · [email] · [phone]

---

### 5. Short universal version (for any vendor / web contact form)

> Hi — I'm [Kevin] with [COMPANY] in Carlsbad, CA. We build AI software for commercial exterior
> cleaning (3D surface mapping → per-surface cleaning plans → verified results) and we're
> selecting hardware platforms. Integration capability matters more to us than raw pressure, so
> before we buy, could you answer these in writing?
>
> 1. Do you provide a public SDK or API?
> 2. Can an external application upload custom 3D flight paths or waypoint missions?
> 3. Can we command velocity, heading, altitude, and standoff distance programmatically?
> 4. Is there real-time telemetry — position, IMU, obstacle sensors, range data?
> 5. Can we run an onboard NVIDIA Jetson or companion computer?
> 6. Can our software control the spray pump/nozzle based on location?
> 7. Do you support ROS 2, MAVLink, PX4, or Auterion APIs?
> 8. Is the interface available to customers, or only internal/engineering partners?
> 9. Will custom software void the warranty or certification?
> 10. Is there a supported developer or OEM partnership program?
>
> Happy to sign an NDA. Thanks — [Kevin], [email], [phone]

---

### Tracking

Log every reply in `docs/decisions/CLEANING_DRONE_PLATFORM.md` and score each vendor
**Open / Semi-open / Closed** per the rubric in `LAUNCH_PLAYBOOK.md` §1.0.

| Vendor | Sent | Replied | Score | Notes |
|---|---|---|---|---|
| Lucid Bots | | | | |
| DJI Enterprise | | | | |
| Foxtech | | | | |
| drone-payload | | | | |
| Freefly | | | | |
| Skydio | | | | |

<a id="docslucidoutreach"></a>

---

# Lucid Bots — partnership outreach & questions

> **Source file:** `docs/LUCID_OUTREACH.md`

## Lucid Bots — partnership outreach & questions

> Purpose: resolve the single biggest strategic unknown in PROPWASH (CLAUDE.md §7, §15.1).
> Posture: **transparent partnership**, not circumvention. We integrate *with* Lucid and *within*
> FAA Part 107. Prefer a vendor-friendly relationship over clever workarounds.

### Who to contact
- Lucid Bots — partnerships / developer relations / Lucid Refresh product team.
- Goal of first contact: a 30-minute intro call to understand the integration surface.

### The framing (lead with value to them)
> "We've built an AI orchestration + verification layer for exterior cleaning that produces
> measured before/after results. We want our customers to buy and run more Sherpas, and we want to
> integrate transparently with Lucid Refresh. We're exploring whether we can read job data — and
> ideally hand structured work orders to operators — through your platform."

Position PROPWASH as **demand generation for Sherpas**, not a threat to their autonomy stack.

### Questions to ask (in priority order)

#### A. Lucid Refresh API (Path A — what we build first)
1. Does Lucid Refresh expose an API? REST/GraphQL/webhooks?
2. Can we **read** job data programmatically (status, telemetry, completion, location)?
3. Can we **push** structured work orders / job packets into Refresh for an operator to execute?
4. What auth model (API keys, OAuth, per-fleet tokens)? Rate limits? Sandbox?
5. Data ownership — who owns the job/telemetry data generated on a customer's Sherpa?

#### B. Control surface (Path B — best case, unverified)
6. Is there any supported way to send pump/pressure/dwell setpoints to the Sherpa?
7. Any MAVLink or documented control endpoint, even partner-gated?
8. If not today — is it on the roadmap? Under what partnership terms?

#### C. Companion / retrofit (Path C — last resort, constrained)
9. What is Lucid's policy on companion computers or third-party hardware on owned Sherpas?
10. Warranty implications? Required reviews?
11. Would Lucid co-develop a sanctioned operator-assist capability (with the appropriate FAA pathway)?

#### D. Commercial / partnership
12. Is there a partner/reseller program? Referral economics?
13. Would Lucid co-sell to operators who want our intelligence layer on their fleet?
14. Any exclusivity or restrictions we should know before we build on Refresh?

### What we will NOT ask for / build
- Anything that conceals autonomous operation from Lucid or the FAA.
- Anything that circumvents Part 107 or keeps the operator out of genuine command (§7, §10).

### Decision gate (after the call)
- **API to read + push work orders** → double down on Path A; it's a real integration.
- **Read-only** → Path A with manual work-order handoff; revisit B later.
- **Open to control partnership** → scope Path B behind a feature flag + capability check.
- **No partnership appetite** → reassess: license our platform to their operator base *with* their
  blessing, or treat Lucid as one swappable transport among several drone vendors.

<a id="surfacetable"></a>

---

# Surface treatment table

> **Source file:** `prescriptions/surface_treatment_v1.json`
>
> Versioned data, not code (CLAUDE.md §9). These are **starting assumptions to calibrate**, not validated constants.

```json
{
  "_meta": {
    "version": "1.0.0",
    "status": "UNVALIDATED_DEFAULTS",
    "note": "Starting assumptions only \u2014 calibrate from real field jobs. Never hard-code these in logic. See CLAUDE.md \u00a79.",
    "last_updated": "2026-06-22",
    "open_calibration_items": [
      {
        "id": "roof-dwell-2026-08",
        "severity": "HIGH",
        "surfaces": [
          "composite_shingle",
          "clay_tile",
          "concrete_tile"
        ],
        "finding": "Roof dwell is 30-40 s. Industry soft-wash practice for biological growth (moss/algae/lichen) is a 15-20 MINUTE dwell. Ours is roughly 26-34x too short to kill growth at the root.",
        "impact_on_schedule": "None material. Modelled at 900 s: total job dwell rises 8.9 -> 66.5 min, but makespan stays 115 min on one aircraft because 66 min hides behind work on other zones. The phase scheduler absorbs it.",
        "impact_on_result": "Material. A 35 s dwell rinses; it does not kill. Zones would pass visually and regrow.",
        "coupled_decision": "Industry roof chemistry is sodium-hypochlorite based. Our table specifies eco_degreaser. Dwell and chemistry must be calibrated together - KEVIN'S CALL, since SH is harsh on landscaping and 'eco' is a positioning choice.",
        "status": "OPEN - do not change dwell without deciding chemistry"
      },
      {
        "id": "pressure-ceiling-is-correct-2026-08",
        "severity": "INFO",
        "finding": "Verified against ARMA guidance: asphalt shingles must NEVER be pressure washed - granule loss and premature failure. Correct method is soft wash at 40-80 psi. Our composite_shingle default of 5.5 bar = 80 psi sits at the top of that band and is CORRECT. The ~7 bar system ceiling is a deliberate design point, not a limitation.",
        "status": "CONFIRMED"
      },
      {
        "id": "high-pressure-belongs-on-the-ground-2026-08",
        "severity": "INFO",
        "finding": "Surfaces that genuinely need 100-200 bar are horizontal hardscape - concrete, driveways, parking decks. That is the ground-robot domain, not the aerial one. The aerial system is soft-wash by design across every surface it touches.",
        "status": "CONFIRMED"
      }
    ]
  },
  "surfaces": {
    "composite_shingle": {
      "pressure_bar_min": 5.0,
      "pressure_bar_max": 6.5,
      "pressure_bar_default": 5.5,
      "pressure_bar_hard_ceiling": 7.0,
      "chemical": "eco_degreaser",
      "chemical_mix_ratio_default": 0.35,
      "dwell_seconds_min": 30,
      "dwell_seconds_max": 40,
      "dwell_seconds_default": 35,
      "nozzle_angle_deg": 40,
      "nozzle_orifice_mm": 0.5,
      "nozzle_pattern": "fan",
      "standoff_m_default": 1.2
    },
    "clay_tile": {
      "pressure_bar_min": 4.5,
      "pressure_bar_max": 6.0,
      "pressure_bar_default": 5.0,
      "pressure_bar_hard_ceiling": 6.5,
      "chemical": "standard_degreaser",
      "chemical_mix_ratio_default": 0.3,
      "dwell_seconds_min": 30,
      "dwell_seconds_max": 40,
      "dwell_seconds_default": 35,
      "nozzle_angle_deg": 40,
      "nozzle_orifice_mm": 0.5,
      "nozzle_pattern": "fan",
      "standoff_m_default": 1.2
    },
    "concrete_tile": {
      "pressure_bar_min": 4.5,
      "pressure_bar_max": 6.0,
      "pressure_bar_default": 5.0,
      "pressure_bar_hard_ceiling": 6.5,
      "chemical": "standard_degreaser",
      "chemical_mix_ratio_default": 0.3,
      "dwell_seconds_min": 30,
      "dwell_seconds_max": 40,
      "dwell_seconds_default": 35,
      "nozzle_angle_deg": 40,
      "nozzle_orifice_mm": 0.5,
      "nozzle_pattern": "fan",
      "standoff_m_default": 1.2
    },
    "solar_panel": {
      "pressure_bar_min": 1.5,
      "pressure_bar_max": 2.0,
      "pressure_bar_default": 1.8,
      "pressure_bar_hard_ceiling": 2.0,
      "chemical": "di_water_only",
      "chemical_mix_ratio_default": 0.0,
      "dwell_seconds_min": 18,
      "dwell_seconds_max": 22,
      "dwell_seconds_default": 20,
      "nozzle_angle_deg": 25,
      "nozzle_orifice_mm": 0.35,
      "nozzle_pattern": "narrow_fan",
      "standoff_m_default": 0.8,
      "_safety_note": "HARD CEILING enforced in safety layer \u2014 detergent residue cuts panel output; high pressure cracks cells. DI water ONLY."
    },
    "window_glass": {
      "pressure_bar_min": 2.0,
      "pressure_bar_max": 2.4,
      "pressure_bar_default": 2.2,
      "pressure_bar_hard_ceiling": 2.5,
      "chemical": "ammonia_free",
      "chemical_mix_ratio_default": 0.2,
      "dwell_seconds_min": 15,
      "dwell_seconds_max": 20,
      "dwell_seconds_default": 17,
      "nozzle_angle_deg": 20,
      "nozzle_orifice_mm": 0.35,
      "nozzle_pattern": "jet",
      "standoff_m_default": 0.6
    },
    "stucco": {
      "pressure_bar_min": 3.5,
      "pressure_bar_max": 4.5,
      "pressure_bar_default": 4.0,
      "pressure_bar_hard_ceiling": 5.0,
      "chemical": "standard_degreaser",
      "chemical_mix_ratio_default": 0.3,
      "dwell_seconds_min": 25,
      "dwell_seconds_max": 35,
      "dwell_seconds_default": 30,
      "nozzle_angle_deg": 40,
      "nozzle_orifice_mm": 0.6,
      "nozzle_pattern": "fan",
      "standoff_m_default": 1.0
    },
    "gutter_aluminum": {
      "pressure_bar_min": 6.0,
      "pressure_bar_max": 7.0,
      "pressure_bar_default": 6.5,
      "pressure_bar_hard_ceiling": 7.5,
      "chemical": "degreaser_solvent_blend",
      "chemical_mix_ratio_default": 0.4,
      "dwell_seconds_min": 35,
      "dwell_seconds_max": 45,
      "dwell_seconds_default": 40,
      "nozzle_angle_deg": 45,
      "nozzle_orifice_mm": 0.7,
      "nozzle_pattern": "fan",
      "standoff_m_default": 0.5
    }
  }
}
```
