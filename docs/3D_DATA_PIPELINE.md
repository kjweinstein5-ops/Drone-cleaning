# PROPWASH — 3D Data Pipeline Deep Dive

## From raw drone capture → surface model → asset segmentation → cleaning flight path

> ⚠️ **Engineering strategy, not legal advice.** Where this touches FAA flight
> automation, see §9 and CLAUDE.md §7/§10 — the cleaning drone stays operator-piloted.
> The flight path this system produces is a **guidance overlay for the operator**, not
> an autonomous command stream, until Lucid + FAA pathways say otherwise.

---

## 0. The honest starting point (read this before anything else)

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

## 0b. ⚠️ Laser Rangefinder ≠ LiDAR (a specific trap — read this)

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

### What this means for us

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

### Honesty rule (CLAUDE.md §5) — same trap as multispectral

Do **not** write "LiDAR" in any spec, patent claim, pitch deck, or marketing copy while
the sensor is a **rangefinder**. It is the exact same overclaim risk as calling the
thermal+RGB grime score "multispectral biofilm detection." A laser rangefinder is a
distance sensor, not a mapping sensor. If we want to *say* LiDAR, we have to *fly* LiDAR
(§8). Until then: "photogrammetry, optionally laser-rangefinder-assisted for scale."

---

## 1. The pipeline in one picture

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

## 2. Stage 1 — Photogrammetry (BUY, don't build)

**Do not write our own SfM engine.** Structure-from-Motion + Multi-View Stereo is a
mature, 20-year-deep research field (bundle adjustment, feature matching, dense depth).
Building it would burn a year and never beat the incumbents. This is pure commodity
infrastructure — buy or use open source.

### The realistic options

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

### What we DON'T buy from them

The SfM tool gives us geometry. It knows *nothing* about cleaning — no surface types, no
grime, no pressure. **Everything from Stage 2 onward is ours.** That's the boundary:
buy the geometry, build the intelligence.

---

## 2b. ⚡ Speed & the "seamless, fast" engine choice (READ if turnaround matters)

The §2 default (OpenDroneMap) is **free but slow** — it's the most CPU-bound option. If the
priority is a **fast, seamless survey→model turnaround** (survey in the morning, clean plan
by afternoon — or eventually near-real-time), the engine choice changes, and it collides
with the Mac Studio decision (`COMPUTE_INFRASTRUCTURE.md`). Here's the honest picture.

### The hard tension: the fastest engines are NVIDIA/Windows, the Mac Studio is not

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

### The decision, tied to the Mac Studio

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

### Gaussian Splatting / NeRF — a visual layer, NOT the measurement engine
Neural reconstruction (3D Gaussian Splatting) trains in **minutes** and looks
photorealistic — tempting for speed. **But its geometric error is ~7.8 cm vs 1–3 cm for
photogrammetry.** That's too loose for standoff distance, area, and prescription math, and
it needs an NVIDIA RTX 4090. **Verdict:** optionally use GS later as a gorgeous
*customer-facing* twin visualization, but **not** as the measurement/geometry source that
feeds Stages 3–5. Measurement stays photogrammetry.

### Where "seamless" actually comes from (this part is ours to build)
No off-the-shelf tool chains capture → reconstruction → thermal overlay → surface
segmentation → cleaning plan into **one automated job.** That orchestration glue — kick the
engine via its CLI/API, auto-ingest the mesh, run our Stage 2–3, emit the twin, no manual
handoffs — **is our code, and it's where the "seamless, fast pipeline" is won or lost.** The
engine is bought; the *seamlessness* is built. See `propwash/backend/geometry/` +
`fusion/` in §11.

---

## 2c. Scanifly as a solar-specialized starting point (worth doing — with eyes open)

**Yes, Scanifly is a reasonable way to START Stage 1** — arguably better-aligned to your
solar wedge than the generic engines, as long as you understand exactly what it does and
does NOT do. Here's the honest split.

### What Scanifly gives you (the geometry canvas) ✅
- **Proprietary photogrammetry + AI → a to-scale 3D model within inches**, from geo-tagged
  drone photos. This is precisely the Stage-1 reconstruction we said to *buy, not build*.
- **Works with any drone that shoots geo-tagged images** — your Autel included, no lock-in.
- **Solar-specialized**: roof planes, pitch/azimuth, obstructions, and the only drone-based
  **shade analysis approved by US regulators/lenders**. That pedigree matches your market.
- **Export + API**: 3D models export to CAD; API integrations push data to solar partners
  (Unirac, IronRidge, Pegasus). So data *can* come out — but see the caveat below.

### What Scanifly does NOT do — this stays PROPWASH's proprietary layer ❌
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

