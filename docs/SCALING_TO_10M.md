# PROPWASH — Full Report: What It Takes for YOUR OWN Company to Reach $10M / Year

> **Scope:** owner-operated cleaning company. **No licensing / SaaS in the core plan** — that's a
> later, separate business model (see §12). This report is the path to $10M as a business *you own
> and run*.
>
> Every dollar figure is a **goal to validate, not a fact** (CLAUDE.md §15.5). Inputs marked
> **UNVERIFIED** (e.g. Sherpa unit cost) must be confirmed. All numbers are produced by
> `propwash/backend/reports/revenue_model.py` — edit the assumptions and re-run
> (`python -m propwash.backend.reports.revenue_model`) to stress-test them.

---

## 1. Executive summary

As an owner-operated services company, $10M/year is reachable **without licensing**, but only by
combining three things: (1) **recurring** commercial contracts, (2) a **verification premium** on
price (your thermal before/after proof lets you charge more than commodity cleaners), and (3)
**multi-surface upsell** (solar → roof → gutter → façade on the same accounts). The lever that keeps
it from becoming a 14-crew treadmill is **revenue-per-crew**, not crew count.

**Recommended route — PREMIUM (7 crews):**

| Stream | Revenue | Gross profit |
|---|---:|---:|
| Own services (recurring commercial) | $6.72M | $3.36M |
| Multi-surface upsell + verification premium | $3.70M | $1.85M |
| **TOTAL** | **$10.42M** | **$5.21M (50% margin)** |
| Crew capex to stand up 7 crews | — | ~$731K (staged) |

**Alternative — VOLUME (10 crews):** ~$10.66M at base pricing; same ~50% margin but **3 more crews,
~$1.05M capex, and a lot more operational/HR load.** The premium route gets to the same number with
fewer moving parts — that's the smarter build.

---

## 2. The two owner-operated routes (pick PREMIUM)

| | PREMIUM (recommended) | VOLUME |
|---|---|---|
| Crews | **7** | 10 |
| Pricing | ~$16/kW (verification premium) | ~$12/kW (base) |
| Upsell intensity | High (0.55 uplift) | Moderate (0.48) |
| Site focus | Larger commercial + portfolios | Broader mix |
| Total revenue | ~$10.4M | ~$10.7M |
| Capex | ~$731K | ~$1.05M |
| Ops/HR burden | Lower | Higher |

Same destination, fewer people and less capital on the premium path. You earn the premium with the
ROI report — measured kWh recovered is something commodity pressure-washers cannot show.

---

## 3. Unit economics (the engine)

- **Commercial solar pricing:** base ~$12/kW per clean; **premium ~$16/kW** with verification proof. VALIDATE on real bids.
- **Crew throughput:** ~300 kW/day × 200 working days = **$720K/crew/year** gross at base price (~$960K at premium).
- **Services gross margin:** ~50% after labor, chemicals, travel, insurance, equipment depreciation.
- **Recurring cadence:** 2 cleans/site/year (biannual) — this is what makes revenue compound instead of resetting.
- **Capex per crew:** ~$104.5K = Sherpa (**~$60K, UNVERIFIED**) + Autel 640T (~$9.5K) + truck/kit (~$35K).
- **Capex for 7 crews:** ~$731K, **staged across years** — you do not buy 7 kits on day one.

Value-story example (from the ROI generator): a 205 kW site with heavy soiling →
**~$6,900 / ~21,700 kWh estimated recovered** per service. That proof justifies the premium and the renewal.

---

## 4. What needs to be BUILT (product & engineering)

Ordered by leverage. Status reflects this repo today. (Owner-operated plan — note SaaS/multi-tenant
items are deferred to §12.)

| # | Build item | Why it's required | Status |
|---|---|---|---|
| 1 | Core loop: schemas, safety, agents, orchestrator, sim | Foundation of everything | ✅ Done |
| 2 | Customer ROI report | Earns the verification premium + drives renewals | ✅ Done |
| 3 | **Operator app** | Non-experts run jobs → add crews without adding experts | ⬜ Next |
| 4 | **Fusion pipeline on real Autel imagery** | Real zone signatures instead of sim | ⬜ |
| 5 | **Persistence: Postgres + PostGIS + Redis** | Many jobs/properties/crews at once | ⬜ |
| 6 | **Scheduling/dispatch + recurring-contract engine** | Recurring revenue needs automated re-booking | ⬜ |
| 7 | **Calibration/learning loop** | Field data → better prescriptions → higher first-pass PASS rate → lower cost/job | ⬜ |
| 8 | Path B/C transports (only if Lucid opens API) | Higher automation, flagged off until §7 resolved | ⬜ Gated |
| — | ~~Multi-tenancy + billing~~ | **Deferred — only needed for licensing (§12)** | ⏸ Later |

---

## 5. What needs to be OPERATIONALIZED (people, equipment, capital)

