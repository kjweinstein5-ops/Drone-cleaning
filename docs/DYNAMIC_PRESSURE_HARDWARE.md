# PROPWASH — Dynamic Pressure Control Hardware

> ⚠️ **Not legal advice.** Patent strategy, hardware regulation (FAA, EPA, OSHA), and
> product-liability law require licensed counsel. This document tells you what to think about
> before engaging them.

---

## 0. The short answer

**Yes, such devices exist — but they are generic, not cleaning-drone-aware.**
No product on the market closes the loop between a *computer-vision/thermal inspection result*
and a servo-controlled pressure regulator on a drone-mounted spray system.
That gap is PROPWASH's hardware IP opportunity.

---

## 1. What exists today (the competitive baseline)

### 1a. General-purpose electronic pressure regulators (EPRs)

Electronic pressure regulators replace a manual pressure knob with a signal-driven valve.
Common examples:

| Manufacturer | Product | Pressure range | Control interface |
|---|---|---|---|
| Proportion-Air | QB1/QB2 series | 0–210 bar | 0–10 V, 4–20 mA, or serial |
| Marsh Bellofram | 900 series | 0–10 bar | 0–10 V / 4–20 mA |
| Bürkert | 2832 / 2872 | 0–20 bar | CAN, IO-Link, 0–10 V |
| Clippard | EV series | 0–7 bar | PWM, 0–10 V |
| SMC | ITV series | 0–9 bar | 0–10 V, RS-485 |

**What they do:** Accept an analog voltage or digital command and hold a set pressure.
**What they don't do:** Know anything about surfaces, grime, solar panels, or whether the
last zone passed verification. They are dumb actuators waiting for a setpoint.

### 1b. Agricultural spray drones (closest analogue)

DJI Agras T40, XAG P100, and similar use electronically-controlled pump motors and
flow controllers to vary application rate across a field (variable-rate application, VRA).
These adjust **flow rate / volume**, not **pressure ceiling**, and they respond to
pre-loaded prescription maps — not to a live AI feedback loop.

**The key difference:** ag drones don't verify the *result* and adjust parameters in
response. They execute a static map. PROPWASH verifies and re-queues with pressure delta.

### 1c. Industrial pressure-washing systems

Hotsy, Karcher, and others sell PWM-controlled pump bypass valves for commercial rigs.
These are ground-mounted, require 240V, and have no drone form factor.

### 1d. Lucid Bots Sherpa

The Sherpa uses an onboard chemical tank with a variable-speed pump motor.
**No confirmed software-addressable pressure API exists** (CLAUDE.md §7).
The operator adjusts pressure via the controller. That manual step is precisely what
the device described in this document would automate.

---

## 2. The device PROPWASH could build — the PROPWASH PSM

**Name (working):** PROPWASH Pressure-Set Module (PSM)

### What it is

A lightweight, drone-mountable electronics module that:

1. **Receives a target pressure setpoint** from the PROPWASH orchestrator (Tier 2) over
   a serial or CAN bus (not from an AI agent directly — the safety layer validates
   the setpoint first; see §4).
2. **Drives an electronic pressure regulator** (EPR) on the spray line between the pump
   and nozzle, holding actual pressure within ±0.1 bar of the setpoint.
3. **Reads actual line pressure** from a piezoelectric sensor at the nozzle manifold
   and streams it back to the orchestrator as telemetry.
4. **Enforces a hard pressure ceiling in firmware** — a per-surface-type limit that
   **cannot be overridden by any software command**, even a malformed one from the
   orchestrator. Solar ceiling: 2.0 bar. This is a firmware constant, not a config
   value. This is the device's core safety invariant.
5. **Has a physical pilot override button** on the controller that instantly drops
   pressure to idle and locks out the EPR until the pilot re-arms it.

### Key components (BOM sketch)

| Component | Function | Off-the-shelf path |
|---|---|---|
| Miniature EPR | Hold line pressure to setpoint | SMC ITV0010 (0–1 MPa, 50 g) or Proportion-Air QB1 |
| Piezo pressure sensor | Measure actual nozzle line pressure | Honeywell MLH series |
| Microcontroller | Safety logic, PID loop, CAN/serial bridge | STM32G0 or RP2040 (50–100 g) |
| CAN transceiver | Isolated bus to orchestrator | MCP2562FD |
| Relay/mechanical shutoff | Pilot override — cuts pressure to zero | Latching relay |
| Enclosure | Dust/water ingress, vibration | IP65 ABS + vibration mounts |
| Total weight target | | < 250 g (including EPR) |

### Weight reality check

The Sherpa carries ~10 kg of liquid plus spray hardware already. 250 g of electronics
is well within practical payload margin. Confirm with Lucid's payload specs before
committing to a specific target.

