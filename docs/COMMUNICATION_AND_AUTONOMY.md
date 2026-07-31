# Deep Dive — Communication Architecture & the Autonomy Ladder

> How the two drones and PROPWASH actually talk, what happens when links fail, and how much
> autonomy is legally reachable — now and under the FAA's proposed **Part 108**.
>
> ⚠️ Regulatory content is **not legal advice** and Part 108 is a **proposed rule, not law**
> (NPRM comment period closed Feb 2026; final rule pending). Verify with an aviation attorney
> before operating on any assumption here.

---

## 0. The headline finding

**The FAA's proposed Part 108 would make BVLOS operations run *autonomously on pre-programmed
flight paths*, and would let a single "Flight Coordinator" supervise *multiple aircraft*.**

Read that against what we've built: `planning/coverage_path.py` **already generates
pre-programmed flight paths**, and `execution/mavlink_mission.py` **already translates them into
uploadable missions**. If Part 108 lands substantially as proposed, PROPWASH's architecture is
pointed directly at the regime the regulation creates — and the labor model in
`SCALING_TO_10M.md` (1 pilot per crew) becomes conservative.

**This is a tailwind, not a pivot.** But it is *proposed*, so plan for Part 107 today and
build so Part 108 is an unlock, not a rewrite.

---

## 1. The communication architecture (three independent links)

A common mistake is imagining one "connection." There are **three**, with different
requirements, and conflating them is how systems fail badly.

| Link | Carries | Rate | Loss tolerance |
|---|---|---|---|
| **C2 (command & control)** | flight commands, RC, heartbeat | 10–50 Hz | ❌ **Zero** — loss triggers failsafe |
| **Payload/telemetry** | pump/nozzle setpoints, actual pressure, position | 1–10 Hz | ⚠️ Low — degrade to safe state |
| **Data/imagery** | thermal + RGB frames, point clouds | bulk, offline | ✅ **High** — can be post-flight |

### Why our loose-sync design is architecturally right (CLAUDE.md §6)
The scout and cleaner **never talk to each other** — they sync through *the plan*. That means:
- No real-time cross-aircraft link to fail.
- Survey data moves as **bulk transfer** (Link 3), where latency is irrelevant.
- The cleaner only needs Links 1–2, both local to its own operation.

This is the difference between a system that degrades gracefully and one that has a
single point of catastrophic failure. It was the right call and this research confirms it.

### Bandwidth reality
- **Telemetry** is tiny (KB/s) — real-time is easy.
- **Imagery is enormous.** A survey is GBs of thermal + RGB. Do **not** design for live
  streaming of survey data to the cloud; **process locally** (Mac Studio, `decisions/
  COMPUTE_INFRASTRUCTURE.md`), transfer in bulk. This also protects the data moat.

---

## 2. Latency budget — which decisions can live where

Latency is what determines *where* a decision is allowed to run. Map it to CLAUDE.md §2 tiers:

| Tier | Decision | Budget | Where it MUST run |
|---|---|---|---|
| 0 | Flight stabilization | 2–20 ms | **On the flight controller.** Never us. |
| 1 | Collision avoid, geofence, pressure ceiling, **human-presence halt** | 30–100 ms | **On-aircraft / companion computer** — local, deterministic |
| 2 | Zone sequencing, work-order dispatch | ~1 s | Ground station / backend |
| 3 | Claude agents — planning, prescription, verification reasoning | seconds | Cloud; **advisory only** |

**The rule this enforces:** anything safety-critical must run where a dropped link cannot
delay it. That's why the safety layer is local and deterministic, and why Tier-3 agents are
advisory. A cloud round-trip (100–500 ms, unbounded on failure) is **categorically unsafe** for
a Tier-1 decision — this is the engineering reason behind the architectural rule, not just
policy.

---

## 3. Link failure — the failsafe ladder (the part that actually matters)

Design for the link failing, because it will. PX4 provides the mechanisms; we define policy.

| Failure | Detection | Required response |
|---|---|---|
| **Companion computer dies** | heartbeat timeout | **Pump OFF**, hold/return; flight controller unaffected (Tier 0 independent) |
| **C2 link lost** | RC/GCS timeout | PX4 failsafe: hold → RTL → land. **Pump OFF first.** |
| **Payload link lost** | setpoint stream stops | **PSM firmware fails to idle** — the independent hardware guarantee |
| **Offboard setpoint stream stops** | PX4 requires continuous stream | PX4 auto-exits Offboard → failsafe mode |
| **GPS degraded** | fix quality | Abort spray; no position = no valid coverage path |
| **Human detected mid-pass** | Tier-1 thermal check | **Immediate pump OFF + halt** (`safety/human_detection.py`) |

### The invariant to hold everywhere
> **Any communication failure results in the pump going OFF and the aircraft entering a safe
> state. There is no failure mode in which spraying continues without positive control.**

