# DEFINITIVE — the drone, the add-ons, and why

> **Kevin:** *"Give me a definitive answer of what drone company we can use to integrate our tech
> stack… and what add-ons if we use a drone without cleaning — which might be the way to go.
> We can add on Foxtech."*
>
> **Answer: yes, buy a bare drone and add the cleaning yourself — but NOT a Foxtech kit.**
> Reason in §2, and it is a number, not an opinion. Screened 2026-08-16.

---

## 1. THE ANSWER

| Decision | Choice |
|---|---|
| **Flight OS** (commit here first) | **Auterion** — AuterionOS + Auterion SDK |
| **Drone company** | **Freefly Systems** — Alta X Gen2, **NDAA SKU** |
| **Aircraft cost** | **~$45,000** |
| **Cleaning add-on** | **Build a soft-wash payload. Do NOT buy a high-pressure kit.** |
| **Water** | **Ground-tethered.** Pump, regulator and chemistry stay on the ground |
| **Backup airframes** | Watts PRISM Sky · Inspired Flight IF1200A — both Auterion/PX4, both NDAA |

**Why Freefly specifically:** Auterion Enterprise PX4 on Skynode, MAVSDK control from the ground
*or* from a companion computer, an internal payload bay with **Ethernet + regulated power + LTE**,
15.9 kg payload, US-made. It is the largest-payload aircraft that runs the OS our software targets.

**Why Auterion first:** because Freefly, Watts and others all run it. Write the integration once,
and the airframe becomes re-sourceable. That is the structural fix for what Lucid did to you — no
vendor can switch you off.

---

## 2. ⭐ Why NOT Foxtech — the number that decides it

**Foxtech's AeroClean kits run 110–200 bar. Our own prescriptions run 1.8–7 bar.
We are a soft-wash system. They are a high-pressure system. It is a 20–30× mismatch.**

Our surface table (CLAUDE.md §9, `prescriptions/`):

| Surface | Our prescribed pressure |
|---|---|
| Solar panel | **1.8 bar** |
| Window glass | 2.2 bar |
| Stucco | 4.0 bar |
| Clay tile / shingle | 5.0–5.5 bar |
| Gutter | 6.0–7.0 bar |

Foxtech AeroClean T-M400C: **110–160 bar**. AeroClean P3 (T50): **20 MPa = 200 bar**.

**Buying that kit would be buying a tool that operates 30× above the ceiling our own safety layer
exists to enforce.** The entire point of `safety/checks.py` is that over-pressure destroys
surfaces. Bolting on a 200-bar rig to run a 1.8-bar solar prescription is not conservative
engineering — it is putting a fire hose on a job that needs a garden sprayer, and trusting
software to never make a mistake.

### The second-order effect: jet reaction force

A spray jet pushes the aircraft backwards. Reaction ≈ `0.0745 × gpm × √psi` (lbf):

| Configuration | Reaction | % of Alta X 35 lb payload |
|---|---|---|
| **Our tile/shingle prescription** — 5.5 bar @ 4 gpm | **2.7 lbf (12 N)** | **8%** |
| Our solar prescription — 1.8 bar @ 4 gpm | 1.5 lbf (7 N) | 4% |
| Foxtech T-M400C — 160 bar @ 4 gpm | **14.4 lbf (64 N)** | **41%, horizontal** |
| Foxtech P3 — 200 bar @ 8 gpm | **32.1 lbf (143 N)** | **92%, horizontal** |

**This is the whole reason purpose-built high-pressure cleaning drones are hard.** Foxtech's own
marketing cites "flexible joints, adaptive balancing" — that is the engineering to fight 64–143 N
of continuous thrust trying to push the aircraft off the wall.

**At our pressures that problem substantially disappears.** ~12 N of reaction on a 15.9 kg-payload
airframe is a routine control-authority question, not a research programme.

> **That is the finding that makes self-integration realistic instead of a moonshot.** We are not
> trying to build a flying pressure washer. We are trying to build a flying *soft-wash* gun, and
> those are two very different engineering problems.

### ✅ CONFIRMED — checked Foxtech's whole catalogue, not one model

Their **entire AeroClean line is high-pressure.** There is no soft-wash option:

| Foxtech model | Pressure | Mounts on |
|---|---|---|
| AeroClean **P1 (A2)** | **20 MPa = 200 bar** | DJI M300 RTK / M350 RTK |
| AeroClean **P2 (A30)** | high-pressure | DJI heavy-lift |
| AeroClean **P3 (T50)** | **20 MPa = 200 bar** | DJI M400 |
| AeroClean **T-M400C** | **110–160 bar** | DJI M400 |
| **P4H** cleaning version | **10 MPa = 100 bar** | DJI |
| AeroClean **F30** | 10 MPa | DJI FlyCart 30 |
| AeroClean **S2 / S4** (solar) | — | DJI T-series ag drones |

**Lowest pressure Foxtech sells is 100 bar. Our highest prescription is 7 bar.**
Even their gentlest product is **14× above** the most aggressive thing we ever ask for, and
**55× above** our solar prescription.

