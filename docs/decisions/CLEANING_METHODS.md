# Cleaning methods beyond spraying — and what "Raptor" actually is

> *"Explore other drones like the Raptor drone — is this something we utilize for cleaning the
> surfaces we want to clean, other than spraying?"*
>
> Screened 2026-08-16. Two separate questions, answered separately.

---

## 1. "Raptor" — it isn't a cleaning drone

**No cleaning drone called Raptor surfaced in any search.** The near-certain referent is
**Raptor Maps**, and it matters — but not as hardware.

**Raptor Maps is a solar asset-management analytics platform.** It builds **geospatial digital
twins of solar facilities**, fusing drone imagery, thermal inspection, SCADA and maintenance
records; runs AI thermal analytics to find module-, string- and combiner-level defects; and drives
technician workflow through a field app.

### ⚠️ Why this is worth your attention

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

## 2. Non-spray cleaning — three real categories

### 2.1 Contact tools on a drone (brush / squeegee) — ❌ the industry moved away

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

### 2.2 Waterless robotic cleaning — ✅ real, proven, and **not a drone**

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

### 2.3 ⭐ Dry / low-water methods on OUR aircraft — the idea worth keeping

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

## 3. ⭐ The real consequence: prescribe METHOD, not just parameters

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

### Why this is genuinely differentiating

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

## 4. Verdict

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
