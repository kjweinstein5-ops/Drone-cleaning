# Decision Note — All-DJI Two-Drone Architecture

> **Status:** OPEN — a strong candidate architecture; revises the CLAUDE.md §4 hardware base.
> **Type:** Platform + system-architecture decision. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `CLAUDE.md` §2 (tiers), §4 (inventory), §6 (loose-sync), §7 (integration paths),
> §10 (operator) · `docs/decisions/CLEANING_DRONE_PLATFORM.md` · `docs/decisions/SPECTRAL_SENSING_DECISION.md`
> · `docs/3D_DATA_PIPELINE.md`.
> ⚠️ Prices/specs from vendor/third-party marketing (July 2026), **UNVERIFIED** — confirm before buying.

---

## 0. The architecture in one picture

```
  DJI SCOUT DRONE (scan)                    DJI CLEAN DRONE (execute)
  Matrice 4T: thermal + RGB + zoom          Matrice 350/400 + cleaning payload
        │                                          ▲
        │ geotagged thermal+RGB                    │ work order + coverage path
        ▼                                          │ (pressure/nozzle setpoints, flagged)
  ┌──────────────────────────────────────────────────────────────┐
  │  PROPWASH BACKEND  (the tech that connects them)               │
  │  NodeODM reconstruct → thermal registration → segmentation     │
  │  → prescriptions (safety-gated) → COVERAGE / FLIGHT PATH        │
  │  Tier-1 safety layer · Tier-2 orchestrator · Tier-3 agents      │
  └──────────────────────────────────────────────────────────────┘
        ▲  DJI Cloud API (MQTT)                    │  DJI Payload SDK
        │  telemetry / imagery in                  │  payload control out
        └──────────────────────────────────────────┘

  ⚠ The two drones NEVER talk to each other directly (CLAUDE.md §6).
    They loose-sync through the PLAN. The "communication tech" is the
    PROPWASH backend + the DJI SDK endpoints — not a real-time drone link.
```

---

## 0b. The moat is the MIDDLE, not the drones

Anyone can buy a DJI scout and a DJI cleaning rig — the hardware is **commodity**. What no
competitor can buy is **the connective tech between them**: the software that ingests the
scout's imagery, **generates the 3D model, extracts every surface and its condition, and
computes the flight path that drives the cleaner.** That middle layer is what makes PROPWASH
unique and hard to copy:

- **Model generation + surface detail** — thermal-onto-mesh registration, the surface/asset
  classifier trained on *your* field data, the conservative safety fusion, the grime proxy.
  (`3D_DATA_PIPELINE.md` Stages 2–3; `IP_PROTECTION.md` §2 — patent the loop, trade-secret
  the brain.)
- **The scan→plan→flight-path bridge** — prescriptions from your calibrated tables, the
  safety gate, the coverage path. Two commodity drones, loose-synced into one closed loop by
  *your* code.
- **The data flywheel** — every job sharpens the classifier and the tables. A copycat with
  identical DJI drones still starts at zero data (`IP_PROTECTION.md` §3).

**So the hardware choice (this doc) should optimize for cost/capability and for *feeding the
middle* — never mistake the drones for the product.** The drones are swappable behind
interfaces (§6); the middle is the company.

---

## 1. Why all-DJI is a coherent bet

- **One SDK ecosystem end to end.** Scout, backend, and cleaner all speak the same DJI
  protocols (Cloud API + Payload SDK + Mobile SDK). Cleaner than the current split of
  **Autel (sensing) + Lucid (cleaning, closed)** — where Lucid keeps autonomy in-house and
  exposes no confirmed control API (CLAUDE.md §7).
- **It's the only path that unlocks your hardware IP.** A DJI clean drone + Payload SDK is
  the platform on which your PSM/IHM pressure/nozzle module can actually be built and
  commanded (`CLEANING_DRONE_PLATFORM.md` §0). On a Sherpa you can't.
- **Mature developer stack.** DJI Cloud API is MQTT-based and production-proven (v1.0 → v1.11+,
  2022→2024), with Dock automation for later scaling.

---

## 2. Best DJI SCOUT (scan) drone

Your scout must do **thermal + RGB photogrammetry in one aircraft** (thermal-forward per
`SPECTRAL_SENSING_DECISION.md`).

| Option | ~Price | Thermal | RGB / photogrammetry | Verdict |
|---|---:|---|---|---|
| **DJI Matrice 4T** ⭐ | **$7,849** | FLIR Boson+ (improved NETD → better solar hot-spots) 640×512 | 4/3 CMOS + 200× zoom + laser rangefinder | **Recommended scout** — thermal+RGB+zoom+LRF in one compact SDK-native aircraft |
| Matrice 350/400 + **Zenmuse H30T** | $$$ | **1280×1024** IR + 3,000 m LRF + NIR aux | 48 MP + 34×/400× zoom | Higher-end; better thermal res if you need it, pricier |
| **Matrice 4E** | ~$6–7K | none | **61 MP mechanical shutter** — best pure RGB geometry | Only if you split thermal/RGB into 2 payloads/flights (not ideal) |
| Mavic 3 Thermal | ~$5K | 640×512 | 20 MP | Budget/compact; less zoom/robustness |