Two independent mechanisms enforce this: (1) software failsafe policy, and (2) the **PSM
firmware ceiling + idle-on-signal-loss** (`DYNAMIC_PRESSURE_HARDWARE.md` §4). Defense in depth
— a software bug alone cannot cause uncontrolled spray.

**Build implication:** `mavlink_mission.py` already forces **pump OFF at the end of every
zone**. Extend that to a heartbeat/watchdog when the live transport is implemented.

---

## 4. The autonomy ladder — what's reachable, in order

Not binary. Five rungs, increasing capability *and* regulatory burden:

| Rung | Capability | Regulatory status | PROPWASH |
|---|---|---|---|
| **0** | Manual flight, manual spray | Part 107 today | Sherpa today |
| **1** | **Operator flies; software guides + controls the payload** (pressure/nozzle by position) | **Part 107 — legal now**, operator in command | ⭐ **Our near-term target** |
| **2** | Software flies pre-programmed paths, VLOS, pilot supervising | Part 107 (+ possible waiver) | Achievable on open stack |
| **3** | BVLOS autonomous on pre-programmed paths | Part 107 **waiver** today → **Part 108** if finalized | Where the economics improve |
| **4** | One coordinator, **multiple aircraft** | **Part 108 proposal** (Flight Coordinator + SUI) | The scaling unlock |

### Rung 1 is the whole near-term game
**Payload autonomy is legal today** — the operator flies, our software sets pressure/nozzle by
location. That's where the PSM/IHM IP lives, it needs no waiver, and it delivers most of the
value (consistent, prescription-accurate cleaning + verification). **Build rung 1 now; don't
wait on regulation.**

### What Part 108 would change (if finalized as proposed)
- Replaces today's case-by-case **Part 107 BVLOS waivers** with a standing framework.
- BVLOS conducted **autonomously on pre-programmed flight paths** — exactly our Stage-5 output.
- New roles: **Operations Supervisor** + **Flight Coordinator**; a coordinator may supervise
  **multiple aircraft** where manufacturer specs permit, with **Simplified User Interaction**
  reducing the human-in-the-loop burden.
- Shifts accountability toward the **organization**, not just the individual pilot.

**Business impact:** `SCALING_TO_10M.md` assumes one pilot per crew. Under rung 4, one
coordinator running several aircraft **breaks the linear labor↔revenue coupling** — the single
biggest constraint in the $10M model. Don't re-plan on it yet (proposed ≠ law), but note that
the current plan is the *conservative* case.

---

## 5. What to build now (so Part 108 is an unlock, not a rewrite)

1. **Rung 1, fully** — `MavlinkPayloadTransport` live: upload missions, drive
   ActuatorServos, read telemetry back. Operator flies. **No waiver needed.** ✅ translator done
2. **Watchdog/heartbeat** — pump OFF on any link or companion-computer timeout (§3).
3. **Keep Tier-1 local** — never let a safety decision depend on a cloud round-trip (§2).
4. **Keep the path machine-readable** — our `FlightPlan` → mission translation is already the
   artifact a Part 108 regime would want. Preserve that shape.
5. **Log everything** — Part 108 leans on organizational accountability; execution-vs-
   prescription logs and safety-event records become compliance evidence *and* feed the
   learning model. Dual-purpose.
6. **Track the rulemaking** — final rule pending. Revisit `SCALING_TO_10M.md` labor
   assumptions if rung 4 becomes real.

---

## 6. Open items
- [ ] Aviation attorney: current Part 107 posture + what a BVLOS waiver would require today.
- [ ] Confirm PX4 failsafe configuration matches the §3 ladder on the chosen airframe.
- [ ] Implement heartbeat/watchdog → pump-OFF in the live transport.
- [ ] Monitor Part 108 final rule; re-run the revenue model under a multi-aircraft coordinator.
- [ ] Confirm manufacturer specs on any platform re: multi-aircraft supervision (Part 108 gates
      this on "where manufacturer specifications permit").

## Sources
- [FAA Part 108 explained — Pilot Institute](https://pilotinstitute.com/part-108-explained/) · [Part 108 complete guide 2026 — UAVHQ](https://uavhq.com/blog/faa-part-108-complete-guide-bvlos-2026/) · [Part 108 vs Part 107 — DroneBundle](https://dronebundle.com/blog/part-108-vs-part-107)
- [New FAA BVLOS rules (Parts 108 & 146) — Skydio](https://www.skydio.com/blog/drones-faa-bvlos-waivers-new-rules) · [BVLOS: shift from waivers to Part 108 — Drone U](https://www.thedroneu.com/blog/bvlos-drone-operations-part-108/) · [Part 108 NPRM: what matters — DRONELIFE](https://dronelife.com/2025/08/08/matt-sloane-read-the-entire-faa-part-108-nprm-so-you-dont-have-to-heres-what-actually-matters/)
- [PX4 Offboard Mode](https://docs.px4.io/main/en/flight_modes/offboard) · [PX4 Companion Computers](https://docs.px4.io/main/en/companion_computer/)