### The two real caveats before committing
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

### Verdict (revised — see §2d)
Scanifly is solar-specialized and accurate, but its export is built to feed *racking
vendors*, not a custom pipeline — which makes it a **worse fit than OpenDroneMap/Metashape
for the "build geometry → layer our data → pipe it" goal you actually have.** Keep it as a
possible fast trial, but §2d is the real recommendation for a pipeline front-end.

---

## 2d. ⭐ The right front-end for "scout collects → engine builds → pipeline runs"

Your actual requirement isn't "a solar design tool" — it's an engine that **automatically
turns scout-drone imagery into clean, exportable geometry your own pipeline consumes.** That
selection filter has a clear winner.

### The requirement, stated plainly
```
Scout drone flies → geotagged RGB (+ thermal) images
        → [ENGINE builds the 3D geometry, automatically]
        → standard mesh/point-cloud/ortho export
        → OUR pipeline layers dirt/mold/material/cleaning data on top (Stages 2–5)
```
The engine must: (a) reconstruct accurately, (b) run **hands-off via an API/CLI**, and
(c) export **open, standard formats** (OBJ/PLY mesh, LAS/LAZ cloud, GeoTIFF ortho/DSM) —
not lock the geometry inside a design app.

### Best fit: **OpenDroneMap via NodeODM (self-hosted REST API)**
- **Purpose-built for exactly this loop**: "drone lands → images upload → processing starts
  → outputs push." NodeODM is a REST API you script; PyODM is the Python client. This is the
  automated ingest→build→export pipeline you described, out of the box.
- **Standard open exports** — `odm_texturing/*.obj`, `*.laz` point cloud, `odm_orthophoto/
  *.tif`, `odm_dem/dsm.tif` — which our Stage 2 (`thermal_registration`) already expects.
- **Self-hosted → data-sovereignty moat intact** (§7). Imagery never leaves your box.
- **Free** (AGPL — fine for internal processing; §2 caveat only if you resell processing).

### Premium alternative: **Agisoft Metashape (Python SDK)**
- **Full batch automation via a Python API/SDK** — scriptable end to end, higher-quality
  meshes than ODM, native Apple-Silicon GPU (§2b), standard exports. ~$3.5K perpetual, no
  copyleft. Buy this if ODM's mesh quality isn't good enough on complex roofs.

### Also-ran for a custom pipeline
- **Pix4Dengine** — real SDK/API, but pricier and more cloud-tied.
- **RealityCapture / DJI Terra** — fast but Windows+NVIDIA and less pipeline-native (§2b).
- **Scanifly / DroneDeploy** — cloud, design/partner-oriented export → **not ideal for a
  custom pipeline** despite being polished.

### ⚠️ The honest limit: glass & solar panels do NOT reconstruct "perfectly"
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

### Recommendation
Make **OpenDroneMap/NodeODM the Stage-1 front-end** (self-hosted REST API, standard exports,
data stays yours), with **Metashape's Python SDK** as the paid upgrade if you need better
meshes. Wire it behind the `GeometrySource` interface as the concrete `SfmSource` (§8, §11);
everything from Stage 2 on — the dirt/mold/material/cleaning intelligence — stays your
proprietary, in-house layer.

---

## 3. Stage 2 — Thermal registration (BUILD — this is ours)