**Recommendation: DJI Matrice 4T (~$7,849).** It replaces the Autel EVO II 640T with a newer,
SDK-native platform: same-class thermal but better NETD (sharper solar hot-spots + moisture),
plus zoom and a laser rangefinder for scale (helps the glass/panel reconstruction limits in
`3D_DATA_PIPELINE.md` §2d). Thermal-forward, one aircraft, one ecosystem.

*(This would update CLAUDE.md §4: Autel EVO II 640T → DJI Matrice 4T for the sensing role.)*

---

## 3. Best DJI CLEAN (execute) drone

Covered in depth in `CLEANING_DRONE_PLATFORM.md` — the DJI-native path is:

**DJI Matrice 350 RTK or Matrice 400 + third-party cleaning payload** (Foxtech AeroClean /
drone-payload) **+ your PSM/IHM via Payload SDK.** ~$25–45K all-in. This is CLAUDE.md §7
**Path C** (own the stack): it unlocks the hardware IP and deep control, but you own the
warranty, FAA-airworthiness, and liability. Operator stays in command (Part 107).

---

## 4. The communication tech (what PROPWASH builds)

This is the heart of your question — and the good news: **most of it already exists in the
repo.** The DJI ecosystem just provides the on-drone endpoints; PROPWASH provides the brain.

### The DJI SDK surfaces we'd use
- **Cloud API (MQTT)** — scout uploads imagery/telemetry to the backend; clean-drone streams
  execution telemetry back. Two modes: Pilot-to-Cloud (manual/operator) and Dock-to-Cloud
  (automated, later).
- **Payload SDK (PSDK v3)** — build/command the cleaning payload (and the PSM/IHM
  pressure+nozzle module). This is the endpoint the Cleaning agent's setpoints reach — **after**
  the Tier-1 safety layer validates them.
- **Mobile SDK / Waylines** — fly the scout's automated survey mission and (later, with FAA
  waivers) the clean drone's coverage path.

### What PROPWASH builds on top (mostly done)
- **Reconstruct → surfaces → flight path** — `geometry/` + `fusion/` + `segmentation/` +
  planning (Stages 1–5). Already built and tested (scan → classified zones → safety-gated
  work orders). The coverage path (Stage 5) is the "flight path toward the surfaces" you want.
- **Two new adapters** (behind existing feature flags):
  - `DjiCloudAdapter` — MQTT ingest of scout imagery/telemetry + clean telemetry.
  - `DjiPayloadTransport` — an `ExecutionTransport` (Path B/C) that speaks PSDK to the
    cleaning payload. Mirrors the existing `WorkOrderTransport` / `VendorApiTransport` /
    `CompanionTransport` pattern; **flagged off** until FAA/warranty/liability review.

### Two things that MUST stay true (CLAUDE.md)
1. **Loose-sync, not a live link (§6).** The drones sync through the *plan*, not a real-time
   drone-to-drone connection. The clean plan is the sync point. This is a feature — it's what
   makes the system robust and legal.
2. **Operator in command (§7, §10).** PSDK lets you command the *payload* (pressure/nozzle —
   Tier-1 safety-gated). It does **not** entitle autonomous *flight* — that needs the FAA
   pathway/waiver. Never conflate payload control with self-flying.

---

## 5. How this solves the whole tech stack (your ask)

> "…from scanning to having the geodata presented so the algorithm produces all the necessary
> surfaces as well as the flight path toward these surfaces."

| Your requirement | Where it's solved | State |
|---|---|---|
| Scout collects data | DJI M4T + waylines (Mobile SDK) | Buy + configure |
| Engine builds the geodata | NodeODM/Metashape (`3D_DATA_PIPELINE.md` §2d) | Buy + wire `SfmSource` |
| Present geodata to our algorithm | `geometry/source.py` → mesh/point cloud | ✅ Built (interface + synthetic) |
| Produce all the surfaces | `segmentation/` (surfaces + exclusions) | ✅ Built + tested |
| Produce the flight path to surfaces | Stage 5 coverage path (offset shell, sweeps, keep-outs) | Designed; not yet coded |
| Communicate scout ↔ cleaner | PROPWASH backend + DJI Cloud API/PSDK adapters | Backend ✅; DJI adapters to build |

So the remaining net-new work is: (a) wire the real `SfmSource` (NodeODM reader), (b) build
the Stage-5 coverage-path code, and (c) the two DJI adapters. Everything else is done.

