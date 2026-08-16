# Decision — which drone company, and how our stack gets inside it

> **Kevin:** *"It needs to be differentiated from any other company out there, and I need to
> integrate my tech stack into the drone. Lucid doesn't allow that."*
>
> Extends `INTEGRABLE_PLATFORM.md` with the vendor screen it said was still owed.
> Screened 2026-08-16.

---

## 0. The answer: don't pick a drone, pick the operating system

**Go with Auterion.** Then choose an airframe from the several NDAA manufacturers that already
run it.

This is the single most important decision in the document, and it is not the one that was being
asked. "Which drone company" is the wrong frame — it is how you end up locked to a vendor again,
which is exactly the Lucid problem.

**AuterionOS lets you run your own application *on the aircraft's mission computer*.** Not "send
it waypoints from the ground." Your code, on the drone, sandboxed as an add-on, built on ROS 2,
able to issue position/velocity/acceleration commands, read telemetry, and **interact with
external payloads**.

That is literally the request: *integrate our technology into the drone.*

And because **Freefly, Watts Innovations and others all build on Auterion**, you write the
integration **once** and the airframe becomes a commodity you can re-source. No vendor can
switch you off. That is the structural fix for what Lucid did to you.

**Recommended first aircraft: Freefly Alta X Gen2 (NDAA).** Reasoning in §3 — but note the
airframe is now the *replaceable* part of the decision, which is the point.

---

## 1. What "integrate my stack into the drone" actually requires

Four levels, increasing depth. Lucid gives you level 0. Most vendors stop at level 2.

| Level | What it means | Who offers it |
|---|---|---|
| 0 — **Work order** | Hand a human a job sheet | Lucid (Path A) |
| 1 — **Mission upload** | Push waypoints and speeds to the aircraft | Most enterprise drones, DJI included |
| 2 — **Payload control** | Command a pump/servo as an actuator mid-mission | Any PX4/ArduPilot airframe |
| 3 — **Onboard application** ⭐ | **Your software runs on the aircraft**, reads telemetry, commands motion, drives payloads, closes a loop in flight | **AuterionOS apps via Auterion SDK** |

Level 2 is where `execution/mavlink_mission.py` sits today, and it is enough to fly a
prescription. **Level 3 is where the differentiation lives**, because it is the only level at
which the aircraft can *react to what it is seeing while it is spraying*.

### Why level 3 is the actual moat

Everything in the repo today is **open-loop within a pass**: scan, decide, fly the plan, verify
afterwards. Every competitor could eventually do that.

With an onboard app you get **closed-loop within the pass**:

- adjust standoff or traverse speed when the live thermal says a patch is heavier than the plan
  assumed;
- hold a pass longer on a zone that isn't responding, instead of discovering it at verification;
- abort a zone the instant a surface reads wrong — before damage, not after.

**Nobody in exterior cleaning is doing in-flight adaptive treatment.** Not Lucid, not the 18
regional operators, not the PV inspection platforms. That is a defensible claim, and unlike
"we detect soiling" (which `GO_NO_GO.md` §1.4 showed is commoditised) it is not already shipping
somewhere else.

---

## 2. The Auterion route in practice

| | |
|---|---|
| **Auterion SDK** | Build onboard software for AuterionOS vehicles. **Based on ROS 2.** Apps send acceleration / velocity / position commands and receive autopilot telemetry |
| **Third-party apps** | Explicitly supported: *"through common APIs, third-party software companies can develop AuterionOS applications that add use-case-specific capabilities"* |
| **Sandboxing** | Customer apps run as add-ons **in a safe sandbox within the mission computer** — Auterion manages the OS |
| **Access** | AuterionOS **2.7+** and a **Skynode Developer Program** subscription via Auterion Suite |
| **⭐ Virtual Skynode** | **A simulated Skynode. You can develop and test the onboard app with no aircraft at all.** |

### The sandbox is a feature, not a limitation

