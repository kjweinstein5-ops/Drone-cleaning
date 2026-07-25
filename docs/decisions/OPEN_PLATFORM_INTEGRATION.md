# Decision Note — Open-Platform Integration (the "openness spectrum")

> **Status:** OPEN — complements the DJI note; answers "how do I run my own tech on the drones."
> **Type:** Platform-openness + integration decision. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `CLAUDE.md` §2, §7, §10 · `docs/decisions/DJI_TWO_DRONE_ARCHITECTURE.md` ·
> `docs/decisions/CLEANING_DRONE_PLATFORM.md` · `docs/LUCID_OUTREACH.md`.
> ⚠️ Specs/prices from vendor marketing (July 2026), UNVERIFIED — confirm before buying.

---

## 0. Reframing "I want to bypass Sherpa's autonomy restriction"

Read the goal correctly and it's completely legitimate — read it wrong and it's out of scope.

**✅ The legitimate goal (what we build toward):** the Sherpa is a **closed** platform — Lucid
keeps autonomy in-house and exposes no developer control API, so PROPWASH is stuck at Path A
and can never run *its own* tech on the aircraft. The fix is **not to hack a closed drone** —
it's to **choose an open, developer-friendly platform where your tech is a first-class citizen
by design.** That's picking the right partner architecture, and it's what this note maps.

**❌ The line we do not cross (CLAUDE.md §7, §10):** we do **not** build anything whose premise
is concealing autonomous operation from a manufacturer or circumventing Part 107. Even on a
fully open platform, **increased flight autonomy requires the appropriate FAA pathway/waiver,
and the operator stays in command until then.** Openness gives you the *ability* to build
autonomy legally; it does not exempt you from the FAA. Payload autonomy (pressure/nozzle,
Tier-1 safety-gated) is available now; autonomous *flight* is a separate, regulated step.

**Two honest routes to escape the Sherpa's closedness:**
1. **Convince Lucid to adhere to your tech** — a partnership / API access (Lucid Refresh),
   which is the transparent path (`docs/LUCID_OUTREACH.md`). Having your own open stack is
   *leverage* in that conversation.
2. **Choose an open platform** (below) where integration is welcomed, not fought.

---

## 1. The openness spectrum (the core framework)

| Tier | Example | What you can integrate | Trade-off |
|---|---|---|---|
| **Closed** | **Lucid Sherpa** | Nothing — Path A work orders only | Supported/turnkey, but your tech is locked out |
| **Semi-open** | **DJI + Payload SDK** | Custom payloads + some mission control | Best price/capability; DJI owns the flight core + NDAA concentration risk |
| **Open commercial** | **Freefly Astro, Skydio X10** | Payloads + deep SDK (MAVSDK / APIs) | US-made, NDAA-safe, developer-first; pricier, less turnkey |
| **Fully open** | **PX4 / ArduPilot custom build** | The ENTIRE autonomy stack (MAVLink) | Total control; you're the aircraft integrator = all airworthiness/FAA/liability |

**The insight:** the further right you go, the more of your own tech runs on the aircraft —
and the more responsibility you own. Sherpa is as far left as it gets (that's the frustration);
your PSM/IHM + closed-loop control need at least **semi-open**, and "run everything through my
tech" points at **open commercial or fully open.**

---

## 2. MAVLink / MAVSDK — the open "tech between them"

For any open platform, the communication standard is **MAVLink** (the lightweight open
messaging protocol drones/ground-stations/payloads speak) and **MAVSDK** (Dronecode's SDK:
C++, **Python**, Swift, Kotlin bindings). This is the open-stack equivalent of DJI's Cloud
API/PSDK — and it's **vendor-neutral**: the same MAVSDK code talks to PX4, ArduPilot, and
Freefly Astro. So an open stack lets PROPWASH's backend speak to the drone through an **open,
non-proprietary protocol you fully control** — exactly the "communicate through our tech" goal.

---

## 3. Open platform options

### Freefly Astro — the open-commercial sweet spot ⭐
- **US-made** commercial drone (NDAA hedge vs DJI). **Smart Dovetail** standard payload
  interface + **Pixhawk Payload Bus**; uses **MAVSDK**. Any compliant payload works on any
  compliant drone — so your **PSM/IHM cleaning payload** (or a thermal scout payload) can be
  built to a published standard.
- This is the platform CLAUDE.md §5's *original* planning assumed (Sentera 6X on a Freefly
  Astro). The instinct was right — it's open, supported, and US-made.

### PX4 / ArduPilot — fully open, you own everything
- Open-source autopilot stacks + MAVLink/MAVSDK. Build a custom heavy-lift airframe + cleaning
  payload + your PSM/IHM, and you own the *entire* autonomy stack. Maximum integration and no
  vendor lock-in — but you become the aircraft manufacturer for airworthiness/FAA/liability.

