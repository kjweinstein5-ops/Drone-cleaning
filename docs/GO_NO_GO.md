# Is this worth pursuing? — a deliberately skeptical read

> Kevin's question: *is this space too crowded, and is it worth pursuing further even with tech
> they don't have?*
>
> This document argues the **against** case as hard as it can, then says what survives.
> Companion to `COMPETITIVE_LANDSCAPE.md` (who is out there) — **this one is the verdict.**
>
> All figures are cited, dated **2026-08-16**, and come from vendor/press sources, which are
> promotional. Treat them as the optimistic end.

---

## The one-paragraph answer

**The market is not too crowded. But the plan as written points at the weakest intersection of
every axis it could have chosen** — coastal geography where solar cleaning barely pays,
residential scale where jobs are worth hundreds instead of $14,000, and a "we detect dirt" claim
that shipped in commercial PV software years ago. Same technology, repointed at **inland/desert
commercial and solar assets**, is a materially better business. And one number in our own model
is **4.8× too optimistic** and needs fixing before any funding conversation.

**Verdict: pursue — but re-aim, and prove the intelligence sells before buying a spray drone.**

---

## Part 1 — The case AGAINST (taken seriously)

### 1.1 The solar wedge is weakest exactly where we're based ⚠️

| Geography | Annual soiling loss | Cleanings/yr justified |
|---|---|---|
| **Coastal SoCal** (Santa Monica, Long Beach — **and Carlsbad**) | **2–8%** | **~1** — rain rinses |
| Inland / desert SoCal | **5–25%** | 2+ |
| Desert, remote | up to **30%+** | continuous programmes |

At SCE's ~34.5¢/kWh, recovering 10% of a 12,000 kWh/yr system is ~$414/yr against ~$400 for two
cleanings — *near-breakeven inland*. **On the coast, with lighter soiling and free rain rinsing,
the arithmetic is worse.**

**CLAUDE.md §1 names coastal Carlsbad as the base market and solar as the wedge. Those two
choices fight each other.** Carlsbad is a fine place to *live*; it is close to the worst place in
Southern California to sell solar cleaning on ROI.

### 1.2 The market grows slowly

Solar panel cleaning: **$1.22B (2025), 3.5% CAGR** to 2035. That is a mature service market, not
a hypergrowth one. Nothing wrong with it — but nobody should pitch this as a rocket ship, and a
$10M target is ~0.8% of the *entire global* solar-cleaning market. Exterior building cleaning
overall is much larger, which is an argument for **not** over-indexing on solar.

### 1.3 The SaaS-to-operators play is weaker than I said last turn ❌

**I recommended licensing to Lucid's 400+ operators. I have to walk that back.**

**Lucid Refresh** is already a **subscription that bundles**: Sherpa drone + **Lavo AI autonomous
pressure-washing robot** + **Lucid Command fleet-management software** + **"job intelligence"** +
training + equipment loaner guarantee. One price, one vendor.

So selling software into that base means competing with a bundle, through the relationship of
the company that owns the hardware, the channel and the customer. That is a hard motion, and I
under-weighted it.

Worse for the long game: Lucid **just raised $20M explicitly to build "America's leading exterior
cleaning platform,"** keeps autonomy in-house (they acquired Avianna), and has now shipped an
**autonomous** ground robot. **The capability gap closes from their side, funded, while we
write Python.**

### 1.4 "We see the dirt" is already commoditised ❌

Sitemark, MapperX, Anvil Labs, Inspekt AI and Folio3 already ship automatic classification of
thermal *and visual* anomalies **including soiling**, with pixel-precise measurement and
historical digital twins. In utility solar, **SolarVision AI-class systems already dispatch
cleaning automatically** when SCADA performance data flags underperforming strings — that is a
closed loop, in production, today.

Any patent or marketing built on soiling detection is weak. (`IP_PROTECTION.md` and CLAUDE.md §11
should both be read against this.)

### 1.5 Operator pain is sales, not pressure settings

An operator running 10+ jobs/year averages **$200K revenue** with a payback under two months.
Their constraint is **finding the next commercial contract**, not deciding whether stucco takes
4.0 or 4.5 bar. Software that optimises the thing that isn't the bottleneck doesn't get bought.

### 1.6 The base market already has our exact thesis, taken

**DronePower1 markets Carlsbad specifically**, on the *high-solar-adoption-on-Spanish-tile-roofs*
argument. That is our wedge, our city, our roof type — already someone's homepage.

### 1.7 ⚠️ Our own revenue model is 4.8× optimistic

This is the most uncomfortable finding in the document.

| | Per crew / operator per year |
|---|---|
| `reports/revenue_model.py`, premium route | **$960,000** |
| Observed: Lucid operator running 10+ jobs/yr | **$200,000** |

| Crews needed for $10M | |
|---|---|
| Our model (premium, 1 aircraft) | **7** |
| At observed $200K/crew | **33** |
| At an aggressive $400K/crew | **17** |

Cross-check: 400+ operators, ~1,000 robots, **$75M cumulative** network revenue ≈ **$187K per
operator cumulative** — i.e. most of that fleet is part-time or adjacent-service, not a
full-time exterior-cleaning business.

**The model's 300 kW/day × 200 days is not a plan, it is a ceiling nobody has hit.** It must be
recalibrated against observed job values before it is shown to anyone.

---

## Part 2 — What survives the beating

### 2.1 The services economics are genuinely better than I assumed ✅

| Metric | Value |
|---|---|
| Average **commercial** job | **$14,023** |
| Median job needing 8+ hours flight | **$30,588** |
| Operator payback on hardware | **< 2 months** (vendor claim) |
| Operator with 10+ jobs/yr | **$200,000/yr** |