Read the sandbox against **CLAUDE.md §2**. Our own architectural rule says a Tier-3 agent must
never write a Tier-0 setpoint or suppress a Tier-1 check. Auterion **enforces that in the
platform**: our app is an add-on, the OS and flight control are Auterion's, and the separation is
structural rather than a promise in a design doc.

That is an easier story for an insurer, a customer and an FAA waiver application than "we
promise our code stays out of the flight loop."

### Virtual Skynode changes the sequencing

`INTEGRABLE_PLATFORM.md` §7 said: build the ground rig before buying a $45K aircraft. Virtual
Skynode extends that further —

> **You can build and test the onboard application before buying any aircraft, and before
> building the ground rig.**

Ground rig proves the *pressure* IP. Virtual Skynode proves the *onboard* IP. Neither needs an
airframe. **The capital decision moves to the end of the process, not the start.**

---

## 3. Airframe screen — all Auterion/PX4, all NDAA, all US-made

| | **Freefly Alta X Gen2** | **Watts PRISM Sky** | **Inspired Flight IF1200A** |
|---|---|---|---|
| Payload | **15.9 kg / 35 lb** ⭐ | 11.3 kg / 25 lb | 8 kg / 19.1 lb |
| Endurance | ~41.7 min @ 5 lb · ~20 min @ 20 lb | LTE-enabled, heavy-lift | **~43 min max** ⭐ |
| Flight stack | Skynode, **Auterion Enterprise PX4** | **Auterion ecosystem**, Pixhawk-based, ArduPilot **or** PX4 | **Open PX4 architecture** |
| Payload mounting | Smart Dovetail + internal bay: **Ethernet, regulated power, LTE** | **Rail system — top *or* bottom mounting**, quad or X8 coaxial ⭐ | **Universal Payload Interface** (M600-compatible spacing) |
| Compliance | NDAA; **Blue List in process** | NDAA, US-made (Baltimore) | **Blue UAS *and* Green UAS dual-certified** ⭐ |
| Price | **~$45,000** | quote | quote |

### How to read that table

- **Alta X — most payload, best documented integration path.** The internal bay with Ethernet,
  regulated power and LTE is purpose-built for a companion computer, and Freefly explicitly
  documents MAVSDK control "from the ground via radio, or onboard via an expansion computer."
  **Recommended first aircraft.**
- **PRISM Sky — most mechanically flexible.** Rail mounting top *or* bottom and a
  quad/X8-coaxial choice matters for a spray system, where nozzle geometry and hose routing fight
  the airframe. Worth a serious quote.
- **IF1200A — best compliance posture, least payload.** Blue *and* Green certified is the
  strongest position for institutional and federally funded work — which `GO_NO_GO.md` argued is
  the segment to target. 8 kg is thin for spray, **but with tethered water you are carrying a
  ~1.2 kg gun and hose, not a tank.** Do not rule it out on payload alone.

**Nobody should buy on this table.** Send all three the §1.0 questionnaire, and add the two
questions this document exists to ask:

1. *Do you run AuterionOS, at what version, and will you support a third-party onboard app?*
2. *What is your position — warranty and airworthiness — on a customer-integrated **liquid spray**
   payload?*

Question 2 is the one that will actually disqualify vendors. Water, electronics and rotors is a
different conversation from a camera gimbal, and a vendor who says no to it is a dead end no
matter how good the SDK is.

---

## 4. The full stack, end to end