### Skydio X10 / X10D — open, autonomy-first, US
- US, NDAA-compliant, best-in-class autonomous navigation; open platform with APIs/ICDs and
  **custom attachment** specs (mechanical/electrical/power). Excellent **scout** (autonomous
  inspection); Skydio does **not** make a cleaning drone, so it's a scout option, not a cleaner.

---

## 4. Scout vs. cleaner on open stacks

- **Scout (scan):** Freefly Astro + thermal/RGB payload, or Skydio X10 (autonomous inspection).
  Both US-made, both feed the pipeline via MAVSDK/API.
- **Cleaner (execute):** there is **no off-the-shelf open cleaning drone** — you build one:
  an open heavy-lift airframe (Freefly-class or custom PX4) + a cleaning payload (Foxtech/
  drone-payload or custom) + your PSM/IHM over the Smart Dovetail / Payload Bus. This is
  Path C, fully owned — more work than the DJI retrofit, but maximum openness + US hedge.

---

## 5. How PROPWASH stays vendor-neutral (so the platform is swappable)

The whole point of the interface discipline: **support DJI *and* open stacks behind one
boundary**, so the platform choice (and any future policy change) is a swap, not a rebuild.

```
Orchestrator → ExecutionTransport (already exists)
                 ├─ WorkOrderTransport      (Path A — Sherpa/operator)      ✅ built
                 ├─ DjiPayloadTransport      (Path B/C — DJI PSDK)   flagged, to build
                 └─ MavlinkPayloadTransport  (Path B/C — PX4/Freefly) flagged, to build
```
A new `MavlinkPayloadTransport` (an `ExecutionTransport` speaking MAVSDK) sits beside the DJI
one — both behind `PROPWASH_ENABLE_PATH_B/C`. The safety layer (Tier 1) validates every
setpoint before either transport actuates. Your tech is the constant; the drone is the plug-in.

---

## 6. Guardrails (firm)
1. **No hacking closed hardware; no concealing autonomy; no circumventing Part 107** (§7, §10).
2. **Operator in command** until an FAA waiver authorizes more automation — on *any* platform.
3. **Payload autonomy ≠ flight autonomy.** MAVSDK/PSDK can command the payload (safety-gated);
   autonomous flight is separate and regulated.
4. **Safety layer authoritative (§2)** — vetoes any unsafe setpoint regardless of transport.
5. **Vendor-neutral interfaces** — MAVLink is open and portable; don't hard-code any vendor.

---

## 7. Recommendation

- **Pragmatic now:** DJI + PSDK (semi-open) — best price/capability, covered in the DJI note.
- **Open + US hedge (the "run everything through my tech" answer):** **Freefly Astro** for an
  open, supported, US-made platform with a standard payload bus + MAVSDK; **PX4/ArduPilot** if
  you want to own the entire stack. Both escape the Sherpa's closedness *legitimately*.
- **Build a `MavlinkPayloadTransport`** beside the DJI one so the backend speaks the open
  protocol; keep everything flagged until FAA/liability review.
- **In parallel, run the Lucid conversation** — an open stack is your leverage to get Lucid to
  adhere to your tech if you'd rather partner than build.

Escape the closed platform by **choosing openness**, not by fighting a locked one — and keep
the interfaces vendor-neutral so you're never trapped again.

---

## 8. Open items
- [ ] Freefly Astro price + payload-bus power/data specs for a cleaning payload.
- [ ] MAVSDK payload-control capability check for the pump/nozzle setpoints we need.
- [ ] FAA waiver scope for any beyond-operator automation (per platform).
- [ ] Decide: DJI (semi-open, cheap) vs Freefly/PX4 (open, US hedge) — or support both.

## 9. Decision log
| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Reframe "bypass Sherpa" → choose an OPEN platform (not hack a closed one); map the openness spectrum; recommend DJI-now / Freefly-PX4 as the open+US path; build a MAVSDK-based ExecutionTransport; keep interfaces vendor-neutral. Part 107 line firm. | Claude (advisory) | Awaiting Kevin — status OPEN |

---

## Sources
- [PX4 Autopilot](https://github.com/PX4/PX4-Autopilot) · [Dronecode / MAVSDK / MAVLink](https://dronecode.org/projects/)
- [PX4 vs ArduPilot comparison](https://thinkrobotics.com/blogs/learn/px4-vs-ardupilot-complete-comparison-guide-for-drone-developers)
- [Freefly Astro — US-made commercial drone](https://freeflysystems.com/astro) · [Freefly payloads / Smart Dovetail](https://freefly.gitbook.io/astro-public/other-user-manuals/freefly-payloads)
- [Skydio developer tools](https://www.skydio.com/developer-tools)
