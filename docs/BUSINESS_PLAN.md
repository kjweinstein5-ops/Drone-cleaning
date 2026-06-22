# PROPWASH — Path to $10M/year

> Strategy is the source of truth for *direction*; numbers here are **goals to validate, not facts**
> (per CLAUDE.md §15.5). Treat every dollar figure as a hypothesis with a test attached.

---

## 0. The core insight

PROPWASH is **not a drone-cleaning service**. It is a **data-and-software company** that uses a
cleaning service as (a) its go-to-market wedge and (b) its data-collection engine. The defensible,
scalable asset is the closed-loop intelligence (Sense → Fuse → Plan → Execute → Verify → re-queue)
and the calibrated prescription + verification models — **not** swinging a wand at more buildings.

A single fully-booked crew tops out around **$600–800K/year** (≈3 jobs/day × ~$1,000 × 5 days).
$10M as pure services ⇒ ~13+ crews ⇒ low-margin, labor-heavy treadmill. That is not the plan.

**The plan: services prove and feed the system; recurring commercial contracts + software licensing
produce the $10M.**

---

## 1. The wedge: AI-verified solar cleaning

Lead with **AI-verified solar panel + roof cleaning**, not generic "exterior cleaning." Why solar first:

| Reason | Why it matters |
|---|---|
| **Quantifiable ROI** | Dirty panels lose 5–20% output. Thermal scan *measures* soiling before/after — you sell **measured output recovery with proof**, not "we cleaned it." |
| **Recurring** | Panels re-soil → quarterly/biannual contracts → recurring revenue (the thing that scales and is valuable). |
| **Commercial scale** | Warehouses, dealership canopies, HOAs, municipal, small solar farms = $50K–500K+ recurring contracts. A handful = most of the number. |
| **Lowest risk surface** | DI water only, low pressure (CLAUDE.md §9) → least damage/liability while learning. |
| **Drone-native** | Rooftop commercial work is dangerous/expensive for humans; drones are genuinely better. |
| **Ties to your tech** | Your thermal sensor directly detects soiling/hotspots → your verification loop *is* the value prop. |

Win solar → land-and-expand into roofs/gutters/façades for the same customers.

⚠️ **Riskiest assumption to kill first:** that thermal soiling cleanly maps to recoverable kWh.
Prove it on the first 5 jobs before building a sales deck on it (see §5).

---

## 2. Products to build (in order)

1. **Operator app** — per-zone checklist, nozzle/standoff/dwell guidance, live thermal overlay,
   PASS/retry. Lets a non-expert be productive → scale crews without scaling expertise. *(Operational moat.)*
2. **Customer ROI report** — automated before/after thermal report showing measured soiling removed
   and estimated output/value recovered. **This is the sales + retention engine.** *(Built — see
   `propwash/backend/reports/roi_report.py`.)*
3. **PROPWASH SaaS platform** *(the $10M unlock, yr 2+)* — license the orchestration + verification
   software to other Lucid Sherpa operators / cleaning contractors. 80%+ margins. This is where the
   valuation and the $10M get real.

---

## 3. The flywheel

Every job feeds the calibrated surface/pressure table + verification model (trade secrets, §11).
More jobs → better prescriptions → better results → better proof → more contracts → more data.
After ~12–18 months of real jobs the prescription model is non-replicable by new entrants **and**
is the thing you license. Services build the moat; software is the money.

---

## 4. Phased path (milestones, not promises)

| Phase | Window | Focus | Crews | Run-rate (goal) |
|---|---|---|---|---|
| **0 — Prove the loop** | 0–6 mo | 20–40 paying solar/roof jobs; nail unit economics + verify loop | 1 | $100–250K |
| **1 — Recurring commercial** | 6–18 mo | Convert proof → recurring contracts (PM firms, HOAs, solar O&M) | 2–3 | $1–2M |
| **2 — Productize** | 18–36 mo | Launch SaaS + franchise/equipped-operator model in new metros | network | toward $5–10M |

$10M ≈ **recurring commercial contracts + software licensing + a network of operators on your platform** —
not you personally cleaning everything.

---

## 5. 30 / 60 / 90 day plan

**Next 30 days**
- Commit to solar as the wedge.
- Run 5 real solar jobs (even at cost). Produce 5 ROI reports.
- **Validate the thermal → kWh recovery correlation** (the make-or-break assumption).
- Capture true cost-per-job.

**Next 60 days**
- Operator app + ROI report to MVP.
- Sign first *recurring* commercial pilot (one HOA or one commercial solar site).
- Call Lucid (see `docs/LUCID_OUTREACH.md`).

**Next 90 days**
- Close 3 recurring contracts.
- Harden prescription model on real data.
- Decide the Phase-2 fork (services-led vs. platform-led).

---

## 6. Risks to kill early (do not skip)

1. **Lucid dependency (§7):** No confirmed API; in-house autonomy. Call them this month. If they
   won't partner, the licensing play must target their operator base *with* them or stay Path A.
   **Single biggest strategic unknown.**
2. **Thermal-ROI must be real (§5):** Edge is "measured output recovery." Prove on first 5 jobs.
3. **Honest claims (§5, §7, §11):** No "multispectral," no "fully autonomous." Honesty *is* the
   moat and what makes you fundable.
4. **Part 107 / operator-in-command (§10):** Don't design flows that hide automation from the
   regulator. More flight automation needs an FAA pathway.

---

## 7. The open strategic fork

**Operator-led services company with great software**, or **software/platform company that licenses
the brain?** The blended path above leans platform (that's where $10M lives), but it's a function of
your appetite for ops vs. product. Decide by end of Phase 0 — the data from real jobs will tell you
which one the market is pulling you toward.