---

## 6. ⚠️ The one big risk to weigh: DJI concentration / regulatory

Betting **both** drones on DJI concentrates risk in a single vendor that faces real US
regulatory headwinds (NDAA / proposed "Countering CCP Drones" restrictions, potential FCC/
procurement bans). For a US business, if DJI gets restricted, **your entire stack is exposed
at once.** Mitigations to keep in mind:
- **Abstraction saves you.** Keep the `GeometrySource` and `ExecutionTransport` interfaces
  vendor-neutral (already the design). If DJI is ever restricted, you swap adapters, not the
  whole system.
- **NDAA-compliant / Blue-UAS alternatives exist** (e.g., Anzu Robotics — DJI-tech licensed,
  US-assembled; Skydio; Freefly) — pricier, but a hedge if you sell to gov/regulated clients.
- **Don't hard-code DJI assumptions** past the adapter boundary.

This doesn't kill the all-DJI plan — DJI is the best price/capability today — but go in with
the abstraction discipline so a policy change is a swap, not a rebuild.

---

## 7. Recommendation

**Target architecture: all-DJI two-drone, PROPWASH as the connective tissue. Adopt it in
stages, keeping every vendor behind an interface.**

1. **Now — switch the scout to the DJI Matrice 4T** (~$7,849). SDK-native, better thermal
   NETD, one ecosystem. Low-risk, immediate, and it starts the DJI stack. (Updates §4.)
2. **Year 1 cleaning — still start on the Sherpa subscription (Path A)** to get revenue and
   the data moat cheaply/legally (`CLEANING_DRONE_PLATFORM.md` §4d), OR go straight to the
   DJI retrofit if you're ready to own the integration/FAA/liability. The cost model says
   platform choice isn't cash-limiting once a crew works — so decide on IP appetite.
3. **Build the two DJI adapters + Stage-5 coverage path** behind feature flags, in parallel.
4. **Year 2+ — graduate cleaning to the DJI M350/M400 + PSDK + PSM/IHM** once the business
   is proven and the FAA/warranty/liability review is done. That completes the all-DJI stack
   and turns on your hardware IP.

Net: the scout goes DJI immediately (cheap, better, starts the ecosystem); the cleaner
graduates to DJI when you're ready to own Path C. The interfaces make it safe either way.

---

## 8. Guardrails
1. **Loose-sync via the plan (§6)** — no real-time drone-to-drone link.
2. **Operator in command (§7, §10)** — PSDK commands the payload, not autonomous flight;
   more automation needs an FAA waiver. No covert automation.
3. **Safety layer is authoritative (§2)** — validates every pressure/nozzle setpoint before
   PSDK actuation; can veto any dispatch.
4. **Vendor-neutral interfaces** — `GeometrySource` / `ExecutionTransport` keep DJI swappable
   (regulatory hedge, §6).
5. **Path C only after review** — FAA airworthiness, DJI warranty, product liability.

---

## 9. Open items
- [ ] Confirm DJI Matrice 4T price/availability + thermal spec vs the H30T for our needs.
- [ ] Confirm DJI Cloud API + PSDK v3 support the payload control we need (pump/nozzle).
- [ ] Get real quotes for the M350/M400 cleaning payload (Foxtech / drone-payload).
- [ ] Assess DJI NDAA exposure for your client mix (residential = low; any gov/commercial?).
- [ ] Decide scout swap now (Autel → M4T) — update CLAUDE.md §4 if yes.

## 10. Decision log
| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Recommend all-DJI two-drone target architecture; scout → M4T now, cleaner → DJI+PSDK+PSM/IHM Year 2+; keep vendor-neutral interfaces; flag DJI NDAA concentration risk | Claude (advisory) | Awaiting Kevin — status OPEN. Communication = PROPWASH backend + DJI Cloud API/PSDK, loose-synced via the plan (§6). |

---

## Sources
- [DJI SDK guide — Enterprise Insights](https://enterprise-insights.dji.com/blog/dji-sdk-guide)
- [DJI Cloud API docs](https://developer.dji.com/doc/cloud-api-tutorial/en/)
- [DJI Payload SDK v3](https://developer.dji.com/payload-sdk/)
- [DJI Matrice 4T vs 30T vs Mavic 3T — Global Drone HQ](https://globaldronehq.com/blogs/news/dji-matrice-4t-vs-matrice-30t-vs-mavic-3t-thermal-drone-comparison-2026)
- [DJI Enterprise buyer's guide 2026 — Global Drone HQ](https://globaldronehq.com/blogs/news/dji-enterprise-drone-buyers-guide-2026-every-platform-compared)
- [Foxtech AeroClean for DJI M300/M350/M400](https://www.foxtechrobotics.com/T50-Drone-Cleaning-for-DJI-M300-M350-M400-drone.html)
