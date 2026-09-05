# PROPWASH — the essentials

> Generated 2026-09-05. The six documents that carry the argument, for pasting where the full bundle is too long.
>
> Full version: `PROPWASH_COMPLETE.md` (35 documents).


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
