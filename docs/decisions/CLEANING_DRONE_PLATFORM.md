# Decision Note — Cleaning Drone Platform

> **Status:** OPEN — this is the highest-risk assumption in the project (CLAUDE.md §7).
> **Type:** Hardware + integration-strategy decision. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `CLAUDE.md` §4 (inventory), §7 (Lucid integration paths), §10 (operator model) ·
> `docs/DYNAMIC_PRESSURE_HARDWARE.md` (PSM/IHM) · `docs/IP_PROTECTION.md`.
>
> ⚠️ Prices/specs below are from vendor and third-party marketing (July 2026) and are
> **UNVERIFIED** — confirm with each vendor before buying. Competitor knocks sourced from a
> rival's own blog are flagged; treat them skeptically.

---

## 0. The insight that reframes the whole decision

**The cleaning-drone choice is not really about PSI or price — it decides which integration
path (CLAUDE.md §7) is even available to you, and therefore whether your hardware IP
(PSM/IHM, `DYNAMIC_PRESSURE_HARDWARE.md`) can ever be built.**

- **Buy a Lucid Sherpa → you are locked to Path A** (work-order integration). Lucid controls
  the aircraft and keeps autonomy in-house (they acquired Avianna); **no public developer
  pump/control API is confirmed.** You cannot bolt your own pressure/nozzle hardware onto it
  without their cooperation. Safe, supported, vendor-friendly — but a ceiling on your IP.
- **Build on a DJI + third-party cleaning payload → Path B/C becomes possible** because you
  own and control the whole stack. This is the only path on which your PSM/IHM pressure/
  nozzle IP can actually be integrated — but you become the integrator and take on the
  warranty, FAA-airworthiness, and liability responsibility (CLAUDE.md §7 Path C).

So read every option below through: *"which integration path does this buy me, and what does
that do to my IP and my risk?"*

---

## 1. The market — three categories

### A. Purpose-built commercial cleaning drones (turnkey, supported)

| Drone | Price (verify) | Pressure | Notes |
|---|---|---|---|
| **Lucid Bots Sherpa** | **$75,000** outright, or **$2,950/mo** (Lucid Refresh, incl. maintenance) | up to 4,500 PSI, 300+ sqft/min | Purpose-built for commercial contractors. Up to 150 ft. Soft-wash / pressure / window-squeegee payload. Radar collision 0.5–50 m. 1 pilot + 1 ground. Most-deployed in NA (400+ operators, $75M operator revenue, $20M Series B). **This is what CLAUDE.md §4 already specs.** |
| **Apellix Power Wash** | from **$47,000** (loaded ~$71,500) | 4,000 PSI, 8–10 gpm | Aimed at **industrial** (tanks, marine, infrastructure, painting/coating), tethered or battery+tether. Per Lucid's (biased) comparison, its tethered design limits maneuverability around complex building geometry — **not ideal for residential/commercial facades**. Cheaper, but wrong market for PROPWASH. |

### B. DIY retrofit — DJI enterprise drone + third-party cleaning payload (own the stack)

| Component | Price (estimate — confirm) | Notes |
|---|---|---|
| **DJI Matrice 350 RTK** | ~$12–15K | Proven enterprise platform, omnidirectional sensing, RTK. |
| **DJI Matrice 400** | ~$15–20K | Newer (2025-gen), higher payload/endurance. |
| **Foxtech AeroClean P3 (T50)** payload | contact vendor | Tethered cleaning for M350/M400. **20 MPa default, up to 40 MPa (~400 bar!)**, reach 45 m (latest 120 m), **800 m²/h**. Facades, solar panels, insulators, towers. |
| **Foxtech AeroClean T-M400C** | contact vendor | **Dual tether (power + water)** for M400. 8 h continuous, 1.2 kg spray gun, 80 m hose, 110–160 bar, heights to 60 m. |
| **drone-payload RT-AP3** | contact vendor | For M300/M350 RTK / M400. 1.3 kg payload, facades / glass curtain wall / solar / wind turbines. |