---

## 3. What makes this protectable IP

### 3a. Utility patent — the method

The combination that is novel and non-obvious:

> **"A method of drone-borne surface cleaning comprising: sensing a surface zone with a
> thermal and visual imaging sensor; computing a residual-grime proxy score from said
> sensing; comparing said proxy score to a verification threshold; and, on failure,
> automatically commanding an electronic pressure regulator mounted on the spray drone
> to apply a prescribed pressure delta to a subsequent cleaning pass of said zone —
> wherein the pressure command is validated against a per-surface-type hard ceiling
> stored in regulator firmware before actuation."**

The core claim: **closed-loop, verification-driven, per-surface-aware pressure
adjustment via an onboard EPR on a spray drone.**

This is the same method patent discussed in `IP_PROTECTION.md` (§5), but now with a
hardware component that strengthens the claim — because you are not just describing
a software method, you are describing a specific hardware+software system that
*physically enforces* the prescribed pressure. Harder to design around.

Additional dependent claims to layer in with counsel:

- Firmware-enforced hard ceiling per surface type (solar, glass, stucco, etc.)
- Pilot physical override with lockout logic
- Telemetry streaming of actual vs. prescribed pressure for post-hoc deviation logging
- The specific combination of EPR + piezo feedback + CAN bus on a tethered spray drone

### 3b. Trade secrets (keep these out of patent claims)

- The specific PID tuning parameters for pressure control under drone vibration
- The calibrated pressure-to-result lookup table that PROPWASH builds from field data
  (how much pressure delta is actually needed to re-clean a stucco wall vs. a clay tile)
- The firmware constants for each surface-type ceiling (beyond what patents require)
- Any novel vibration-compensation algorithm you develop for the EPR under drone flight

These are the brain. Patent the mechanism; keep the calibration as trade secret.

### 3c. Industrial design / trademark

- The physical form factor of the PSM module (IP65 enclosure, mounting bracket design)
  can be protected as a design patent or trade dress once you have a production design.
- `PROPWASH PSM` or a variant could be trademarked as a hardware product sub-brand.

---

## 4. How PSM fits the PROPWASH architecture

```
PROPWASH orchestrator (Tier 2, ~1 Hz)
        │
        │  validated setpoint (already safety-gated by SafetyChecker)
        ▼
   PSM firmware (Tier 1 — NOT Tier 3)
   ┌────────────────────────────────────┐
   │ 1. Accept setpoint from Tier 2     │
   │ 2. Check vs. hard firmware ceiling │  ← cannot be bypassed by any software
   │ 3. Run PID loop → drive EPR        │
   │ 4. Stream actual pressure back     │
   │ 5. Pilot override → drop to idle   │
   └────────────────────────────────────┘
        │
        ▼
   Electronic pressure regulator → nozzle line
```

**Critical:** The PSM sits at **Tier 1** (deterministic, safety-authoritative), not Tier 3.
Claude agents (Tier 3) prescribe a target pressure. The orchestrator (Tier 2) validates it
with `SafetyChecker`. Only then does the validated setpoint reach the PSM. The PSM's
firmware ceiling is the last hardware-level guarantee before liquid leaves the nozzle.

This tiered design is important for two reasons:
1. It matches CLAUDE.md §2 — agents never sit inside a safety loop.
2. It makes the safety claim in your patent and in conversations with Lucid / FAA
   bulletproof: even a software bug in the orchestrator **cannot cause over-pressure**
   because the hardware enforces the ceiling independently.

### What to add to `propwash/backend/safety/checks.py`

Add a check: `PSM_SETPOINT_EXCEEDS_FIRMWARE_CEILING` — when preparing a CAN message
for the PSM, confirm the setpoint ≤ the surface ceiling before the message is sent.
Belt-and-suspenders: firmware also checks, but the orchestrator should never send an
invalid setpoint in the first place.

---

## 5. The product business case — selling PSM to other operators

### Who buys it

- Lucid Bots Sherpa operators who are not PROPWASH customers but want closed-loop
  pressure control for their own cleaning workflows
- Other commercial drone cleaning operators (not limited to Lucid hardware — any spray
  drone with an accessible pump line)
- Industrial inspection + cleaning service companies (bridges, cell towers, tanks)
- Potentially: rooftop solar O&M companies (large-scale utility solar farms need
  automated cleaning; this is a $1B+ global market)

### Revenue model for PSM hardware

This becomes a **hardware product line** — separate from PROPWASH's service revenue.
Illustrative unit economics (validate before committing):

