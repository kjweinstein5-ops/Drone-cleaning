# PROPWASH — Field Operations, End to End

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

## 0. What actually exists today — read this first

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

## 1. Qualify the site — before anyone drives out

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

## 2. Scout flight — capture

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

## 3. Process — and the latency that shapes the whole business

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

### ⚠️ This latency forces a two-visit model

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

## 4. Prescribe and review — the human gate

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

## 5. Wash day

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

### 5.1 Battery swaps are a first-class cost

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

### 5.2 Ordering constraints the planner already enforces — and one it doesn't

The planner sequences solar-first and top-down (`planning/zone_ordering.py`): you wash top-down
so runoff never re-dirties finished work, and solar first because it's the most sensitive.

**What the planner does not know: solar panels must not be washed hot.** Cold water on
sun-loaded glass is a thermal-shock risk, and industry practice is early morning or evening.
That collides directly with §2.1:

> **The scan window (10:00–15:00, sun-loaded) and the solar wash window (early/late, cool) are
> mutually exclusive.** This is another reason scan day and wash day are different days.

*TODO(PROPWASH): encode a per-surface time-of-day constraint in the scheduler. Today it is the
crew's job to remember.*

### 5.3 Treatment phases

Each zone gets pre-soak → chemical → **dwell** → rinse. Pre-soak and rinse are water-only by
construction. Dwell occupies no aircraft, which is why the scheduler can pipeline it — but on
this house deconfliction caps concurrency at **1 aircraft**, so there is nothing to pipeline
*into*. Multi-aircraft pays off on large commercial and solar sites, not compact residential.

### 5.4 The operator stays in command

Part 107, always. The app says which nozzle to fit and when to begin; the operator confirms,
executes, monitors video plus the thermal overlay, and can abort at any moment. The system is
designed to reduce the *skill* required, never the *authority*.

---

## 6. Verify — and the problem nobody warns you about

### ⚠️ The dry-down problem

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

### 6.1 The re-queue loop

Failed zones get adjusted parameters and re-queue. Under a same-day RGB verification the
adjustment is bounded — you can raise dwell or re-run a pass, but you cannot chase a thermal
residual you can't yet trust.

### 6.2 The deviation log

Every job records prescribed-vs-actual: pressure, dwell, standoff, coverage, outcome. **This is
the flywheel.** The uncalibrated defaults in the surface table only become real numbers by
accumulating these deltas across jobs. Treat the log as the product, not as telemetry exhaust.

---

## 7. Close

⏱ **15 min, mostly automated.**

- Customer report: before/after twin, per-zone results, what was excluded and why.
- Invoice.
- Schedule the next service — and note that its pre-scan verifies this one (§6, option 3).
- Push the deviation log into the learning set.

The report is a genuine differentiator. Nobody else in exterior cleaning hands the customer a
3D model of their own building with the dirt mapped on it, before and after.

---

## 8. Failure modes, ranked by how much they cost you

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

## 9. Crew and kit

**Year 1: one crew of two.**

| Role | Does |
|---|---|
| **RPIC (Part 107)** | Flies both aircraft, owns the go/no-go, owns the abort |
| **Ground tech** | Water, hose, pump, batteries, nozzle changes, containment, customer contact |

The RPIC is the licensed, non-delegable role. The ground tech is trainable in days. That ratio
is what makes the model scale — and it is why the software's job is to remove *skill*
requirements, not authority.

### Kit
Scout drone + spare batteries · cleaning drone + **enough batteries to never wait** · fast
charger · pump and hose · chemical stock, measured and labelled · nozzle set (see the IHM
concept in `DYNAMIC_PRESSURE_HARDWARE.md` for removing manual changes) · containment (berms,
vacuum, mats) · ground station laptop + LTE · cones, signage, PPE.

---

## 10. The honest summary

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
