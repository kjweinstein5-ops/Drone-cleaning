# PROPWASH — Launch Playbook

> One place for the *practical* launch essentials: **what to ask vendors**, the **open-source
> stack to build on**, the **steps to first revenue**, and an **index of everything already
> built** in this repo. Pairs with the decision notes in `docs/decisions/`.

---

## Part 1 — Questions to ask every vendor

### ⭐ 1.0 THE INTEGRATION QUALIFICATION QUESTIONNAIRE (send this to EVERY manufacturer, before buying anything)

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

### Vendor-specific follow-ups (after the Q1–10 baseline)

### 1A. Lucid Bots (cleaning drone — Path A first)
Full list in `docs/LUCID_OUTREACH.md`. The five that matter most:
1. Does **Lucid Refresh** expose an API (REST/GraphQL/webhooks)? Can we **read** job status/
   telemetry and **push** structured work orders?
2. Any supported way to send **pump/pressure/dwell setpoints** (MAVLink or partner endpoint)? Roadmap?
3. Policy on **companion computers / third-party hardware** on an owned Sherpa — warranty impact?
4. **Who owns** the job/sensor data generated on a customer's Sherpa?
5. Partner/reseller economics — will Lucid **co-sell** to operators who want our intelligence layer?

### 1B. DJI (scout + retrofit cleaning drone — the owned-stack path)
Ref `docs/decisions/DJI_TWO_DRONE_ARCHITECTURE.md`.
1. Confirm **Matrice 4T** price/lead-time + thermal spec vs the **Zenmuse H30T** for our needs.
2. Does **Cloud API (MQTT)** give us the telemetry/imagery ingest + mission dispatch we need?
3. Does **Payload SDK (PSDK v3)** support commanding a **pump/nozzle** payload (our PSM/IHM)?
4. Does mounting a third-party cleaning payload **void warranty**? What's the airworthiness stance?
5. NDAA/procurement exposure for US commercial use — any restrictions we should plan around?

### 1C. Retrofit cleaning-payload vendors — Foxtech / drone-payload
Ref `docs/decisions/CLEANING_DRONE_PLATFORM.md`.
1. **Price** of the AeroClean (P3/T50, T-M400C) or RT-AP3 kit — the biggest unknown in the model.
2. Which **DJI airframes** are supported (M350 / M400)? Tethered vs untethered water?
3. **Max pressure / flow / reach**, and per-hour coverage (m²/h)?
4. Can we integrate **our own pressure/nozzle control** (PSM/IHM) or is the payload closed?
5. Warranty, support, spares, and lead time.

### 1D. Open-platform (if going owned/vendor-neutral) — Freefly / PX4
Ref `docs/decisions/OPEN_PLATFORM_INTEGRATION.md`.
1. Freefly **Astro** price + **Smart Dovetail / Payload Bus** power+data specs for a cleaning payload.
2. Does **MAVSDK** expose the payload control (pump/nozzle setpoints) we need?
3. FAA waiver scope for any beyond-operator automation on this platform.

### 1E. Photogrammetry / processing (the geometry engine)
Ref `docs/3D_DATA_PIPELINE.md` §2d.
1. **OpenDroneMap/NodeODM** self-host (free) vs **Metashape** (~$3.5K, Python SDK) — mesh quality on roofs?
2. Can we get the raw **mesh/point cloud export** (OBJ/LAZ/GeoTIFF) into our pipeline?
3. **Scanifly** (solar-specialized) — does its export feed a custom pipeline, or only racking partners?

### 1F. Anthropic / cloud (the AI layer)
1. Commercial API **data terms** (no-training), **Zero-Data-Retention** eligibility, or **Bedrock/Vertex** tenant.
2. (Ref `docs/decisions/COMPUTE_INFRASTRUCTURE.md` — Claude runs cloud-side; data stays yours via terms.)

---

## Part 2 — The open-source & off-the-shelf stack (what to build on)

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

## Part 3 — The 90-day path to first revenue (owner-operated)

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

## Part 4 — What's ALREADY built in this repo (your asset base)

### Working software (79 tests passing)
- **Drone-scan pipeline** — `propwash/backend/geometry/`, `fusion/`, `segmentation/`: scan →
  3D model → surface types + grime proxy + exclusion zones. Demo: `python -m sim.scan_demo`.
- **Scan → plan** — `planning/scan_to_plan.py`: classified zones → safety-gated work orders.
  Demo: `python -m sim.scan_to_plan_demo`.
- **Flight path (Stage 5)** — `planning/coverage_path.py`: standoff sweeps + keep-outs, solar-
  first ordering. Demo: `python -m sim.flight_plan_demo`.
- **Safety layer** — `safety/`: deterministic pressure ceilings + human-presence detection.
- **Execution transports** — `execution/`: Path A active; DJI/MAVLink/companion seams flagged off.
- **The visor** — `samples/propwash_visor_artifact.html` (hosted Artifact) + `frontend/`.

### Business & strategy
- `docs/BUSINESS_PLAN.md`, `docs/SCALING_TO_10M.md` — the plan + path to $10M.
- Revenue/cost models — `propwash/backend/reports/`: `revenue_model.py`,
  `drone_platform_cost.py`, `platform_payback.py`, `roi_report.py`.
- `docs/IP_PROTECTION.md`, `docs/DYNAMIC_PRESSURE_HARDWARE.md` — the moat + hardware IP.

### Decisions (in `docs/decisions/`)
Sensor platform · spectral sensing · compute infra · cleaning-drone platform · DJI two-drone
architecture · open-platform integration.

### Vendor outreach
- `docs/LUCID_OUTREACH.md` — full Lucid question set + partnership framing.
- Part 1 above — DJI, retrofit, open-platform, processing, and cloud question sets.

---

**The honest one-liner:** most of what a "business plan chat" would hand you as bullet points
already exists here **as working code, tested models, and decision records** — this playbook is
the index + the practical next steps to turn it into a running company.