The SfM tool used only the **RGB** frames (thermal isn't good for feature matching). So
after we have the mesh, we must **paint the thermal data onto it ourselves.** No
off-the-shelf tool does this well for cleaning — this is our code.

### The algorithm

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

### Tools we lean on (libraries, not products)

- **Open3D** (BSD license) — mesh I/O, raycasting, point-cloud ops. Free, commercial-OK.
- **trimesh** (MIT) — mesh geometry, ray-triangle intersection, face areas/normals.
- **OpenCV** (Apache 2.0) — camera calibration, undistortion, frame handling.
- **NumPy / SciPy** — the math.
- **PDAL** (BSD) — point cloud translation/filtering if we work at cloud level.
- **rasterio / GDAL** — read the orthomosaic + DSM GeoTIFFs.

All permissively licensed. All commercial-safe. **None of them know anything about
cleaning — the registration logic is 100% ours and is a trade secret** (the view-angle
weighting, the reflection-rejection heuristic, the extrinsic calibration constants).

### Repo home
```
propwash/backend/fusion/
  sfm_ingest.py            # read ODM/Pix4D outputs into our data structures
  thermal_registration.py  # THE core build — project thermal onto mesh
  reflection_filter.py     # glass/solar IR reflection rejection (trade secret)
  twin_builder.py          # assemble the DigitalTwin (already have the model)
```

---

## 4. Stage 3 — Surface & asset segmentation (BUILD the labels, BUY the backbone)

This is the question the user really asked: **how do we identify solar panels vs.
windows vs. roof tiles vs. gutters from the drone data?** Three complementary signals,
fused:

### Signal A — RGB semantic segmentation (the workhorse)

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

### Signal B — Geometry from the mesh (deterministic, no ML)

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

### Signal C — Thermal (condition, not identity)

Thermal doesn't identify the *surface* so much as its *condition* — the grime/moisture
proxy (CLAUDE.md §5). But it also disambiguates: a warm rectangular blob that RGB
thinks is a solar panel but that's 45°C uniform and rigid is probably an **HVAC unit**
→ exclusion, not a panel.

### The fusion decision

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

### Build vs. buy verdict for Stage 3
- **BUY (open source):** SAM/SAM2, the segmentation backbone, Open3D RANSAC, OpenCV.
- **BUILD (ours, secret):** the labelled training dataset of San Diego roofs, the
  classifier head, the geometry rule set, the three-signal conservative fusion, the
  exclusion-zone logic. **This is defensible IP** — a competitor can download SAM too,
  but they can't download our labelled dataset or our fusion rules.

---

## 5. Stage 5 — Flight / coverage path generation (BUILD)

Once each zone is classified and prescribed, we generate **how the cleaning drone
should cover it.** This is a **coverage path planning (CPP)** problem — a known robotics
field we can borrow algorithms from, but the *cleaning-specific* constraints are ours.

### What "flight path" means here (critical framing, §9)

Per CLAUDE.md §7/§10, the Sherpa is **operator-piloted**. So the output of this stage
is **NOT an autonomous flight command stream.** It is an **operator guidance overlay**:
the app shows the operator the recommended standoff surface, sweep lines, coverage
order, and keep-out volumes — the operator flies it and stays in command. If/when Lucid
exposes an API and FAA waivers permit (Path B/C), the *same computed path* can feed more
automation behind a feature flag. We compute the path either way; we don't assume we
get to fly it autonomously.

### The computation, per zone

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

### Tools we lean on
- **Open3D / trimesh** — normal offsetting, mesh boolean for keep-outs.
- **Shapely** (BSD) — 2D polygon ops for per-plane boustrophedon decomposition.
- **NetworkX** (BSD) — zone-ordering as a routing/TSP-ish graph problem.
- **NumPy** — the geometry.
- (Optional later) **OMPL / MoveIt** concepts for 3D motion planning if we go full Path C.

### Repo home
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

## 6. Build-vs-buy summary (the whole pipeline)

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

## 7. Data sovereignty (why self-hosted matters)

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

## 8. Do we ever add LiDAR? (documented future option, not now)

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

## 9. The flight-automation boundary (safety + legal — do not blur)

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

## 10. Concrete tech stack (add to CLAUDE.md §12 stack)

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

## 11. Suggested repo layout (extends CLAUDE.md §13)

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

## 12. Build roadmap for the pipeline

### Phase 1 — Geometry online (weeks 1–3)
1. Stand up **OpenDroneMap** (Docker) on a GPU box / cloud instance.
2. Process one real Autel survey → confirm we get cloud + mesh + ortho + DSM.
3. Build `sfm_source.py` behind a `GeometrySource` interface.
**Milestone:** raw Autel flight → 3D model on our servers, no third-party cloud.

### Phase 2 — Thermal twin (weeks 3–6)
4. One-time **camera calibration** (thermal intrinsics + RGB↔thermal extrinsics).
5. Build `thermal_registration.py` — project °C onto mesh faces (Open3D raycast).
6. Build `reflection_filter.py`; assemble the `DigitalTwin`.
**Milestone:** thermographic digital twin renders in the visor (already built).

### Phase 3 — Segmentation (weeks 6–12)
7. Wire **SAM** for region proposals; label a starter dataset of ~30–50 San Diego roofs.
8. Train the surface classifier head; add `geometry_rules.py` + `fusion_decision.py`.
9. Feed labelled zones into the existing Fusion → Supervisor → safety chain.
**Milestone:** upload a survey → auto-labelled zones (solar/window/tile/…) with
conservative fusion + exclusion zones.

### Phase 4 — Coverage path (weeks 12–16)
10. Build offset-surface + boustrophedon `coverage_path.py`; `keep_out.py`;
    `zone_ordering.py`.
11. Render the **operator guidance overlay** in the visor over the twin.
12. Emit the structured path behind `PROPWASH_ENABLE_PATH_B` (flagged off).
**Milestone:** full survey → labelled zones → prescriptions → operator-flyable
coverage plan, end to end, no hardware autonomy assumed.

---

## 13. The one-paragraph answer to the user's question

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
