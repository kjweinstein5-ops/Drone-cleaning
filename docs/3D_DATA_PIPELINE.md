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

**Not for Year 1.** SfM from the Autel is sufficient for cleaning prescription. Add
LiDAR only if a concrete need appears:

- **When it'd help:** heavy tree occlusion around a property; survey-grade geometry for
  very tall/complex commercial structures; night/low-light capture; faster turnaround
  (LiDAR needs less overlap than SfM).
- **What it'd cost:** a different aircraft + payload (e.g., DJI Matrice 350 + Zenmuse
  L2, ~$15–20K all-in) and a second processing path (LiDAR → point cloud is direct, no
  SfM needed; our Stage 2–5 code stays the same because it already consumes a point
  cloud + mesh).
- **Architecture note:** because Stage 2+ consumes a **point cloud + mesh abstraction**,
  swapping the *source* from SfM to LiDAR is a Stage-1 change only. Keep Stage 1 behind
  a `GeometrySource` interface (`SfmSource`, `LidarSource`) — mirror the swappable
  `ExecutionTransport` pattern. **Don't hard-code SfM assumptions into Stage 2+.**

Do **not** claim LiDAR in any spec/patent/marketing until it's actually in the loop
(CLAUDE.md §5 honesty rule).

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
photogrammetry — there's **no LiDAR** on the Autel, and we don't need one for Year 1.
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