| Item | Estimate |
|---|---|
| BOM + manufacturing (contract manufacturer) | $400–600/unit |
| Target ASP | $1,800–2,500/unit |
| Gross margin | ~65–70% |
| Annual recurring: firmware updates / calibration subscription | $300–500/unit/yr |

A fleet of 100 PSM units at $2,000 ASP + $400/year = $200K hardware + $40K ARR.
Not the core business — but meaningful margin and a data-collection surface for
improving your own calibration tables.

### The strategic reason to build it even if you don't sell many

Every PSM unit sold creates a data-collection endpoint: actual nozzle pressure vs.
prescribed pressure vs. verification result. That telemetry, aggregated across many
operators, accelerates PROPWASH's learning model faster than your own fleet alone.
This is the data flywheel extended to hardware.

**Important:** If you collect data from third-party PSM units, your customer contracts
for PSM must secure your right to use that telemetry for model improvement — same
principle as your service contracts (IP_PROTECTION.md §7).

---

## 6. Regulatory considerations before building hardware

- **FAA:** Adding electronics to a certificated drone is a **modification**. Under Part 107,
  this may require the operator to re-declare airworthiness. Work with Lucid to understand
  whether the PSM can be installed as an accessory within their airworthiness envelope,
  or whether you need to operate on hardware you own outright (Path C territory, §7).
- **EPA/state chemical applicator laws:** Varying spray pressure affects pesticide and
  chemical application rates. In some states, commercial chemical application is regulated.
  For DI water / degreaser on building exteriors this is typically low-risk, but verify
  with counsel for your California market.
- **UL/CE listing:** If you sell PSM as a product in commerce, you'll likely need UL
  recognition (US) or CE marking (EU). Factor this into your cost model. Budget $15–50K
  and 6–12 months for initial listing.
- **Product liability:** Hardware that controls pressure on a flying vehicle creates product
  liability exposure. Make sure the firmware-enforced ceiling and pilot override are
  documented, tested, and provable in court. Keep test logs.

---

## 7. Build roadmap for PSM

### Phase 1 — Proof of concept (no drone required)
1. Buy an SMC ITV0010 EPR + piezo sensor + STM32 dev board.
2. Write firmware: receive setpoint via serial, run PID, stream actual pressure.
3. Validate pressure accuracy on a bench test rig (garden hose + pressure gauge).
4. Document the firmware hard-ceiling behavior with test logs — this is your IP evidence.

**Estimated cost:** ~$800 in parts. Timeline: 4–6 weeks (part-time).

### Phase 2 — Drone integration
1. Work with Lucid (or on hardware you own) to tap the Sherpa spray line.
2. Mount PSM prototype, connect to a laptop running the orchestrator.
3. Run `sim/scenario.py` with `PSMTransport` (a new adapter) instead of `MockTransport`.
4. Fly controlled tests: did actual pressure match setpoint within ±0.1 bar under vibration?

### Phase 3 — Miniaturization + enclosure
1. Contract a PCB layout shop to consolidate the prototype onto a 50×50mm board.
2. Design an IP65 enclosure + Sherpa-compatible mounting bracket.
3. Send to a contract manufacturer (JLCPCB, Tempo Automation) for small run (10–25 units).

### Phase 4 — Patent + product launch
1. File the provisional **before** any public demo of the PSM (§5 of IP_PROTECTION.md).
2. Launch to beta operators. Collect telemetry data.
3. Convert provisional to utility within 12 months.

---

## 8. What to do this quarter

1. **Buy the bench parts** (SMC ITV0010 or equivalent, STM32 Nucleo board, pressure sensor)
   and validate the PID loop on a test rig. This creates tangible, dated invention evidence.
2. **Add `PSMTransport`** as a new execution adapter in `propwash/backend/execution/` behind
   a feature flag (`PROPWASH_ENABLE_PSM=true`). Mirror the `CompanionTransport` pattern.
3. **Talk to a patent attorney** about adding a hardware claim to the provisional — the EPR
   + firmware ceiling + pilot override combination strengthens the method patent significantly.
4. **Ask Lucid directly** (in the outreach call, `docs/LUCID_OUTREACH.md`) whether PSM can
   be accessory-installed within their airworthiness framework, or whether you need to run
   it only on hardware you own.

---

## 9. Mental model

```
Patent the mechanism (EPR + feedback loop + firmware ceiling + pilot override).
Keep the calibration tables secret (what pressure delta fixes what surface — that's your data moat).
Sell the hardware to create more data endpoints.
Use the data to widen your calibration advantage over anyone who tries to copy you.
```

The PSM is not just a product — it is a *data-collection terminal* that accelerates the
flywheel described in `IP_PROTECTION.md §3`. Every unit sold by a third-party operator
is another sensor reporting back to PROPWASH's learning model.