**And every single one is DJI-mount.** This is not "adaptable with effort" — it is the wrong
pressure class on the wrong airframe.

> **Verdict on Foxtech: no.** Not "probably not" — their catalogue contains nothing in our
> pressure class, on any airframe we can buy.

### Three more reasons Foxtech is the wrong purchase

- **DJI-specified.** AeroClean P3 (T50) and T-M400C are built for M350/M400 mounting, power and
  comms. Foxtech advertises "in-depth custom development" but publishes **no non-DJI
  compatibility**. This would be a bespoke engineering engagement, not a purchase.
- **Country-of-origin risk.** Foxtech, EAUAV, ZJIEC and Jitian are all Chinese suppliers. We chose
  a US NDAA airframe specifically to keep federally funded and institutional work open
  (`GO_NO_GO.md`). **Whether a Chinese-made payload on a US airframe preserves that eligibility is
  a legal question we have not answered.** ⚠️ Counsel, before purchase.
- **It solves a problem we don't have.** High-pressure kits exist for concrete, industrial tanks
  and heavy soiling. Our differentiation is *not* damaging surfaces.

**Where Foxtech is still worth a call:** the *mechanical* parts — gimballed gun mounts, lightweight
high-pressure hose, tether management — are genuinely hard and they have solved them. Ask whether
they will supply components decoupled from DJI. That is a much smaller ask than a full kit.

---

## 3. The build — a bare drone plus add-ons

### 3.1 Airborne (keep it stupid)

| # | Item | Why | Notes |
|---|---|---|---|
| 1 | **Freefly Alta X Gen2 (NDAA)** | The aircraft | ⚠️ NDAA SKU only — the stock Herelink radio is **not** compliant; the Doodle Labs variant is |
| 2 | **Companion computer** in the payload bay | Runs our onboard app | Bay supplies Ethernet, regulated power, LTE. Small ARM SBC class |
| 3 | **Soft-wash gun / lance**, gimbal-mounted | Directs the spray | Rated well above 7 bar. Light — this is the whole point |
| 4 | **Lightweight supply hose** | Water from the ground | Sized for ~4–8 gpm at low pressure. Weight and drag are the design drivers, not burst rating |
| 5 | **Solenoid valve** | Pump/flow on-off at the gun | Driven by a PX4 actuator output — `PUMP_CHANNEL` in `mavlink_mission.py` |
| 6 | **Nozzle selector (IHM)** | Per-surface nozzle without landing | `NOZZLE_CHANNEL`. **Phase 2** — fly fixed nozzles first and change by hand |
| 7 | **Downward/forward rangefinder** | Standoff hold, the safety-critical measurement | Standoff is in every prescription; it must be measured, not assumed |

**Airborne total is a gun, a hose, a valve and a small computer.** No tank, no pump, no
high-pressure electronics, no 143 N thrust to fight.

### 3.2 Ground (where the IP lives)

| # | Item | Why |
|---|---|---|
| 8 | **Soft-wash pump**, ~4–8 gpm to ~10–20 bar | Standard soft-wash equipment. Commodity, cheap, well understood |
| 9 | **Electronic pressure regulator / VFD** | **This IS the PSM** from `DYNAMIC_PRESSURE_HARDWARE.md` — it just doesn't fly |
| 10 | **Firmware pressure ceiling on the regulator** | The independent guarantee. **Must refuse an over-ceiling command in hardware**, not trust software |
| 11 | **Chemical injector / proportioner** | `chemical_mix_ratio` per zone, ground-side |
| 12 | **DI water stage** | Solar is DI-only, non-negotiable |
| 13 | **Hose reel + tether management** | The unglamorous part that decides whether a job takes 4 hours or 6 |
| 14 | **Containment / recovery** | Regulated discharge in California (`FIELD_OPERATIONS.md` §1.3) |

### 3.3 Software — what already exists

| Layer | Status |
|---|---|
| Mission + actuator emission | ✅ `execution/mavlink_mission.py` — already the standard PX4 pattern |
| Per-surface prescription + safety gate | ✅ `planning/`, `safety/` |
| Per-face grime layer | ✅ `fusion/scan_pipeline.py` |
| MAVSDK connection | ⚠️ documented seam in `mavlink_transport.py` |
| **Onboard AuterionOS app** | ❌ **the new build** — and the differentiator (`PLATFORM_VENDOR_CHOICE.md` §1) |
| Ground pump controller | ❌ new, and buildable on a bench today |

---

## 3.4 ⭐ Where the add-ons actually come from: the agricultural sprayer ecosystem

This is the answer to "what add-ons," and it is a different industry than the one we were looking in.

**We were shopping in *facade cleaning*, which is a high-pressure industry. We should be shopping
in *agricultural spraying*, which is a low-pressure, high-flow, open-architecture industry.**

Why it fits, point for point:

