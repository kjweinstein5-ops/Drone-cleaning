# Fleet Architecture — every aircraft and system, for all needs

> *"Continue analyzing, finding the best drone and system for all my needs."*
>
> Supersedes the single-aircraft framing in `BUILD_SPEC.md`. Screened 2026-08-16.
>
> ⚠️ **This document changes the scout recommendation and re-ranks the cleaning airframe.**
> A December 2025 FCC action broke assumptions made throughout this repo.

---

## 0. ⚠️ THE RULE CHANGE THAT RESETS EVERYTHING

On **22 December 2025** the FCC added to its Covered List **all uncrewed aircraft systems, and
UAS critical components, produced in a foreign country.** Wiley called it
"unexpected, first-of-its-kind." It is far broader than the DJI action we already logged.

| What | Effect |
|---|---|
| Covered equipment cannot obtain **new FCC equipment authorizations** | No new import, marketing or sale in the US |
| **Previously authorized models stay valid** | Existing fleets keep flying |
| Scope includes **"UAS critical components"** | Not just airframes — components too |

**Two exemptions (issued 7 Jan 2026, effective through 1 Jan 2027):**

1. **Blue UAS Cleared List** — DCMA-managed (moved from DIU in July 2025)
2. **Buy American** — manufactured in the US with **domestic content > 65% of cost**
   (rising to 75% after 2028)

### What this breaks in our own plan

- ❌ **The Autel EVO MAX 4T V2 — our scout — is Covered.** The FCC named **DJI *and* Autel**
  explicitly, and then covered all foreign-produced UAS besides. Autel is contesting it (arguing
  the FCC relied on classified material it could not see, and on allegations aimed at DJI), but
  **the proceeding is live and the listing stands.**
  → **CLAUDE.md §4 names the Autel as the sensing platform. That needs to change.**
- ❌ **Foxtech / EAUAV payloads look worse, not better.** "UAS critical components" plausibly
  captures a foreign-made powered payload. Already a "no" on pressure class; now likely a
  sourcing problem too.
- ⚠️ **Every compliance claim in this repo has a shelf life.** The exemptions expire
  **1 January 2027**. Re-verify at purchase — do not trust this document or any vendor's page.

---

## 1. The fleet — four roles

| # | Role | Recommendation | Status |
|---|---|---|---|
| 1 | **Scout / mapping** | **Skydio X10D** | ⭐ NEW — replaces the Autel |
| 2 | **Cleaner (aerial soft-wash)** | **Inspired Flight IF1200A** *or* Freefly Alta X Gen2 | ⭐ RE-RANKED |
| 3 | **Ground unit (hardscape, high pressure)** | Deferred — conventional gear first | Phase 3 |
| 4 | **Second aerial (pre-soak pipelining)** | Deferred — only pays on large commercial | Phase 3 |

---

## 2. Role 1 — Scout. **Skydio X10D**

The Autel replacement, and on the merits it is an upgrade rather than a compromise.

| | Skydio X10D |
|---|---|
| Compliance | ✅ **Blue UAS Cleared** (X10D since 2024; X10, R10 and Dock added July 2026) |
| Thermal | **Teledyne FLIR Boson+** — described as the most precise radiometric thermal sensor in small UAS |
| Optical | **Three optical sensors** alongside the thermal, in one camera system |
| Origin | US |

### Why it preserves the thing that mattered

`THERMAL_LAYERING_PIPELINE.md` §1 argued the single strongest case for the Autel 4T V2 was
**co-registered RGB + thermal on one gimbal** — it turns cross-sensor alignment from a per-frame
problem into a fixed boresight constant, which is what makes Metashape's multi-camera workflow
clean.

The X10D carries its optical and thermal sensors in **one camera system**, so that property
survives the swap. `geometry/autel_ingest.py` models boresight as a constant; the module needs a
rename and a new file-format reader, **not a redesign**.