- **Crews:** scale 1 → 7 over ~4–5 years. Each crew = 1 Part 107 pilot + drone kit + truck.
- **Hiring ladder:**
  - *Phase 0:* you operate (founder-pilot).
  - *Phase 1:* +1–2 pilots, +1 ops/sales hire.
  - *Phase 2:* +ops manager, +scheduler/dispatcher, +1–2 more pilots, dedicated sales.
  - *Phase 3:* +account managers for recurring portfolios, +finance/admin.
- **Equipment:** buy drone/truck kits to demand; don't pre-buy.
- **Capital:** ~$731K crew capex (staged) + payroll runway. Owner-operated services can largely
  **self-fund from recurring cash flow** once Phase 1 contracts land — likely **less outside capital
  than a software play**, which is an advantage of this route. A working-capital line or equipment
  financing for drone kits is the most likely outside need.
- **Insurance & compliance:** commercial drone liability, workers' comp, Part 107 currency per pilot.

---

## 6. What needs to be SOLD (go-to-market & pipeline math)

- **Wedge:** AI-verified commercial **solar** cleaning — quantifiable ROI, recurring, drone-native, safest surface.
- **Buyers:** property managers, HOAs, REITs, solar O&M firms, school districts, municipalities, warehouse/logistics owners.
- **Recurring-contract math (premium route):** $6.72M of own-services at an average ~$40–60K/yr
  recurring account ⇒ roughly **110–170 active recurring accounts**, built over years.
- **Land-and-expand motion:** one site → ROI report proof → portfolio rollout → multi-surface
  bundle → biannual auto-renewal. Net revenue retention is the quiet engine of this plan.
- **Why you win the bid:** you don't quote "a cleaning," you quote **measured output recovery with proof.**

---

## 7. Partnerships & regulatory (gates, not optional)

- **Lucid (§7):** Even owner-operated, your execution rests on Lucid hardware with no confirmed API.
  Work `docs/LUCID_OUTREACH.md` now — at minimum confirm Refresh data access; a partnership de-risks fleet growth.
- **FAA Part 107 (§10):** Operator stays in command. Each crew needs a current Part 107 pilot. Any
  increase in flight automation needs a proper FAA pathway/waiver — budget time/legal; don't assume it.
- **Legal/IP (§11):** Provisional patent on the *method*; keep the prescription table + learning model
  as trade secrets. Engage counsel. A provisional is a placeholder, not protection.

---

## 8. The data moat (why this stays defensible even as services)

Every job feeds the calibrated surface/pressure table + verification model. Higher first-pass PASS
rate → fewer re-cleans → lower cost/job → fatter margin than competitors at the same price. The moat
shows up as **margin and reliability**, not just as a future product.

---

## 9. Year-by-year milestone ladder (owner-operated)

| Year | Revenue (goal) | Crews | The job to be done |
|---|---:|---:|---|
| **0** (0–6 mo) | $0.1–0.25M | 1 | Prove loop; 20–40 jobs; validate thermal→kWh; nail unit economics |
| **1** | $0.7–1.2M | 2 | First recurring commercial contracts; operator app + DB; call Lucid |
| **2** | $2.5–3.5M | 3–4 | Scheduling/recurring engine; learning loop live; build sales muscle |
| **3** | $5.5–7M | 5–6 | Premium pricing established; portfolio accounts; account managers |
| **4–5** | **$10M+** | 7 | Premium route at steady state; ~50% gross margin |

---

## 10. KPIs to track from day one

- Cost per job + gross margin per job
- **Thermal-soiling → measured kWh-recovered correlation** (make-or-break metric)
- First-attempt verification PASS rate (drives cost/job and the moat)
- Recurring contract count + net revenue retention
- Revenue per crew (the lever that keeps crew count down)
- Re-soil interval per site (drives renewal cadence)

---

## 11. Kill-list — validate before betting big

1. **Thermal soiling ↔ recoverable kWh** is real and measurable (whole solar wedge rests on it).
2. **You can actually charge the ~$16/kW premium** — that the proof commands the price.
3. **Sherpa unit cost (~$60K)** and throughput (~300 kW/day) hold against reality.
4. **Lucid** at least exposes job data; ideally partners on fleet growth.
5. **Part 107 / automation** path doesn't block the operational model or crew scaling.

Hit these cheaply and early. The premium route's whole advantage (#2) depends on #1 being true.

---

## 12. Licensing — the LATER business model (explicitly not in this plan)

Once you have 18+ months of field-calibrated data and a hardened product, you *can* add a second
business: license the PROPWASH intelligence layer to other operators (SaaS). For reference, that
would add a high-margin (~80%) stream and could lift the blend to ~$10M with **fewer crews (6) plus
~140 licensed fleets at ~61% margin** — but it requires multi-tenancy + billing (deferred in §4),
the Lucid relationship, and a product mature enough to hand to strangers. **Park it as Phase 3+
upside; don't let it pull focus from the owner-operated build now.**