| Ag sprayer property | Why it matches us |
|---|---|
| **Low pressure by design** | Ag spraying is a few bar — the same class as our 1.8–7 bar table |
| **Airframe-agnostic components** | Sold as pumps, nozzles, valves and flow sensors, **not** as a kit welded to one drone model |
| **Native flight-stack support** | **ArduPilot ships a Sprayer library** (ArduCopter 4.0+); PX4 treats sprayers as generic MAVLink actuators. Pump control is a first-class citizen, not a hack |
| **Mature and cheap** | Brushless IP67 pumps, diaphragm pumps, Y-nozzles, centrifugal and pressure nozzles, quick-connect fittings, anti-drip control — commodity parts |
| ⭐ **Ground-speed-compensated flow** | Ag spray controllers already **govern pump speed in real time from GPS ground speed to hold a constant application rate** |

### That last row is the important one

Ag controllers solve — in shipping hardware — the problem of applying a **uniform dose while the
aircraft's speed varies**. That is exactly what `planning/coverage_path.py` needs: our
`traverse_speed_mps` and `dwell_seconds` only produce an even clean if delivered volume tracks
actual ground speed, not commanded speed.

**We were going to have to build that. We can adopt it instead**, and spend the effort on the
per-surface prescription that nobody else has.

### The synthesis with a ground tether

An onboard ag pump is ~5 L/min (~1.3 gpm) — fine for chemicals, **thin for rinsing a building**.
But we are not carrying a pump:

- **Volume comes from the ground pump** over the tether — 4–8 gpm, commodity soft-wash equipment.
- **The airborne parts reduce to ag components**: a valve, a nozzle (or the IHM selector), and a
  flow sensor for closing the loop.
- **The ag control logic moves to the ground controller**, where it modulates the regulator.

**Airborne bill of materials, final: a gun, a hose, a valve, a nozzle, a flow sensor, a
rangefinder, a small computer.** Every one of those is off-the-shelf, and none of them is a
bespoke integration with a Chinese facade-cleaning vendor.

---

## 4. Why this beats buying a cleaning drone

| | Buy a cleaning drone (Sherpa / Foxtech kit) | Bare drone + our add-ons |
|---|---|---|
| Pressure range | Fixed at the vendor's design point | **Matched to our surface table** |
| Our code in the loop | ❌ / limited | ✅ onboard app + ground controller |
| Pressure IP | Vendor's | **Ours, on ground equipment we own** |
| Airframe swappable | ❌ | ✅ any Auterion aircraft |
| Vendor can cut us off | ✅ | ❌ |
| Airworthiness | Vendor's | **Ours** ⚠️ |
| Time to first clean | Weeks | Months |

The last two rows are the honest cost. **You are trading speed and vendor-backed airworthiness for
control and differentiation.** Given `GO_NO_GO.md` concluded the services layer is commoditising
and the intelligence layer is the business, that is the right trade — but it is a real trade.

---

## 5. Sequence — capital last

| Step | Cost | Proves | Aircraft needed? |
|---|---|---|---|
| 1 | **Ground rig**: pump + regulator + gun on a stand | low four figures | Per-surface pressure control + firmware ceiling. **The core IP.** | ❌ |
| 2 | **Auterion Skynode Developer Program + Virtual Skynode** | subscription | Onboard app, flown against the reference house in simulation | ❌ |
| 3 | **Scan-only revenue** with the Autel | Autel only | That anyone pays for the intelligence | ❌ |
| 4 | **Vendor quotes** — Freefly, Watts, Inspired Flight | free | Who supports a liquid spray payload at all | ❌ |
| 5 | **Buy the Alta X and integrate** | ~$45K + integration | The whole loop | ✅ |

**Steps 1–4 need no aircraft.** If step 3 fails, you spent a few thousand dollars and a
subscription — not forty-five thousand and an integration programme.

---

## 6. Questions that must be answered before capital

**To Freefly (and Watts, and Inspired Flight):**
1. Warranty and airworthiness position on a **customer-integrated liquid spray payload**? ⚠️ *This
   is the disqualifying question.*
2. AuterionOS version, and will you support a third-party onboard app?
3. Payload-bay power budget, actuator outputs available, and Ethernet spec?
4. Real endurance **with a tether attached and a gun running** — not the datasheet payload figure?

**To Auterion:**
5. Skynode Developer Program cost, terms, and **commercial-product licensing**?
6. Does the app sandbox permit **actuator/payload commanding**, or only motion commands?

**To Foxtech / EAUAV:**
7. Will you supply **gun, gimbal mount and hose as components**, decoupled from DJI — and do you
   have anything in the **soft-wash (< 20 bar) range** rather than high-pressure?

**To counsel:**
8. Does a **Chinese-manufactured payload on a US NDAA airframe** preserve federal-contract
   eligibility? ⚠️ This may rule out Foxtech and EAUAV entirely.

**To an insurer:**
9. Premium for a **self-integrated spray drone** versus a vendor-supported one? *Still the number
   most likely to decide this, and still unasked.*

> `TODO(PROPWASH): needs Kevin + Freefly + Auterion + counsel + insurer before capital.`

---

## 7. One-line summary

**Freefly Alta X Gen2 (NDAA) on Auterion, with a soft-wash gun on a ground tether — not a Foxtech
high-pressure kit, because we prescribe 1.8–7 bar and they build 110–200 bar.**
