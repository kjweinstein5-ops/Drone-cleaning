# Decision — an airframe we can actually integrate into (non-Lucid)

> **Kevin's requirement:** stop building on Lucid. Own an airframe our tech can drive directly.
>
> **Supersedes the platform recommendation in `CLEANING_DRONE_PLATFORM.md`.** That doc
> recommended "DJI M350/M400 + Foxtech AeroClean, ~$25–45K" as the own-the-stack route.
> **That route is now largely closed** (§1). Screened 2026-08-16.

---

## 0. The recommendation, up front

**Freefly Alta X Gen2 (NDAA) + tethered water + ground-side pressure control.**

Three reasons, in order of importance:

1. It runs **Auterion Enterprise PX4 on a Skynode** and is **controllable via MAVSDK** — from the
   ground radio *or* from a companion computer in its own payload bay. That is exactly the
   interface `execution/mavlink_mission.py` already emits against.
2. It is **US-made and NDAA-compliant** (Blue List in process), which the DJI path no longer is.
3. With **tethered water, the hard part stops flying** (§4) — the pressure intelligence moves to
   the ground, where we control it completely and where it is not a flight-safety function.

**~$45,000 airframe.** More than a Sherpa's assumed cost, and worth it, because it is the only
configuration where the IP in this repo can actually run.

---

## 1. ⚠️ The DJI path closed in December 2025

Our earlier recommendation assumed DJI M350/M400 + a Foxtech AeroClean kit. Current status:

| Fact | Consequence |
|---|---|
| DJI is on the **FCC Covered List**. On 21 Dec 2025 a White House interagency body issued an affirmative national-security determination; the FCC implemented it the next day | **New models cannot receive FCC equipment authorisation, so they cannot be legally imported or sold in the US** |
| Existing airframes stay legal to own and fly; firmware/security updates committed to **1 Jan 2029** | An existing fleet keeps working — but you cannot *grow* one |
| US retail stock is **depleting and not being replenished** | Sourcing risk on every additional aircraft |
| From 22 Dec 2025, federal contractors **may not use drones from covered foreign entities on federally funded contracts** | **Municipal, school-district, port, military-adjacent and federally funded commercial work is off the table** |

**Read that last row against `GO_NO_GO.md`:** we just concluded the business should re-aim at
*commercial and institutional* customers. Institutional buyers are exactly the ones with federal
funding threads. Building on DJI would foreclose the segment we just decided to target.

**Foxtech's AeroClean kits are excellent hardware but built around DJI mounting, power and
comms** — AeroClean P3 (T50) and T-M400C are specified for M350/M400. The kit is not the problem;
the aircraft under it is.

---

## 2. Why Alta X fits what we already wrote

`execution/mavlink_mission.py` translates a `FlightPlan` into MAVLink mission items plus
`ActuatorServos` setpoints for pump / pressure / nozzle. That was written speculatively. It turns
out to be exactly right:

- **PX4 documents sprayers as generic actuators controlled over MAVLink** — pump activate/
  deactivate, and where the hardware supports it, flow rate and nozzle shape. Our channel model
  (`PUMP_CHANNEL`, `PRESSURE_CHANNEL`, `NOZZLE_CHANNEL`, normalised to [-1, 1]) is the standard
  PX4 pattern, not an invention.
- **MAVSDK is the recommended MAVLink API for PX4** and is what Freefly documents for Alta X:
  *"control of Alta with custom MAVSDK API software, from the ground via radio, or onboard via
  an expansion computer."*
- The Alta X **internal payload bay provides Ethernet, regulated power and LTE** — a home for a
  companion computer running our Tier-2 orchestrator, with a backhaul for telemetry.

### Specifications that matter operationally

| | Alta X Gen2 |
|---|---|
| Payload | **15.9 kg / 35 lb** |
| Endurance | ~41.7 min @ 5 lb · **~20 min @ 20 lb** |
| Flight stack | Skynode, **Auterion Enterprise PX4** |
| Control API | **MAVSDK** (ground radio or onboard companion) |
| Price | **from ~$45,000** |
| NDAA | Airframe + Pilot Pro compliant. ⚠️ **The stock Herelink radio is NOT** — the NDAA variant swaps in a Doodle Labs link. **Buy the NDAA SKU, not the standard one.** |

**Cross-check against `FIELD_OPERATIONS.md` §5.1:** 114 min of spray time at ~20 min endurance is
~6 flights and ~5 swaps (+15 min). At a lighter tethered payload, endurance improves. That is a
workable day — unlike an 8-minute untethered tank configuration.

---

## 3. Options considered

| Option | Integrable? | NDAA / sourcing | Verdict |
|---|---|---|---|
| **Freefly Alta X Gen2 (NDAA)** | ✅ PX4 + MAVSDK + payload bay w/ Ethernet, power, LTE | ✅ US-made, Blue List in process | ⭐ **Recommended** |
| Lucid Sherpa | ❌ No confirmed developer control API; autonomy kept in-house | ✅ | The thing we are moving away from |
| DJI M350/M400 + Foxtech AeroClean | ⚠️ PSDK payload dev only; flight control not open like PX4 | ❌ **Covered List — no new imports, federal-contract prohibition** | ❌ Closed (§1) |
| Full custom PX4/ArduPilot build (Pixhawk / Cube Orange+ / ARK) | ✅ Maximum control | ⚠️ Depends entirely on sourcing | Cheapest and most work. **No support, no warranty, and you own airworthiness.** Viable later, wrong for first aircraft |
| Apellix | ⚠️ Computer-controlled but vendor-closed | ✅ US | Industrial/tank market, not building façades |

