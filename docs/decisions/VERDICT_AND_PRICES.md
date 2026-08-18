# ⭐ VERDICT — the two aircraft, the system, and what it costs

> *"Give me the verdict — what drone for both applications, scout and cleaning, and prices."*
>
> Final procurement recommendation. Screened **2026-08-16**.
> Prices are list/retail from public sources and are **subject to quote**. Every compliance
> claim must be re-verified at purchase (§6).

---

## THE VERDICT

| Role | Aircraft | Price |
|---|---|---|
| **SCOUT / MAPPING** | **Skydio X10D** | **~$16,000** |
| **CLEANER** | **Inspired Flight IF1200A** | **~$32,000** airframe |

Both **US-made**, both **Blue UAS Cleared**, both **open enough to run our stack**.

### The headline number

**The complete two-aircraft PROPWASH fleet — everything, both aircraft, ground rig, payload,
software — costs $71K–$93K.**

**A single Lucid Sherpa costs $75,000 outright.**

For the price of one closed spray drone that maps nothing and integrates nothing, you get a
scout, a cleaner, the ground rig that holds the pressure IP, and a stack you own end to end.

---

## 1. SCOUT — Skydio X10D · ~$16,000

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

## 2. CLEANER — Inspired Flight IF1200A · ~$32,000

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

## 3. FULL COSTED BILL OF MATERIALS

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

### ⭐ The ground rig is almost free, and it's a perfect match

Commodity 12V soft-wash systems run **5.3–7 gpm at 60–100 PSI** for **$1,500–$2,500**.

**60–100 PSI is 4–7 bar. That is our prescription range exactly** — stucco 4.0, tile 5.0,
shingle 5.5, gutter 6.5. We are not designing exotic hardware; we are buying a standard
contractor rig and putting an electronic regulator and our controller on it.

**The "PSM" from `DYNAMIC_PRESSURE_HARDWARE.md` is a ~$3–6K ground assembly, not an
aerospace project.**

---

## 4. SPEND IT IN THIS ORDER

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

## 5. WHAT YOU GET THAT NOBODY ELSE HAS

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

## 6. ⚠️ VERIFY BEFORE YOU SPEND

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
