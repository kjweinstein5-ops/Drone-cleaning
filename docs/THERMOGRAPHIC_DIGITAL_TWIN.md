# PROPWASH — Thermographic Digital Twin + Human Presence Detection

> ⚠️ **Not legal advice.** Engage counsel for patent filings, FAA regulatory review,
> and any claims about safety-critical detection systems before shipping.

---

## 0. What this is

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

## 1. Why the 3D model matters more than a flat thermal image

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

## 2. How to build it (the pipeline)

### Step 1 — Survey flight (existing: Autel EVO II 640T)

The Autel flies a grid or orbit pattern. It already captures:
- **RGB frames** at high resolution
- **Radiometric thermal frames** (640×512, with per-pixel temperature values)

No new hardware needed for the 3D model. The Autel's dual camera provides exactly what
photogrammetry requires.

### Step 2 — Structure from Motion (SfM) → 3D mesh

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

### Step 3 — Thermal registration onto the mesh

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

### Step 4 — Zone segmentation on the mesh

The Mapping Agent already segments zones. On the 3D model, zones become **mesh
sub-regions** (groups of faces) rather than flat polygons. Each zone inherits:
- Surface type (from RGB classification)
- Mean grime proxy score (from thermal overlay)
- Pitch angle (from face normals — directly from the mesh, no inference)
- True area in m² (from face areas — more accurate than 2D projections)

This fixes the pitch-angle estimation that currently relies on SfM inference in the
Fusion pipeline.

---

## 3. Human presence detection

### What it detects

A human body at rest or in motion has a core skin temperature of **32–36°C** and a
distinctive **compact thermal blob signature** — roughly 0.4 × 1.8 m when viewed from
above, warmer than most roof surfaces in the morning, cooler than sun-heated dark
surfaces in the afternoon.

The detection task: before any cleaning pass executes, scan the target zone's thermal
mesh for any blob whose:
- Mean temperature is in the range [30°C, 40°C]
- Bounding box aspect ratio matches a human figure (tall and narrow, or compact if prone)
- Area is in the range [0.1 m², 1.5 m²] (filters out HVAC vents and small birds)

### Where this lives in the architecture

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

### Why thermal rather than RGB

| Detection method | Problem |
|---|---|
| RGB only | People in dark clothing on dark roofs are invisible; shadows mask figures |
| Thermal only | Can't distinguish a human from an HVAC unit at 35°C |
| **Thermal + shape filter (what we build)** | Temperature range + blob geometry together are highly reliable |

The Autel's dual camera gives you both channels simultaneously. The shape filter runs
on the thermal channel; the RGB channel provides a second confirmation (is there a
person-shaped object at the location flagged by thermal?). This dual-channel approach
is patentable — see §5.

### Edge cases to handle

| Scenario | Handling |
|---|---|
| HVAC exhaust vents (35–45°C, compact) | Shape filter — vents are round, not elongated |
| Birds (small, 38–41°C) | Area filter — birds are < 0.05 m² from drone altitude |
| People in direct sun on a hot roof (surface temp 55°C+) | The person is *cooler* than the surface — detect as a cool blob, not a warm one |
| Shadow zones (anomalously cold in thermal) | Flagged as UNCERTAIN, not CLEAR — requires manual operator review |

---

## 4. Roof vs. structural features (the other classification)

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

## 5. IP angles

### 5a. The core patentable system

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

### 5b. Dependent claims worth adding

- The dual-channel confirmation (thermal blob + RGB shape co-registration)
- The per-face thermal averaging across multiple flight passes (reduces noise, improves
  prescription accuracy over repeat customers)
- The "cool blob on hot surface" human detection mode (afternoon sun scenario)
- Storing the thermographic digital twin as a persistent customer asset and using
  delta-comparison between visits to detect new soiling (predictive scheduling)

### 5c. Trade secrets (do not put in patent claims)

- The specific temperature range thresholds used for human detection ([30, 40°C] above
  is an example — your field-tuned values are the secret)
- The blob shape filter parameters tuned for drone altitude and camera FOV
- The grime proxy calibration coefficients per surface type
- The multi-visit delta model that predicts when a zone will fail next (scheduling IP)

---

## 6. The persistent customer asset: the living digital twin

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

## 7. Architecture changes

### New modules

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

### Data flow change

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

### New Pydantic model (sketch)

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

## 8. Build roadmap

### Phase 1 — Flat-to-3D upgrade (no new hardware)
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

### Phase 2 — Human presence detection
1. Build `human_detection.py` with temperature-range blob detector; write unit tests
   covering the HVAC / bird / afternoon-sun edge cases.
2. Wire into `SafetyChecker` as a pre-dispatch check.
3. Add a `HUMAN_DETECTED` alert to the operator app — zone card shows a red banner
   with the thermal frame annotated with the detected blob location.
4. Log every human detection event to the audit table (liability protection).

**Milestone:** No cleaning pass can execute without a thermal human-clear check.

### Phase 3 — Living twin + predictive scheduling
1. On each return visit, run a delta comparison between the new thermal scan and the
   stored baseline model.
2. Build the soiling rate model: fit a curve to the delta-per-zone over multiple visits.
3. Surface scheduling recommendations in the operator dashboard: "Zone SOL-ROOF
   predicted to exceed threshold in ~42 days — schedule next clean."
4. Add the persistent twin archive as a customer-facing report deliverable — the
   property owner can see their building's soiling history.

**Milestone:** PROPWASH can offer predictive maintenance contracts backed by real data.

---

## 9. What to do this quarter

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

## 10. Mental model

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
