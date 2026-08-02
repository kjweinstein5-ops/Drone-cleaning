# Decision Note — Sensor Platform Shortlist

> **Status:** OPEN — awaiting Kevin's call.
> **Type:** Hardware decision record (the survey / mapping drone only — NOT the cleaning drone).
> **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `docs/3D_DATA_PIPELINE.md` §0b, §8 · `CLAUDE.md` §4 (hardware inventory), §5 (honesty rule).

This note is the running shortlist for **which drone captures the survey data** that feeds
the fusion pipeline. It is a decision *record*, not a spec — update the status line when a
choice is locked, and reflect it into `CLAUDE.md §4`.

---

## The decision in one line

**The thermal sensor is the crown-jewel input, and it is 640×512 radiometric on every
option below — identical.** So this decision is about the *survey platform around the
thermal camera* (RGB/photogrammetry quality, obstacle avoidance, mission automation),
**not** about improving grime-detection data. Frame every trade-off through that lens.

---

## Shortlist (ranked for PROPWASH's survey role)

### 1. Autel EVO MAX 4T **V2** — *recommended if buying fresh* (verified specs, July 2026)

**V2 confirmed specs:** 48MP 1/2" CMOS wide camera · 8K zoom (10× optical / 160× hybrid) ·
**thermal 640×512 radiometric**, 13mm lens, 16× digital zoom, −4°F to 1022°F · **laser
rangefinder 5–1200 m, ±1 m** · **RTK module option** · 42 min flight · 720° obstacle avoidance ·
SkyLink 3.0 (20 km).

**Why it fits PROPWASH specifically:** thermal and RGB are on the **same gimbal**, so they are
**co-registered** — same pose, same instant. That materially simplifies Stage-2 thermal
registration (no cross-flight alignment), which is the hardest part of painting temperature
onto the mesh. With the RTK option the mesh gains survey-grade georeferencing, improving
standoff accuracy and the area math behind the ROI report.

**⚠️ Correction — Autel is NOT an NDAA hedge.** Autel Robotics is Shenzhen-based and faces
broadly similar US regulatory scrutiny to DJI. Do **not** buy Autel to diversify away from the
DJI concentration risk flagged in `DJI_TWO_DRONE_ARCHITECTURE.md` §6 — it does not achieve
that. (Freefly / Skydio are the genuine US/NDAA hedges.) Buy Autel on sensor merit.

**⚠️ SDK is the open question.** Autel's developer ecosystem is thinner than DJI's. Lower risk
for a *scout* (we mainly need geotagged imagery + poses out), but send the Integration
Qualification Questionnaire — especially **Q1, Q2, Q4, Q8** — before buying. If imagery and
telemetry can't be pulled programmatically, the "seamless pipeline" degrades to manual SD-card
transfers.

---

### 1b. Autel EVO MAX 4T (original) — *superseded by V2*
- **Thermal:** 640×512 radiometric (same as EVO II).
- **RGB:** 50 MP wide (larger sensor) + up to ~160× hybrid zoom.
- **4th sensor:** **Laser rangefinder** (single-point, ~5–1200 m) — **NOT LiDAR** (§0b).
- **Obstacle avoidance:** omnidirectional — the biggest real-world win flying close to buildings.
- **Automation:** modern SDK + repeatable mission planning (automated survey flights).
- **Cost (verify):** ~$9K+.
- **Best when:** buying fresh, want the strongest survey platform + safety margin near structures.

### 2. Autel EVO II Dual 640T (V3) — *current inventory; keep if already owned*
- **Thermal:** 640×512 radiometric (identical crown-jewel channel).
- **RGB:** 8K / ~48 MP.
- **4th sensor:** none.
- **Obstacle avoidance:** basic.
- **Automation:** older SDK.
- **Cost (verify):** ~$6–7K.
- **Best when:** already owned — thermal data won't improve by upgrading, so keep flying it
  and spend the money on the PSM prototype + IP instead.