**Not screened, worth checking before committing:** Watts Innovations, Inspired Flight, Harris
Aerial — other US NDAA heavy-lift builders. Ask each the same questionnaire
(`LAUNCH_PLAYBOOK.md` §1.0). Do not take this doc's single recommendation without quoting at
least two.

---

## 4. ⭐ The architectural insight: with a water tether, the hard part stops flying

This is the most important paragraph in the document.

`DYNAMIC_PRESSURE_HARDWARE.md` designs a **PSM** (electronic pressure module) and **IHM**
(motorised nozzle turret) as *airborne* payloads. That framing came from assuming an onboard tank.
**With tethered water, it is wrong — and wrong in our favour.**

In a tethered-water configuration:

- the **pump and pressure regulator sit on the ground**, not on the aircraft;
- the drone carries a **spray gun and hose** (Foxtech's is ~1.2 kg), not a tank and pump;
- so the aircraft needs only **pump on/off** and **nozzle selection** — two simple actuator
  channels — while **pressure is commanded ground-side**.

Three consequences, all good:

1. **Dramatically less airborne integration risk.** No high-pressure electronics on a flying
   vehicle, no weight penalty, no vibration/water-ingress qualification on the hard part.
2. **The pressure intelligence — the actual IP — runs on equipment we fully own and can change
   today**, without a vendor, an airframe integration, or an airworthiness argument. A ground
   pump with a VFD or electronic regulator, commanded by our orchestrator, *is* the PSM.
3. **It is clean under CLAUDE.md §2.** Commanding a ground pump is not a flight-safety function
   and touches no Tier-0 or Tier-1 loop. The aircraft's flight controller is untouched; we
   modulate the fluid, not the vehicle. That is the most defensible possible split.

**Practical read: we can build and validate the per-surface pressure control loop on a ground rig
with a spray gun on a stand — no aircraft at all — and prove the core IP before spending $45K.**

---

## 5. What integration actually requires

| Layer | Status | Work |
|---|---|---|
| Mission upload (waypoints, speeds) | ✅ `mavlink_mission.py` emits it | Wire MAVSDK connection — documented seam in `mavlink_transport.py` |
| Pump on/off | ✅ modelled as `ActuatorServos` | Map to a real PX4 actuator output; relay/solenoid on the gun |
| Nozzle selection (IHM) | ✅ modelled | Build the turret, or fly fixed nozzles and change by hand at first |
| **Pressure control (PSM)** | ✅ modelled | **Move to ground pump (§4).** Electronic regulator + our controller |
| Telemetry back | ⚠️ | MAVSDK telemetry → Tier-2 orchestrator; LTE in the payload bay |
| Safety gating | ✅ `safety/checks.py`, hard ceilings, audit log | Enforce ground-side too — the regulator must refuse an over-ceiling command in firmware |

**Nothing here requires a vendor's permission.** That is the whole point of leaving the Sherpa.

---

## 6. What this does NOT change

- **Part 107 still governs.** An open flight stack does not grant autonomy. Pre-programmed missions
  are already legal; VLOS (107.31) and multi-aircraft (107.35) still bind and are still waiverable
  (`REGULATORY_STRATEGY.md`, `WAIVER_107_35.md`). Owning the airframe changes the *software* story,
  not the *regulatory* one.
- **The operator stays in command** (CLAUDE.md §10).
- **Tier 0 is still untouchable.** We command payload actuators and upload missions. We do not
  write flight-stabilisation setpoints, and PX4 being open source is not a licence to start.
- **Airworthiness becomes ours.** On a Sherpa, the vendor owns the aircraft's integrity. Bolt a
  spray system to an Alta X and **we** own that integration, its failure modes and its liability.
  Budget for that — it is the real cost of the freedom, and it is not in the $45K.

---

## 7. Recommended sequence

1. **Build the ground rig first.** Pump + electronic regulator + gun on a stand. Prove per-surface
   pressure control and the safety ceiling with **zero aircraft** and near-zero capex. This
   de-risks the IP that matters (§4).
2. **Quote at least three NDAA heavy-lift builders** — Freefly plus two of Watts / Inspired
   Flight / Harris — against the §1.0 questionnaire. Confirm payload-bay power, Ethernet, actuator
   outputs, and whether they will support a spray integration at all.
3. **Confirm with Foxtech** whether an AeroClean gun/tether assembly can be supplied decoupled
   from DJI mounting and control — the mechanical parts are likely reusable.
4. **Then** buy one Alta X Gen2 **NDAA SKU** and integrate.

**Do not buy an aircraft before step 1.** The ground rig tests the thesis for a few thousand
dollars; the aircraft tests it for forty-five.

---

## 8. Open questions

- [ ] Will Freefly support a **liquid spray payload** on Alta X — warranty and airworthiness
      position? Water plus electronics plus rotors is not a camera gimbal.
- [ ] Tethered-hose dynamics on an Alta X: hose weight, drag and snag behaviour differ from the
      airframes Foxtech tuned against.
- [ ] Real endurance **with the tether attached and gun running** — not the 20 lb datasheet figure.
- [ ] Auterion Enterprise PX4 licence terms for a **commercial derivative product**.
- [ ] Insurance: what does a carrier charge for a self-integrated spray drone versus a
      vendor-supported one? This may be the deciding number and nobody has asked it.

> `TODO(PROPWASH): needs Kevin + Freefly + insurer decisions before committing capital.`