```
  Autel 4T V2 scan
        │
        ▼
  Photogrammetry + our fusion  ──▶  per-face surface + grime layer     [Tier 3, ground]
        │
        ▼
  Supervisor  ──▶  per-zone prescription, safety-gated                 [Tier 3, ground]
        │
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │  OUR ONBOARD APP  (AuterionOS add-on, ROS 2, sandboxed)          │  ⭐ the new part
  │   · executes the zone plan                                      │
  │   · reads live telemetry + payload sensing                      │
  │   · adapts standoff / speed / dwell WITHIN the pass             │
  │   · commands nozzle select + pump on/off                        │
  │   · aborts a zone on an unexpected surface reading              │
  └─────────────────────────────────────────────────────────────────┘
        │                                    │
        ▼                                    ▼
  Auterion flight control              GROUND PUMP + regulator        [Tier 0/1 — theirs]
  (untouched, sandboxed away)          = the PSM, pressure IP          [ours, not flying]
        │
        ▼
  Post-clean verification ──▶ PASS / re-queue ──▶ learning
```

Two things to notice:

1. **The pressure intelligence never flies** (`INTEGRABLE_PLATFORM.md` §4). It lives on a ground
   pump we own outright. The aircraft only selects a nozzle and toggles a pump.
2. **The flight controller is never touched.** The sandbox guarantees it. We modulate fluid and
   request motion; we do not stabilise the vehicle.

---

## 5. Why this is genuinely differentiated

| Layer | Anyone can copy? | Ours |
|---|---|---|
| Buy a cleaning drone | ✅ trivially — Lucid has ~1,000 deployed | — |
| Detect soiling from thermal/RGB | ✅ ships in PV inspection software today | — |
| Plan a coverage path | ✅ standard mission planning | — |
| **Per-surface prescription with hard safety ceilings** | ⚠️ needs the surface model + calibration data | ✅ |
| **Tamper-evident audit of what pressure touched what material** | ⚠️ nobody has built it | ✅ |
| **In-flight adaptive treatment from live sensing** | ❌ **nobody in cleaning is doing this** | ✅ level 3 |
| **Verification-driven parameter learning across jobs** | ❌ needs the deviation log, which compounds | ✅ |

The bottom four rows are the company. The top three are table stakes that a competitor buys with
a purchase order.

**And the moat compounds in the right direction:** every job feeds the deviation log, which tunes
the surface table, which makes the next prescription better. A competitor starting two years
later doesn't just lack the code — they lack the data.

---

## 6. Sequence — capital last

| Step | Cost | Proves |
|---|---|---|
| 1. **Skynode Developer Program + Virtual Skynode.** Port the Tier-2 executor to an AuterionOS app; fly the reference house in simulation | subscription only | The onboard app works. **No aircraft.** |
| 2. **Ground rig** — pump, electronic regulator, gun on a stand | low four figures | The pressure control loop + safety ceiling. **No aircraft.** |
| 3. **Quote all three vendors** on the two questions in §3 | free | Who will actually support a spray integration |
| 4. **Scan-only revenue** in parallel (`GO_NO_GO.md` §3) | Autel only | That anyone pays for the intelligence |
| 5. **Buy one airframe** and integrate | ~$45K + integration | The whole thing |

**Steps 1, 2 and 4 all happen before any airframe purchase.** If step 4 fails, you have spent a
subscription and a few thousand dollars, not forty-five plus an integration programme.

---

## 7. Open questions — ask before committing

- [ ] **Skynode Developer Program: cost, terms, and commercial-product licensing.** Can we ship a
      commercial product built on it, and on what royalty or licence basis?
- [ ] **Will Freefly / Watts / Inspired Flight support a liquid spray payload?** Warranty and
      airworthiness position. **This is the disqualifying question.**
- [ ] **Does the sandbox permit the actuator control we need**, or only motion commands? The docs
      say apps "interact with external payloads" — confirm that includes commanding a servo/relay.
- [ ] **Real endurance with tether and gun running** — not the datasheet payload figure.
- [ ] **Insurance for a self-integrated spray drone** versus a vendor-supported one. Still the
      number most likely to decide this, and still unasked.
- [ ] **Auterion's own roadmap** — if Auterion or a partner ships cleaning-specific capability,
      the same commoditisation that hit soiling detection hits us.

> `TODO(PROPWASH): needs Kevin + Auterion + airframe vendors + insurer before capital.`
