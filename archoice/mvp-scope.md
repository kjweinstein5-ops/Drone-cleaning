# ARCHOICE — MVP Scope

> v0.1 (2026-06-23). The smallest build that proves the core bet: **does the
> diagnose → plan → choose → buy loop actually convert at peak intent?**
> Everything not serving that question is deferred.

---

## 0. The one thing the MVP must prove

> A homeowner points their phone at a real problem, and ARCHOICE produces a plan and a
> shopping list good enough that they **buy and act** — measurably more than they would
> from a Google search.

If that's true, the business works. If it's not, no amount of extra features saves it.
So the MVP is built to test exactly that, in **one beachhead category**, on **iOS LiDAR
devices only.**

---

## 1. In scope (v1)

### 1.1 Capture & diagnose
- Camera capture + LiDAR depth on supported iPhones/iPads.
- Single-photo diagnosis via multimodal AI (Claude API): object + problem + severity +
  confidence.
- **Confidence gating:** low-confidence or safety-critical results show "consult a pro"
  instead of a DIY plan.

### 1.2 Measure
- LiDAR area/length capture for the work zone (drives material quantities).

### 1.3 Plan
- AI project decomposition: ordered steps, tools, materials + **quantities**, est. cost,
  est. time, DIY-difficulty score.
- Versioned prompt + tool schema in-repo.

### 1.4 Choose
- Recommendation set per material need: **Best Fit / Sponsored(optional) / Budget /
  alternatives** (per advertising-spec §2).
- Affiliate buy-buttons to **one** retail partner.
- Sponsored slot present but can ship dark (no advertisers yet) — slot exists, just empty.

### 1.5 Shopping list
- Aggregate all materials/tools into one list with a single "buy all" hand-off.

### 1.6 Waitlist → onboarding
- Landing page (built) → TestFlight beta.

### 1.7 Instrumentation (critical)
- Full funnel: scans → diagnoses → plans viewed → list created → buy-button taps →
  attributed purchases. This **is** the experiment; without it the MVP proves nothing.

---

## 2. Explicitly deferred (NOT in v1)

| Deferred | Why | Comes back at |
|---|---|---|
| Android / ARCore | iOS LiDAR is the cleanest beachhead | Phase 3 |
| AR step-by-step **Execute** guidance | Heavy AR work; not needed to test the buy loop | after loop converts |
| Contractor Pro / pro network | Different sales motion | Phase 2 |
| SDK / white-label | B2B; needs a proven consumer loop first | Phase 3 |
| Multi-category | Focus beats breadth for the experiment | after one category works |
| Live brand-placement marketplace | Need audience before advertisers | when DAU justifies it |
| AR result-preview rendering | Nice, not load-bearing for conversion | fast-follow |

---

## 3. Beachhead category (pick ONE before building)

Criteria: high frequency, low safety risk, clear SKU mapping, DIY-feasible, photogenic
problem. Candidates: **interior paint + wall patch**, **caulk/sealant refresh**, **fixture
swap (faucet/handle/hardware)**. Recommend starting with **caulk/sealant or paint+patch** —
common, forgiving, and the SKU set is small and mappable.

> `TODO(ARCHOICE): Kevin picks the single launch category.`

---

## 4. Architecture (thin but real)

```
iOS app (React Native + native AR module)
   │  capture (photo + LiDAR depth/measure)
   ▼
Backend API
   ├─ Diagnosis service  → Claude API (multimodal): problem + confidence + safety flag
   ├─ Planning service   → Claude API: decomposition (steps/tools/materials/qty/cost/time)
   ├─ Product graph      → problem → materials → SKUs (one category, one retailer)
   └─ Funnel analytics   → every step instrumented
```

- Product graph and the calibrated problem→SKU mapping are the **trade-secret asset** —
  seed it for one category, grow it from real usage.
- Prompts/tool schemas versioned in-repo.

---

## 5. Build sequence (≈ first 12 weeks)

| Wk | Milestone |
|---|---|
| 1–2 | iOS capture + LiDAR measure spike; backend skeleton + analytics. |
| 3–4 | Diagnosis service (one category) + confidence/safety gating. |
| 5–6 | Planning service → structured plan UI. |
| 7–8 | Product graph (one category) + recommendation slots + affiliate buy-buttons. |
| 9–10 | Shopping list + full funnel instrumentation; internal dogfood. |
| 11–12 | Closed TestFlight; measure the loop; iterate diagnosis accuracy. |

---

## 6. Success criteria (decide go / no-go on data)

Track from beta — _all thresholds are hypotheses to validate, not promises:_

- **Diagnosis acceptance:** % of users who agree the diagnosis was right.
- **Plan→list rate:** % of plans that become a shopping list.
- **List→buy rate:** % of lists with an attributed purchase.
- **Time-to-decision:** vs. a self-reported baseline (the "42%" claim — validate first-party).
- **Diagnosis accuracy / safety:** false-negative rate on safety-critical problems → must be
  near zero before broadening categories.

Go = the diagnose→buy loop beats the user's status-quo (search + guess) on conversion and
confidence. Otherwise iterate diagnosis quality before adding any deferred feature.

---

## 7. Risks specific to the MVP

| Risk | Mitigation in v1 |
|---|---|
| Diagnosis wrong on safety-critical issue | Confidence gating + hard pro-handoff list; near-zero false-negative bar. |
| LiDAR-device-only shrinks beta pool | Accept it — we want signal quality, not volume, in v1. |
| No advertisers yet | Sponsored slot ships dark; affiliate carries early revenue test. |
| Scope creep into Execute/AR | Deferred list (§2) is the contract; resist. |
