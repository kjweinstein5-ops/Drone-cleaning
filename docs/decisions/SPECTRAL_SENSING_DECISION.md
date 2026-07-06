# Decision Note — Spectral Sensing for Mold / Dirt / Biofilm Analysis

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

## 1. The honest reframe — what "spectrum analysis of mold and dirt" actually means

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

## 2. The spectral ladder — four rungs, increasing capability & cost

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

## 3. What multispectral actually buys us (the indices)

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

## 4. The sensor options (verified July 2026)

### Option A — DJI Mavic 3 Multispectral (M3M) — *pragmatic entry*
- **Bands:** RGB 20 MP + Green (560), Red (650), **Red-Edge (730)**, **NIR (860)**.
- **Extras:** built-in RTK, DLS 2 irradiance sensor (sun-normalization — important for
  consistent readings across days/weather), 43-min endurance.
- **Thermal:** ❌ none.
- **Price:** ~$5,000–5,700.
- **Verdict:** cheap, capable multispectral. But **no thermal** → you'd fly it *alongside*
  the Autel (two aircraft, two flights, loose-synced per CLAUDE.md §6). Best low-cost way
  to add real biofilm detection without abandoning your thermal channel.

### Option B — Sentera 6X Thermal Pro — ⭐ *the technically best answer*
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

### Option C — MicaSense RedEdge-P — *multispectral-only, high res*
- 5 narrow bands + panchromatic, pansharpened to ~2 cm at 60 m. Excellent multispectral
  detail, no thermal. Similar role to the M3M but higher-end / integrator-oriented.

### Option D — Hyperspectral (Headwall / Cubert class) — *future / overkill*
- 100s of bands, 99% material-ID accuracy. Expensive ($25K–100K+), heavy, complex
  processing, false-positive risk. **Not Year 1.** Revisit only if fine material
  discrimination becomes a proven product need.

---

## 5. Recommendation

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

## 5a. ⭐ Updated recommendation given Kevin's steer (thermal-forward)

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

## 6. How this resolves CLAUDE.md §5

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

## 7. IP implications (this is why it matters beyond data quality)

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

## 8. Architecture / pipeline impact

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

## 9. Open items before locking the decision

- [ ] Confirm budget envelope: Matrice 350 + 6X Thermal Pro quote (Option B) vs. M3M
      ~$5–6K (Option A).
- [ ] Decide capital appetite: buy the best now (B) or prove value cheap then upgrade (A→B).
- [ ] Confirm we keep/own the Autel EVO II 640T for the two-drone Option A path.
- [ ] Attorney: confirm what spectral claims we may make once multispectral is in the loop.
- [ ] On purchase: update CLAUDE.md §4 + §5, add `MULTISPECTRAL` to `models/zone.py`.
- [ ] Confirm Part 107 coverage for the added platform / any automated survey missions.

---

## 10. Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Initial analysis surfaced Option B (multispectral) as the max-capability path | Claude (advisory) | Superseded by Kevin's steer same day |
| 2026-07-06 | **Kevin's steer: thermal-forward, "doesn't need to be exact" → CLAUDE.md §5 Option A** (stay Autel thermal+RGB proxy; multispectral = future upgrade) | Kevin | See §5a. Recommend closing §5 as **Option A** once confirmed |

---

## Sources
- [DJI Mavic 3M specifications — DJI Ag](https://ag.dji.com/mavic-3-m/specs)
- [DJI Mavic 3 Multispectral — Advexure](https://advexure.com/products/dji-mavic-3-multispectral)
- [Sentera 6X Sensor](https://senterasensors.com/6x/)
- [MicaSense RedEdge-P — Wingtra](https://wingtra.com/mapping-drone-wingtraone/drone-sensors/micasense-rededge-p/)
- [Red-edge / chlorophyll-a algae detection — Frontiers in Remote Sensing](https://www.frontiersin.org/journals/remote-sensing/articles/10.3389/frsen.2025.1633491/xml)
- [Multispectral vs hyperspectral façade material classification — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0926580522000371)
- [Multispectral vs Hyperspectral imaging — Anvil Labs](https://anvil.so/post/multispectral-vs-hyperspectral-imaging-key-differences)
- [Aerial imaging-based solar PV soiling detection — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11821171/)
