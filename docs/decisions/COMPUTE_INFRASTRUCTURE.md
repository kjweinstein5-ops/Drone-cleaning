# Decision Note — Compute Infrastructure (Hybrid Local + Cloud)

> **Status:** RECOMMENDED — awaiting Kevin's purchase.
> **Type:** Infrastructure decision record. **Owner:** Kevin. **Last updated:** 2026-07-06.
> **Related:** `IP_PROTECTION.md` §3 (data moat) · `docs/3D_DATA_PIPELINE.md` §7 (data
> sovereignty) · `CLAUDE.md` §2 (tiered safety), §12 (stack).

Goal: run PROPWASH **internally** on hardware Kevin controls, keeping the trade-secret
data in-house, **without** overpaying Apple for storage or pretending Claude can run
locally (it can't — §2).

---

## 1. The one-paragraph decision

Buy a **Mac Studio, M4 Max chip, 64 GB unified memory, 2 TB internal SSD** as the internal
box. It runs photogrammetry, computer vision, the backend, the databases, local open-weight
models, and stores the crown-jewel data — all on hardware you own. Use **cloud Claude**
(via the API with commercial terms + zero-retention, or inside your own AWS Bedrock / Google
Vertex tenant) for the hard reasoning, because **Claude cannot run locally.** For bulk data,
**do not pay Apple's SSD prices** — put the growing imagery/point-cloud/dataset archive on
**external Thunderbolt 5 NVMe + a RAID NAS**, which costs a fraction per terabyte.

---

## 2. Can Claude run locally? No. (Settle this first.)

**Anthropic does not release Claude's weights.** Claude runs only on Anthropic's
infrastructure or approved clouds (AWS Bedrock, Google Vertex AI). There is no
downloadable / offline / on-prem Claude. So:

| You want | Reality |
|---|---|
| Claude's reasoning quality | **Cloud only** — API call over HTTPS |
| Something running on the Mac Studio | **Open-weight models** (Llama, Qwen, DeepSeek) — *not* Claude, weaker at hard reasoning |

"Local Claude" is a contradiction. Choose per-workload (§3).

### Data sovereignty without local Claude
Protecting the data does **not** require Claude on your hardware. Three levels:

1. **Anthropic API, commercial terms** — Anthropic does **not** train on your API
   inputs/outputs by default.
2. **Zero Data Retention (ZDR)** — for qualifying customers, prompts/outputs aren't
   stored after the response.
3. **Claude in your own cloud tenant (AWS Bedrock / Google Vertex)** — Claude runs inside
   your VPC boundary; data stays in your account, not sent to Anthropic directly. Closest
   thing to "private Claude."

*(Confirm current Anthropic terms/ZDR eligibility before relying on them.)*

---

## 3. The hybrid architecture — what runs where

```
┌──────────────────────────────────────────────────────────────┐
│  MAC STUDIO (M4 Max, 64 GB) — your internal box, data at home │
│                                                                │
│  • Photogrammetry (OpenDroneMap SfM)                           │
│  • Computer vision (SAM / PyTorch via Metal)                   │
│  • Backend: FastAPI + PostgreSQL/PostGIS + Redis               │
│  • Tier-1 SAFETY LAYER (deterministic — always local)          │
│  • Tier-2 orchestrator (~1 Hz)                                 │
│  • Local open-weight model (Ollama) for quick/offline tasks    │
│  • CROWN-JEWEL DATA storage + the labelled dataset             │
└───────────────┬──────────────────────────────────────────────┘
                │  advisory reasoning only (API over HTTPS)
                ▼
┌──────────────────────────────────────────────────────────────┐
│  CLOUD CLAUDE (API / Bedrock / Vertex) — Tier-3 agents         │
│  • Mapping · Fusion · Supervisor · Cleaning · Post-Clean       │
│  • The hard reasoning where quality matters ("be brilliant")   │
│  • Protected by commercial terms + ZDR, or your own tenant     │
└──────────────────────────────────────────────────────────────┘
                ▲
                │  (optional) air-gapped local open model for any
                │  workload that must never touch a network
```

**Why this is safe to depend on cloud for Tier 3:** per CLAUDE.md §2, the **safety layer
(Tier 1) and orchestrator (Tier 2) are local and deterministic.** The cloud agents are
**advisory only.** If the network drops, safety and orchestration still function — only the
advisory reasoning degrades. Cloud dependency never sits in a safety loop.

---

## 4. Chip binning + memory — exact recommendation

**M4 Max, 16-core CPU / 40-core GPU, 64 GB unified memory.** Reasoning:

### The chip bin is not optional — it's tied to the memory
Apple bins the M4 Max in two ways, and memory is gated by the bin:

| M4 Max bin | Max unified memory |
|---|---|
| 14-core CPU / 32-core GPU | **36 GB only** |
| **16-core CPU / 40-core GPU** | 36 / 48 / **64 GB** |

**To get 64 GB you *must* select the 16-core / 40-core chip** — the base 14/32 bin caps at
36 GB. So the "should I upgrade the cores?" question is already answered by the memory
decision: yes, and there's no 64 GB build without it.

### The bigger chip also helps PROPWASH's heaviest local jobs
Even independent of memory, the upgrade speeds up exactly what this box does:
- **16 CPU cores** → faster **photogrammetry** (OpenDroneMap SfM is CPU-bound; this is the
  slowest pipeline step, so cores directly cut survey→model time).
- **40 GPU cores** → faster **computer vision** (SAM/PyTorch via Metal) and faster **local
  LLM** token generation (Ollama's Metal backend uses the GPU).

There is no sensible PROPWASH build on the 14/32 bin.

> ⚠️ **Photogrammetry-speed caveat (see `3D_DATA_PIPELINE.md` §2b).** The Mac Studio runs
> **Agisoft Metashape** (native Apple-Silicon GPU accel) fast enough for building-scale
> models (~30 min–2 h each). But the *fastest* engines — **RealityCapture, DJI Terra** —
> are **Windows + NVIDIA only** and **cannot run on the Mac Studio at all.** If job volume
> or near-real-time turnaround ever demands max speed, that's a **separate small NVIDIA GPU
> box** (RTX 4090/5090-class, ~$2–3K) for the reconstruction step only — not a Mac upgrade.
> Start Mac-only with Metashape; add the NVIDIA box later if speed becomes the constraint.

### Memory sizing
- Unified memory is soldered — **you cannot upgrade it later.** Buy the right amount once.
- **Get 64 GB, not 36 GB.** The 36→64 GB jump is the single most important AI upgrade here.
- 64 GB comfortably runs photogrammetry + CV + backend + databases **simultaneously**, plus
  a local ~70B open model (4-bit ≈ 40 GB) when you want one.
- The M4 Max **caps at 64 GB** — going higher forces the M3 Ultra (96 GB, ~$1,500 more,
  ~800 GB/s bandwidth). **Only worth it if fast local LLM becomes a *primary* workload.**
  Since the heavy reasoning is cloud Claude here, the M4 Max 64 GB is the cost-smart pick.

| Option | Memory | When |
|---|---|---|
| ⭐ **M4 Max, 64 GB** | 64 GB cap | **This build** — hybrid, cloud does heavy LLM |
| M3 Ultra, 96 GB | 96 GB, faster | Only if running large local models fast is core |
| M4 Max, 36 GB | avoid | Too tight for concurrent AI + CV workloads |

---

## 5. Storage — internal vs external (where the real money is saved)

**Apple's internal SSD upgrades are extremely overpriced** — maxing internal storage can add
**thousands of dollars.** Don't. Split storage by how hot the data is:

### 5a. Internal SSD — keep it modest: **2 TB**
Holds the OS, apps, local model weights (a couple of 70B models), the active databases, and
current-job working data. 2 TB is the sweet spot — 1 TB fills fast once you add local models;
4 TB+ internal is where Apple's pricing gets abusive. **Pay Apple for 2 TB, no more.**

### 5b. Fast external (hot bulk) — **Thunderbolt 5 NVMe, ~4 TB**
The M4 Max Mac Studio has **Thunderbolt 5** (up to 120 Gb/s). A TB5 external NVMe enclosure
hits ~5–6 GB/s — fast enough to process imagery and point clouds directly off it. ~4 TB for
a few hundred dollars vs. Apple charging ~$1,000+ for the same internal bump.

### 5c. Archive + the data moat (cold bulk) — **RAID NAS**
The **accumulating labelled dataset is the trade-secret moat** (IP_PROTECTION.md §3). It
needs redundancy and backup, not raw speed:

- A **Synology / RAID NAS** (e.g., 4-bay) gives many TB with **RAID redundancy** — a drive
  can fail without data loss. This is the permanent home for the growing dataset.
- Follow **3-2-1 backup**: 3 copies, 2 media types, 1 offsite (an encrypted cloud bucket or
  a rotated external drive).
- **Encrypt at rest** (FileVault on the Studio; encrypted volumes on the NAS) — the moat
  checklist from IP_PROTECTION.md §4.

### Storage strategy summary

| Tier | Hardware | ~Size | ~Cost | Holds |
|---|---|---|---|---|
| Internal (hot) | Apple SSD | 2 TB | (Apple bump) | OS, apps, models, DBs, active job |
| External fast | TB5 NVMe | 4 TB | ~$300–500 | Imagery/clouds being processed |
| Archive (cold) | RAID NAS | scalable | ~$800–1,500+ | The labelled dataset moat + backups |

**Money saved vs. maxing Apple internal SSD: easily $1,500–3,000+**, redirected to the PSM
prototype / IP filings.

---

## 6. Indicative build + cost

| Item | Spec | ~Cost (verify) |
|---|---|---|
| Mac Studio | **M4 Max (16-core CPU / 40-core GPU), 64 GB, 2 TB SSD** | ~$3,000 |
| External fast storage | TB5 NVMe enclosure + 4 TB drive | ~$400 |
| Archive/backup | 4-bay RAID NAS + drives | ~$1,000–1,500 |
| Cloud Claude | API usage (pay-as-you-go) | usage-based |
| **One-time hardware total** | | **~$4,400–4,900** |

vs. a maxed M3 Ultra (512 GB former config, 16 TB internal) at **~$14,000** — for capability
this hybrid doesn't need, since cloud Claude does the heavy reasoning.

---

## 7. Guardrails

1. **Claude is never local.** Don't design any component assuming an on-prem Claude (§2).
2. **Safety stays local + deterministic.** Tier 1/2 run on the Mac Studio; cloud agents are
   advisory only (CLAUDE.md §2). Network loss must never disable safety.
3. **Encrypt the data moat** at rest + in transit; least-privilege access (IP_PROTECTION.md §4).
4. **Confirm Anthropic data terms** (no-training / ZDR / Bedrock-Vertex) before sending any
   sensitive job data to cloud Claude.
5. **Unified memory can't be upgraded** — get 64 GB up front.

---

## 8. Open items

- [ ] Confirm current Mac Studio configurator (M4 Max 64 GB / 2 TB) pricing + Thunderbolt 5.
- [ ] Choose NAS (Synology model + drive count) sized for expected job volume.
- [ ] Confirm Anthropic commercial terms + ZDR eligibility (or decide Bedrock/Vertex).
- [ ] Pick the local open model for offline tasks (Llama 3.3 70B / Qwen class).
- [ ] Set up FileVault + NAS encryption + 3-2-1 backup before first real customer data lands.

---

## 9. Decision log

| Date | Decision | By | Notes |
|---|---|---|---|
| 2026-07-06 | Recommend **M4 Max (16-core/40-core) / 64 GB / 2 TB** + TB5 external + RAID NAS; cloud Claude for Tier-3; Claude confirmed **not** locally runnable | Claude (advisory) | Awaiting Kevin's purchase — status RECOMMENDED |
| 2026-07-06 | Clarified: 64 GB requires the 16-core CPU / 40-core GPU bin (base 14/32 caps at 36 GB); upgrade also speeds photogrammetry + CV + local LLM | Claude (advisory) | Closes gap in §4 |