**Radiometric matters more than resolution here.** Our grime proxy reads *differential*
temperature — a patch cooler than the surface around it. That needs trustworthy per-pixel
temperature, which is exactly the Boson+'s claim.

**Budget alternative: Parrot ANAFI USA** — Blue-cleared, multi-sensor, and described as the most
accessible option on the list. Lower capability; a reasonable way to start cheap.

> ⚠️ **Verify before buying:** radiometric (not just thermal) output, whether the raw radiometric
> data is *exportable* for our own registration, and thermal resolution. A thermal camera that
> only exports a colourised JPEG is useless to `fusion/thermal_registration.py`.

---

## 3. Role 2 — Cleaner. **Re-ranked, and it is closer than it looked**

### The wrinkle in the Alta X recommendation

Freefly's Alta X was incorporated into the DIU Blue List 2.0 in **December 2023**, then granted a
**one-year Exception to Policy extension running to 28 February 2026** — which has now passed.
Freefly publishes a knowledge-base article on *"DIU Blue List and transition to AUVSI Green
List,"* which suggests a move from Blue to Green.

**Blue listing is one of only two FCC exemptions.** So this is no longer a nice-to-have badge —
it is a purchase-eligibility question.

Freefly is US-made, so the **Buy American >65% domestic content** exemption very likely covers it
regardless. But that is an inference, not a verified fact, and it should be confirmed in writing.

### Side by side

| | **Inspired Flight IF1200A** | **Freefly Alta X Gen2** | **Watts PRISM Sky** |
|---|---|---|---|
| Blue UAS status | ✅ **Blue UAS-certified** (IF1200A + IF800 listed) | ⚠️ ETP lapsed Feb 2026; Green List transition | ⚠️ NDAA stated; **Blue status unconfirmed** |
| Also | **Green UAS dual-certified** | — | — |
| Payload | 8 kg / 19.1 lb | **15.9 kg / 35 lb** | 11.3 kg / 25 lb |
| Endurance | ⭐ **~43 min** | ~20 min @ 20 lb | — |
| Flight stack | Open **PX4** | **Auterion** Skynode | **Auterion** |
| Onboard app | Companion computer (DIY) | ⭐ **AuterionOS SDK, sandboxed** | ⭐ AuterionOS |
| Payload interface | Universal Payload Interface | Bay: Ethernet + power + LTE | Rails top *or* bottom |
| Price | quote | ~$45,000 | quote |

### The payload question resolves itself

We established in `BUILD_SPEC.md` that with **tethered water** the aircraft carries a gun, a hose,
a valve, a nozzle, a flow sensor, a rangefinder and a small computer — call it **3–5 kg**.

**So 8 kg is ample. The Alta X's 15.9 kg advantage buys nothing we need**, while its ~20 min at
load is less than half the IF1200A's 43 min. Endurance is the number that shapes the field day
(`FIELD_OPERATIONS.md` §5.1), and more endurance means fewer battery swaps.

### The real trade

| If your priority is… | Choose | Because |
|---|---|---|
| **Compliance certainty + endurance** | **IF1200A** | Blue-cleared today; 43 min; 8 kg is enough for a tethered rig |
| **The AuterionOS onboard app** | **Alta X** or **PRISM Sky** | Managed ROS 2 sandbox, supported, enforces the Tier separation structurally |

**A companion computer on the IF1200A's PX4 gets the same *function*** — read telemetry, command
motion, drive actuators. Auterion buys a *supported, sandboxed* way to do it, which is worth real
money for the insurer and waiver story (`PLATFORM_VENDOR_CHOICE.md` §2), but it is not the only path.

### 🎯 Recommendation

**Lead with the Inspired Flight IF1200A**, on compliance certainty and endurance, and build the
onboard layer as a companion-computer app on open PX4.

**Keep Alta X / PRISM Sky live** if Auterion's SDK proves decisive after the Virtual Skynode
evaluation — which costs a subscription and no aircraft.