**All-in estimate: ~$25–45K** — likely cheaper than a Sherpa, tethered high-pressure, **and
it's the only path that lets you own the aircraft and integrate your own PSM/IHM hardware.**

### C. Not a fit (noted so we don't chase them)
Window-only squeegee bots, wind-turbine specialists (Aerones-class), and pure industrial
coating rigs — different market than San Diego residential + light commercial.

---

## 2. Tethered vs. untethered — the real trade-off

| | **Tethered** (water ± power from ground) | **Untethered** (battery + onboard tank) |
|---|---|---|
| Endurance | ✅ Continuous, 24/7, no battery swaps | ❌ Short — weight + tank → frequent refills |
| Pressure | ✅ Higher possible (lighter craft; up to ~400 bar on Foxtech) | ⚠️ Limited by payload weight |
| Coverage | ✅ Up to 800 m²/h large-area | ⚠️ Better for small/mid jobs |
| Maneuverability | ❌ Tether management; harder around complex geometry | ✅ Free movement, fast setup, good around facades/roofs |
| Altitude | ❌ **FAA caps tethered at ~140–150 ft AGL** | ✅ Higher AGL possible (still Part 107) |
| Setup cost/complexity | ❌ Higher (ground pump, hose reel, crew) | ✅ Lower startup, faster deploy |
| Best for | High-rise, large-area, continuous industrial | **Residential + light commercial, complex geometry** |

