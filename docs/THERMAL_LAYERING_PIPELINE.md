# Deep Dive — Layering Thermal onto the 3D Model (precisely)

> How captured imagery becomes a 3D model with thermal painted onto it, per-surface,
> accurately enough to drive per-surface pressure decisions.
>
> Companion to `3D_DATA_PIPELINE.md` (which picks the engine) — this doc is the **precision
> procedure** for the thermal overlay specifically.

---

## 0. The headline

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

## 1. Why the Autel 4T V2 makes this work

Multi-camera mode depends on the sensors being rigidly co-mounted and triggering together.
On the 4T V2 the wide, zoom, thermal and laser rangefinder share **one gimbal**, so every
capture is a genuine RGB/IR group: same position, same attitude, same instant, differing only
by a fixed boresight (`geometry/autel_ingest.py`).

**Contrast with a two-aircraft rig:** you'd be solving cross-flight alignment for every frame —
different times, different poses, different lighting/thermal state. The co-registered payload
turns that alignment problem into a **constant**. This is the single strongest technical
argument for the 4T V2 as the scout.

---

## 2. Why RGB must drive the geometry

Photogrammetry works by matching visual features between overlapping images. **Thermal imagery
is low-resolution (640×512), low-contrast, and its "features" move with temperature** — a warm
patch is not a stable landmark. Trying to build geometry from thermal produces poor meshes.

So: **RGB builds the shape; thermal supplies the values.** Every serious thermal-3D workflow
follows this order, and it's why our `SurveyCapture.rgb_paths` feeds photogrammetry while
`thermal_paths` is held for the overlay step.

---

## 3. Two different thermal outputs — we need BOTH

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

## 4. The precision chain — where accuracy is won or lost

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

## 5. Timing — the biggest free accuracy win

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

## 6. The concrete pipeline (what we run)

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

## 7. Open items
- [ ] Confirm Metashape multi-camera ingests Autel 4T V2 RGB/IR groups without manual pairing.
- [ ] Perform the one-time boresight calibration; store the `Boresight` constants per airframe.
- [ ] Price the Autel **RTK module** (biggest single precision upgrade).
- [ ] Define the standard survey pattern (overlap %, altitudes, orbit+nadir) as an SOP.
- [ ] Add thermal-optimal time-of-day windows to the scheduling engine.

## Sources
- [Agisoft — thermal, multispectral & LiDAR data in Metashape](https://www.agisoftmetashape.com/using-agisoft-metashape-with-thermal-multispectral-and-lidar-data/) · [Metashape Pro user manual 2.0 (PDF)](https://www.agisoft.com/pdf/metashape-pro_2_0_en.pdf)
- [MetaMosaic — RGB + thermal orthomosaics via Metashape/CloudCompare](https://github.com/s-du/MetaMosaic)
- [Metashape vs Pix4D comparison](https://vagon.io/blog/agisoft-metashape-vs-pix4d-which-photogrammetry-software-should-you-choose)