*This reverses `BUILD_SPEC.md` §1. The reason is the FCC action, not new opinion.*

---

## 4. Roles 3 and 4 — deliberately deferred

### Ground unit (hardscape)

Concrete, driveways and parking decks genuinely need **100–200 bar** — the range we correctly
refused for the aircraft. That is a **ground robot's** job.

**Do not buy one yet.** A conventional surface cleaner and an operator does hardscape today at
near-zero capex. The robot is justified when hardscape is a large, recurring share of revenue —
and the intelligence layer transfers to it unchanged, because per-surface prescription and
verification do not care what the machine is.

### Second aerial (pre-soak pipelining)

The phase scheduler shows why this waits: on the reference house, deconfliction caps concurrency
at **1 aircraft**, so a second aircraft changes job time by **nothing**. And the 900-second-dwell
model showed a single aircraft already hides **66 of 66.5 minutes** of dwell by switching zones.

**A second aircraft pays only on large commercial and solar sites, and only with a 107.35 waiver.**
Both belong to the re-aimed segment in `GO_NO_GO.md`, not to Year 1.

---

## 5. The complete system

```
 SCOUT              Skydio X10D  (Blue) ── RGB + radiometric thermal, one gimbal
   │
   ▼
 PROCESS            photogrammetry → our fusion → per-face surface + grime layer
   │
   ▼
 PRESCRIBE          per-zone pressure / chemistry / dwell, safety-gated, human-signed
   │
   ▼
 EXECUTE            IF1200A + soft-wash gun on a ground tether
   │                 ├── airborne: gun, hose, valve, nozzle, flow sensor, rangefinder, computer
   │                 └── GROUND:  pump · electronic regulator (= the PSM) · firmware ceiling
   │                              chemical injection · DI stage · containment
   ▼
 VERIFY             re-scan → PASS / re-queue → deviation log → surface-table calibration
```

**Two aircraft, one ground rig, one software stack.** The ground rig holds the pressure IP; the
aircraft is a positioning system for a nozzle; the software is the company.

---

## 6. Capital, in the order it should be spent

| | Item | Aircraft needed? |
|---|---|---|
| 1 | **Ground rig** — pump, regulator, gun on a stand | ❌ |
| 2 | **Auterion Developer Program + Virtual Skynode** (evaluate the SDK) | ❌ |
| 3 | **Scout** — Skydio X10D (or ANAFI USA to start cheap) → **scan-only revenue** | ❌ cleaner |
| 4 | Vendor quotes: Inspired Flight, Freefly, Watts | ❌ |
| 5 | **Cleaner** — IF1200A + integration | ✅ |
| 6 | Ground robot / second aerial | ✅ |

**Steps 1–4 need no cleaning aircraft, and step 3 earns money.** The scout is the only aircraft
required to start, and it is the one that generates the differentiated product.

---

## 7. What must be re-verified before any purchase

- [ ] **Blue UAS Cleared List membership**, on the **DCMA list itself** — not vendor marketing —
      for every airframe considered. *Freefly Alta X's status is specifically unclear.*
- [ ] **Skydio X10D radiometric export** — can we get raw per-pixel temperature out, in a form
      `fusion/thermal_registration.py` can consume?
- [ ] **Which FCC exemption** each purchase relies on (Blue listing vs Buy American >65%) — and
      that it is documented, since **both expire 1 January 2027**.
- [ ] **Liquid spray payload support** — warranty and airworthiness, from Inspired Flight and
      Freefly. ⚠️ Still the disqualifying question.
- [ ] **Whether a foreign-made payload counts as a "UAS critical component."** ⚠️ Counsel.
- [ ] **Insurance** for a self-integrated spray drone. Still unasked, still likely decisive.

> `TODO(PROPWASH): CLAUDE.md §4 hardware inventory is out of date — the Autel is Covered-Listed.`