**Read for PROPWASH:** your market is coastal San Diego **residential + light commercial** —
mostly 1–3 stories, complex geometry (roofs, solar arrays, windows, gutters, stucco).
Maneuverability and fast setup matter more than 24/7 high-rise endurance. That leans
**untethered or a short-tether hybrid**, not a full high-rise tethered rig. The 140 ft
tethered cap is irrelevant to you (you're not doing high-rises) — but the tether's
*maneuverability penalty* around a cut-up residential roofline is a real cost. A **ground-fed
water hose without a power tether** (untethered flight, tethered water) is often the sweet
spot: onboard battery for agility, ground water for pressure/endurance without a heavy tank.

---

## 3. Third-party equipment deep dive (the retrofit path)

This is CLAUDE.md §7 **Path C** — a companion/payload on hardware you own. What it unlocks vs.
what it costs:

**What it unlocks (why it's strategically huge for PROPWASH):**
- **Your PSM/IHM hardware IP becomes buildable.** You can mount your electronic
  pressure-set module + nozzle-selector on an aircraft you own. On a Sherpa you cannot —
  Lucid controls it. This is the difference between having a hardware product line and not.
- **Path B/C software integration.** A companion computer can (within FAA/vendor limits)
  take pressure/nozzle setpoints from the orchestrator — the deeper closed-loop control the
  whole architecture is designed for.
- **Cheaper all-in** (~$25–45K vs $75K) and **no vendor lock-in / no subscription.**
- **Vendor-neutral data.** Your scan→plan→execute telemetry stays entirely yours.

**What it costs you (be honest — these are real):**
- **You are the integrator and the responsible party.** Warranty on a modified DJI is *yours*
  to manage; DJI may void coverage on a modified airframe.
- **FAA airworthiness + Part 107.** Adding a cleaning payload + companion computer is a
  modification. Operator stays in command; **any increase in flight automation needs the
  appropriate FAA pathway/waiver** (CLAUDE.md §7, §10). No covert automation, ever.
- **Liability.** A high-pressure spray system on a modified flying vehicle is a product-
  liability surface. Document the firmware ceilings, pilot override, and test logs
  (mirrors `DYNAMIC_PRESSURE_HARDWARE.md` §6).
- **Integration labor.** You own the debugging, the mounts, the calibration — real
  engineering time before it earns a dollar.

**Principle (CLAUDE.md §7):** pursue Path C **only** with proper FAA/warranty/liability review,
on hardware you own, operator genuinely in command. Prefer partnership + proper waivers over
clever circumvention.

---

## 4. Best-for-the-money verdict

| If your priority is… | Best pick | Why |
|---|---|---|
| **Turnkey, supported, lowest-risk start** | **Lucid Sherpa — subscription ($2,950/mo)** | Preserves capital (matches the lean Year-1 model), maintenance included, purpose-built, market-proven. Path A only. |
| **Own the stack + build the hardware IP** | **DJI M350/M400 + Foxtech AeroClean (or drone-payload) kit** | ~$25–45K, tethered high-pressure, unlocks PSM/IHM + Path B/C. You own the risk. |
| **Raw pressure for industrial** | Apellix | Wrong market for PROPWASH residential/commercial — skip. |

**My recommendation for PROPWASH, staged:**

1. **Year 1 — start on the Sherpa subscription ($2,950/mo), Path A.** Lowest risk, no big
   capex, get real jobs and real field data flowing (the data moat is the real asset). Prove
   the software loop and the business before touching airframe modification. This is exactly
   the CLAUDE.md §4/§7 posture.
2. **In parallel — prototype PSM/IHM on a cheap owned test rig** (not the Sherpa), per
   `DYNAMIC_PRESSURE_HARDWARE.md`, so the hardware IP advances without airframe risk.
3. **Year 2+ — evaluate the DJI + third-party retrofit as the "own-the-stack" platform**
   once (a) the business is proven, (b) you have FAA/warranty/liability review done, and
   (c) the PSM/IHM is bench-validated. That's when Path B/C and the hardware product line
   become worth the integration burden.

This keeps Year 1 cheap and legal, while deliberately building toward the owned-stack future
where the defensible hardware IP lives.

---

## 4b. Side-by-side cost model (reproducible)

Modelled in `propwash/backend/reports/drone_platform_cost.py` (`python -m
propwash.backend.reports.drone_platform_cost`). **Platform cost only** — shared running
costs (chemicals, water, labor, insurance) are identical across platforms and wash out.
All figures are **estimates to validate** (CLAUDE.md §15.5); the retrofit payload price is
the biggest unknown — tune the assumptions and re-run.

| Platform | Year 1 | Year 2 | Year 3 | Cash shape |
|---|---:|---:|---:|---|
| **Sherpa subscription** ($2,950/mo) | $35,400 | $70,800 | $106,200 | Pure opex — $0 capex |
| **Sherpa outright** ($75K + ~$5K/yr) | $80,000 | $85,000 | $90,000 | Heavy capex up front |
| **DJI retrofit + PSM/IHM** | $47,000 | $50,000 | $53,000 | ~$44K capex + ~$3K/yr |
| DJI retrofit (base, no PSM/IHM) | $43,000 | $46,000 | $49,000 | ~$40K capex + ~$3K/yr |

**Break-evens (at these estimates):**
- Owned **retrofit (+PSM/IHM) undercuts the subscription after ~16 months**, and is the
  cheapest option overall by year 2–3 (~$53K at 3 yrs vs $106K subscription).
- **Sherpa outright undercuts the subscription after ~30 months** — so if you're confident
  you'll run 3+ years, buying beats renting; below that, the subscription wins on cash.
- Retrofit capex (~$44K) is well under Sherpa outright capex ($75K).

**How to read it for a startup:** the subscription's value isn't that it's cheapest — it
**isn't** past ~1.5 years — it's that it's **$0 capex and de-risked** (maintenance included,
no integration burden) while you validate the business. The retrofit is cheapest long-run
*and* the only path that builds hardware IP, but it front-loads ~$44K and all the
integration/FAA/liability work. The model quantifies exactly what you pay for that de-risking:
roughly **$35K in year 1** to avoid a $44K capex + integration project.

---

## 4c. Which drone has the most potential?

Two different questions hide in "most potential" — answer both honestly:

- **Most near-term potential (fastest, safest path to revenue): the Lucid Sherpa.**
  Purpose-built, supported, market-proven (400+ operators, $75M operator revenue), works on
  day one via Path A. Its ceiling is that Lucid owns the aircraft and the autonomy — you can
  never deeply integrate your own hardware. It's a great *business* platform with a capped
  *IP* ceiling.

- **Most ultimate potential (highest ceiling): the owned DJI + third-party retrofit.**
  It is the **only** platform on which PROPWASH's defensible hardware IP (PSM/IHM) and the
  deep closed-loop control (Path B/C) can actually exist. It's cheapest long-run, vendor-
  neutral, and opens a **second revenue line** (selling the pressure/nozzle modules to other
  operators — `DYNAMIC_PRESSURE_HARDWARE.md`). You earn that ceiling by taking on the
  integration, FAA-airworthiness, warranty, and liability burden.

**Verdict:** the **retrofit/owned-stack platform has the most potential** — because potential
means *ceiling*, and it's the only one whose ceiling includes owning the IP and a hardware
product line. But potential ≠ the right first move. The disciplined play is **Sherpa first to
capture the business and the data moat cheaply and legally, then graduate to the owned stack**
once the business is proven and the PSM/IHM is bench-validated. Buy the near-term with the
Sherpa; build toward the ultimate ceiling with the retrofit.

---

## 5. Guardrails (do not violate)

1. **Operator stays in command (Part 107).** No covert automation; more flight automation
   needs an FAA pathway/waiver (CLAUDE.md §7, §10).
2. **Path A first.** Don't assume a Lucid control API exists — none is confirmed. Gate any B/C
   code behind capability checks + feature flags.
3. **Retrofit = owned hardware + full review.** FAA airworthiness, DJI warranty, and product
   liability all reviewed before any modified airframe flies a paying job.
4. **The safety layer is deterministic and authoritative** regardless of platform — solar
   pressure ceilings, keep-outs, human detection can veto any dispatch (CLAUDE.md §2).
5. **Match the tool to the market.** PROPWASH = residential + light commercial; don't buy
   high-rise industrial capability you won't use.

---

## 6. Open items

- [ ] Get real quotes: Foxtech AeroClean P3(T50) / T-M400C, drone-payload RT-AP3 (prices not public).
- [ ] Confirm DJI M350 vs M400 pricing + whether a cleaning payload voids warranty.
- [ ] Confirm the Sherpa subscription terms + what Lucid Refresh's API actually exposes (§7 OPEN).
- [ ] Decide Year-1 platform: **Sherpa subscription (recommended)** vs. jump straight to retrofit.
- [ ] Attorney/FAA review scope for any Path-C retrofit before it's more than a bench idea.

---

## 7. Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Deep dive done. Recommend **Year 1 = Sherpa subscription (Path A)**; retrofit (DJI + Foxtech/drone-payload) documented as the Year-2+ owned-stack path that unlocks PSM/IHM + Path B/C | Claude (advisory) | Awaiting Kevin's call — status OPEN. Coupling: drone choice ⇒ integration path ⇒ whether hardware IP is buildable. |

---

## Sources
- [Lucid Bots Sherpa — official](https://www.lucidbots.com/sherpa-drone)
- [Best commercial drones for building cleaning 2026 — Lucid Bots](https://www.lucidbots.com/blog/best-commercial-drone-building-cleaning) *(vendor; treat competitor claims skeptically)*
- [Lucid Bots raises $20M Series B — DroneLife](https://dronelife.com/2026/03/25/lucid-bots-series-b-autonomous-cleaning-drones/)
- [Best exterior building cleaning drones of 2026 — The Drone Girl](https://www.thedronegirl.com/2024/03/08/exterior-building-cleaning-drones/)
- [Foxtech AeroClean P3(T50) for DJI M300/M350/M400](https://www.foxtechrobotics.com/T50-Drone-Cleaning-for-DJI-M300-M350-M400-drone.html)
- [Foxtech AeroClean T-M400C tethered cleaning + power](https://store.foxtech.com/aeroclean-t-m400c-tethered-cleaning-power-solution-for-dji-m400-drone-high-altitude-building-cleaning/)
- [drone-payload facade cleaning system (M350/M400)](https://www.drone-payload.com/drone-facade-cleaning-sysytem/)
- [5 Best Washing Drones 2026 — Fly Eye](https://www.flyeye.io/5-best-washing-drones/)