### 3. LiDAR aircraft (e.g., DJI Matrice 350 + Zenmuse L2) — *future, only on concrete need*
- **Geometry:** true scanning LiDAR → dense point cloud directly (no SfM needed).
- **4th sensor / thermal:** different payload ecosystem; thermal via separate H20T-class payload.
- **Cost (verify):** ~$15–20K all-in — a different aircraft entirely.
- **Best when:** heavy tree occlusion, survey-grade geometry on tall/complex commercial,
  night/low-light, or faster turnaround genuinely become bottlenecks. Not Year 1. (§8)

---

## What actually differs (survey role)

| Factor | EVO II Dual 640T | EVO MAX 4T | Matters to us? |
|---|---|---|---|
| Thermal (grime proxy) | 640×512 radiometric | 640×512 radiometric | **Tie — the key channel is identical** |
| RGB → photogrammetry | 8K / ~48 MP | 50 MP wide, larger sensor | MAX 4T → better SfM mesh |
| Zoom (defect spotting) | limited | up to ~160× hybrid | MAX 4T → spot individual panels/cracks |
| Laser rangefinder | none | 5–1200 m (single-point) | MAX 4T → SfM scale + live standoff |
| Obstacle avoidance | basic | omnidirectional | **MAX 4T → real safety win near buildings** |
| Automated missions | older SDK | modern SDK / mission planning | MAX 4T → repeatable survey flights |
| Platform age / support | 2020–21 gen | current gen | MAX 4T → longer runway |
| Price (verify) | ~$6–7K | ~$9K+ | EVO II cheaper |

*(All specs/prices are UNVERIFIED — confirm with Autel before purchase.)*

---

## Recommendation

- **Buying fresh, no money committed → EVO MAX 4T.** Not for thermal (it's a tie) but for
  omnidirectional obstacle avoidance flying near buildings, better RGB→photogrammetry, zoom
  inspection, and automated survey missions.
- **Already own the EVO II Dual 640T → keep it, don't rush.** Thermal (your key channel) is
  identical; upgrade only when RGB quality, obstacle avoidance, or mission automation become
  actual bottlenecks. Early dollars are better spent on the PSM bench prototype + IP.
- **True LiDAR → future only,** on a concrete need, behind the `GeometrySource` interface
  (`SfmSource` / `SfmWithLrfSource` / `LidarSource`). (§8)

---

## Guardrails (do not violate regardless of platform)

1. **No Autel option is LiDAR.** The MAX 4T's 4th sensor is a *laser rangefinder* (single
   point), not a scanning point cloud. 3D reconstruction stays **photogrammetry (SfM)**
   either way. (§0b)
2. **Honesty (CLAUDE.md §5).** Never write "LiDAR" in a spec, patent, or pitch while flying
   a rangefinder — same overclaim trap as "multispectral biofilm detection." If we want to
   *say* LiDAR, we must *fly* LiDAR.
3. **Survey drone ≠ cleaning drone.** This decision is about the sensing/mapping aircraft
   only. The Sherpa cleaning drone stays operator-piloted under Part 107 (CLAUDE.md §7/§10).
4. **Pipeline is source-agnostic.** Stage 2+ consumes a point-cloud/mesh abstraction, so
   swapping platforms is a Stage-1 change. Don't hard-code platform assumptions downstream.

---

## Open items before locking the decision

- [ ] Confirm current Autel pricing + availability (EVO MAX 4T **V2**, EVO II Dual 640T V3).
- [ ] **Send Autel the Integration Qualification Questionnaire (Q1/Q2/Q4/Q8)** — confirm
      programmatic export of imagery + telemetry before purchase.
- [ ] Price the **RTK module** — survey-grade georeferencing materially improves mesh accuracy.
- [ ] Confirm the MAX 4T laser rangefinder is exposed in the SDK (for live-standoff use).
- [ ] Decide: are we already committed to / do we already own the EVO II Dual 640T?
- [ ] If MAX 4T is chosen → update `CLAUDE.md §4` hardware inventory to match.
- [ ] Confirm automated survey missions are within our Part 107 operating comfort/authorizations.

---

## Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Shortlist drafted; recommendation = MAX 4T if buying fresh, else keep EVO II | Claude (advisory) | Awaiting Kevin's call — status OPEN |