Fourteen good commercial jobs is a $200K business. That is a real, financeable services company
with modest capex — and it is *nothing like* the residential single-family job the repo currently
models.

### 2.2 Damage liability is the real product, and nobody sells it ✅

On a **$30,588** job against solar glass, historic stucco or failing window seals, the expensive
event is not a slow clean — it is **destroying a surface**. Our deterministic safety layer
(`safety/checks.py`), hard per-surface pressure ceilings, and hash-chained audit log
(`safety/audit_log.py`) produce something none of the 18 regional operators and none of the
inspection platforms produce:

> **Provable, per-surface, gated execution with a tamper-evident record of what pressure touched
> what material and why.**

That is an **insurance and risk instrument**, not a convenience feature. It is the answer to
"who pays when the panels crack," and it is worth more on a $30K job than on a $600 one.

### 2.3 Verification has a contractual home — in solar PPAs ✅

Utility and commercial PPAs define obligations by **Performance Ratio** and **Availability
Guarantee**, with documented monthly PR against contract. A cleaning vendor who can hand over a
verified, geolocated, before/after record tied to those metrics is selling into an **existing
compliance requirement**, not creating a new want.

That is where the closed loop stops being a demo and becomes a line item.

### 2.4 The whitespace is real, just narrower than claimed ✅

- Regional operators: execute, no per-surface model, no verification.
- Inspection platforms: analyse, then hand a human a report.
- Utility solar dispatch systems: close the loop **for PV only, at farm scale, via SCADA** — not
  for mixed-surface buildings, and not with damage-gated execution.

**Nobody joins per-surface prescription + safety gating + execution + verification on
heterogeneous building envelopes.** That's narrower than "nobody closes the loop," and it is
still ours.

---

## Part 3 — The verdict

### Pursue. But re-aim on three axes.

| Axis | As written | Re-aimed | Why |
|---|---|---|---|
| **Geography** | Coastal Carlsbad | **Inland / desert** — Inland Empire, Imperial Valley, Palm Springs, Phoenix | Soiling 5–25% vs 2–8%; the ROI story only works where the dust is |
| **Segment** | Residential + light commercial, single-family demo | **Commercial / industrial + solar assets** | $14K–$30K per job vs hundreds; multi-aircraft only pays at this scale; damage exposure is where our safety layer earns |
| **Product claim** | "We detect grime" | **"We prove it was cleaned, and prove nothing was damaged"** | Detection is commoditised; gated execution + audit trail is not |

Note that the deconfliction work already told us this: the reference **house supports max 1
aircraft**. Every multi-aircraft economic argument in this repo only pays on large commercial and
solar sites. The code has been pointing at the right customer for a while; the plan hasn't caught up.

### Sequence — cheapest disproof first

1. **Sell the scan, not the wash.** Inspection + verification reports. No Part 107 spray op, no
   water, no containment, no damage exposure, no drone capex beyond the Autel. `FIELD_OPERATIONS.md`
   §3 already flagged this; the landscape confirms it is uncontested *within cleaning*.
   **This tests whether anyone pays for the intelligence before you bet on hardware.**
2. **Find one inland commercial solar customer** with a PR-based obligation. Deliver the
   before/after verified record against their Performance Ratio.
3. **Only then** decide whether to operate spray hardware yourself, or license to operators who
   already do.

### Kill criteria — decide these now, honestly

Stop, or change strategy, if:

- **Nobody pays for a scan-only report** after ~10 serious commercial conversations. If the
  intelligence has no standalone value, the moat isn't a moat.
- **Lucid ships per-surface prescription + verification inside Lucid Refresh.** They are funded,
  they own the channel, and they are already building autonomy. This is the single most likely
  way the opportunity closes.
- **The dry-down curve can't be calibrated** to make thermal verification reliable
  (`FIELD_OPERATIONS.md` §6). Without trustworthy verification the loop doesn't close, and the
  loop *is* the differentiator.
- **Recalibrated unit economics stay under ~$300K/crew/yr.** At $200K, $10M needs 33 crews — an
  operational sprawl that contradicts the owner-operated plan.

### What to fix in the repo immediately

- [ ] **Recalibrate `reports/revenue_model.py`** against observed job values ($14K commercial,
      $30.5K major). The current 300 kW/day × 200 days is unvalidated and 4.8× optimistic.
- [ ] **Reword any claim resting on soiling detection** — patent language, marketing, IP doc.
      Claim the *gated closed loop*, not the sensing.
- [ ] **Add a commercial/industrial reference structure** to `geometry/source.py`. Every demo is
      a single-family house; every dollar is in flat commercial roofs and solar arrays.
- [ ] **Re-run the market assumption in CLAUDE.md §1** — coastal Carlsbad as base market conflicts
      with solar as wedge.

---

## Part 4 — Honest limits of this analysis

- **Vendor figures are promotional.** Payback "under two months" and "400% ROI" are Lucid's
  marketing. The $200K/operator and $14K/job figures were given by Lucid to a trade publication —
  directionally useful, not audited.
- **$75M "network revenue" is cumulative and undated**, so per-operator annualisation is an
  inference, not a measurement.
- **Soiling percentages vary enormously** by microclimate, tilt, and rainfall year. Carlsbad's
  actual number should be measured on real arrays, not read off a blog.
- **No primary research.** No customer interviews, no operator interviews, no state registries.
  Everything here is desk work and should be treated as a hypothesis to test, including the
  verdict.
- **The strongest single validating action** remains asking Lucid directly: *how many operators
  in Southern California, what does a typical SoCal operator bill annually, and does Lucid Refresh
  do per-surface prescription today?* Three questions, and the answers largely settle this
  document.
