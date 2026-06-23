# ARCHOICE — Master Business Plan

> **Status:** Founder working document, v0.1 (2026-06-23).
> Numbers marked _(projection)_ are unvalidated goals, not facts. Do not encode them
> as business logic or quote them as traction. Calibrate against real funnel data.

---

## 0. One-line pitch

**ARCHOICE turns the moment a homeowner stands in front of a broken thing into a guided,
shoppable, do-it-or-delegate project** — using phone AR + LiDAR + AI to diagnose the
problem, decompose the fix, recommend the exact products, and guide execution or hand off
to a vetted pro.

> Name = **AR** + **CHOICE**: augmented reality that ends in a confident decision.

---

## 1. Problem

Home improvement is a high-anxiety, low-confidence purchase. The person with the problem
is rarely the person with the expertise.

- They don't know **what's actually wrong** (is that a leak, condensation, or efflorescence?).
- They don't know **what the fix involves** — steps, tools, materials, skill, time, risk.
- They don't know **what to buy** — which of 40 caulk SKUs, which drill bit, how much paint.
- They don't know **whether to DIY or hire** — and if hiring, who to trust or what's fair.

The result: decision paralysis, abandoned projects, over-buying, wrong purchases, and
returns. The intent is highest **at the moment of standing in front of the problem** — and
no tool captures it there.

### Why now
- LiDAR + ARKit/ARCore are now in mainstream phones, giving sub-cm spatial measurement for free.
- Multimodal AI (e.g., the Claude API) can decompose a photographed problem into a
  structured project plan — steps, materials, tools, cost, and difficulty — in seconds.
- AR shoppers convert faster: industry studies cite **~42% shorter decision-to-purchase**
  for AR-assisted buyers _(secondary source; verify before quoting publicly)_.

---

## 2. Product

ARCHOICE is an **AR-first home-improvement intelligence app** (iOS first, LiDAR-capable
devices). The user points their phone at a problem; ARCHOICE runs the loop:

**Point → Diagnose → Plan → Choose → Execute / Delegate → Verify.**

### Five product modes

| # | Mode | What it does | Tech |
|---|------|--------------|------|
| 1 | **Diagnose** | Point at a broken/worn/unfinished thing; AI identifies the object, the likely problem, and severity. | Camera + multimodal AI |
| 2 | **Measure** | Auto-capture dimensions, areas, and volumes of the work zone. | LiDAR + ARKit |
| 3 | **Plan** | AI decomposes the fix into ordered steps with tools, materials, quantities, cost, time, and a DIY-difficulty score. | Claude API project decomposition |
| 4 | **Choose** | Recommends the exact SKUs to buy (with alternatives), placed in AR to preview the finished result. | AR rendering + product graph |
| 5 | **Execute / Delegate** | Step-by-step AR-guided execution for DIY, **or** one-tap handoff to a vetted local pro with the scoped project attached. | AR overlays / contractor network |

### The defensible wedge
Existing AR home tools (Houzz Pro, Magicplan, Planner 5D, IKEA Place) use AR mainly for
**visualization** — "see the couch in your room." ARCHOICE uses AR for **diagnosis,
project decomposition, and execution guidance**. Nobody owns the **DIY-execution +
hardware-recommendation layer** at the point of highest intent. That layer — the AI that
turns "what's wrong" into "here's exactly what to buy and do" — is the IP.

---

## 3. Competitive landscape

Mapped against ARCHOICE's six differentiating capabilities:

| Competitor | AR diagnosis | AI project decomposition | DIY execution guidance | Product/SKU recommendation | Contractor handoff | LiDAR precision measure |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Houzz Pro** | – | – | – | ○ (catalog) | ✓ (marketplace) | – |
| **Magicplan** | – | – | – | – | ○ | ✓ |
| **Planner 5D** | – | – | – | ○ | – | ○ |
| **IKEA Place** | – | – | – | ✓ (IKEA only) | – | – |
| **Hover** | – | – | – | – | ○ (pros) | ✓ (exterior) |
| **RoomGPT / AI design** | – | – | – | – | – | – |
| **Thumbtack / Angi** | – | – | – | – | ✓ | – |
| **ARCHOICE** | ✓ | ✓ | ✓ | ✓ (open, multi-brand) | ✓ | ✓ |

✓ = core capability · ○ = partial/adjacent · – = not offered

**Key finding:** every incumbent occupies one slice — visualization (IKEA Place), floor
plans (Magicplan), or lead-gen (Angi/Thumbtack). None close the loop from *diagnosis* to
*shoppable, guided execution*. ARCHOICE's moat is the **AI decomposition + product graph**
sitting between "I have a problem" and "it's fixed."

---

## 4. Business model — five revenue streams

| # | Stream | Mechanism | Notes |
|---|--------|-----------|-------|
| 1 | **Freemium → Pro subscription** | Free diagnosis/measure; Pro unlocks unlimited plans, AR execution guidance, project history. ~$9–14/mo. | Predictable ARR base. |
| 2 | **Brand placement** | Manufacturers pay to be the recommended/featured SKU in a category. Clearly labeled. | Highest-margin; must stay honest to retain user trust. |
| 3 | **Affiliate commissions** | Buy-buttons to Home Depot / Lowe's / Amazon retail APIs. | Captures intent at peak; low lift. |
| 4 | **SDK / white-label licensing** | Retailers & manufacturers embed ARCHOICE diagnosis+recommendation in their own apps. | B2B; later phase, defensible. |
| 5 | **Contractor Pro** | Vetted pros pay for scoped, high-intent leads + in-app project management. | Bridges DIY-to-delegate; competes with Angi on quality of lead. |

**Trust guardrail (non-negotiable):** sponsored/branded recommendations are always
labeled as such, and a neutral "best fit" option is always shown alongside. The moment
recommendations feel bought, the diagnosis loses credibility — and the diagnosis is the
product.

---

## 5. Financial projection _(all figures are projections, not traction)_

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Installs (cumulative) | 120k | 800k | 3.2M |
| Pro subscribers | 4k | 35k | 140k |
| Subscription revenue | $0.5M | $4.4M | $19.5M* |
| Affiliate + brand placement | $0.2M | $1.6M | — |
| Contractor Pro + SDK | — | $0.4M | — |
| **Blended revenue** | **~$0.7M** | **~$6.4M** | **~$8.7M** |

\* Illustrative subscription ceiling; **blended Year-3 target of ~$8.7M** assumes a more
conservative subscriber-conversion and ARPU mix than the gross subscription line implies.
**These are goals to validate against the real funnel — treat the $8.7M as a planning
anchor, not a forecast.** Key sensitivities: free→Pro conversion (assumed 4–5%), monthly
churn, and affiliate take-rate.

---

## 6. Go-to-market — three phases

1. **Phase 1 — DIY wedge (months 0–9).** iOS LiDAR users, single highest-frequency
   category (e.g., interior paint + patch, or fixture replacement). SEO + creator content
   ("point your phone at it"). Goal: prove the diagnosis→purchase loop converts.
2. **Phase 2 — Monetize intent (months 9–18).** Turn on affiliate + brand placement; launch
   Contractor Pro in 1–2 metros for delegate handoff. Expand categories.
3. **Phase 3 — Platform (months 18–24+).** SDK/white-label to a retailer or manufacturer;
   Android; broaden the product graph; international.

---

## 7. Technology

- **Capture:** ARKit / ARCore, LiDAR depth, on-device frame selection.
- **Diagnosis & planning:** multimodal **Claude API** for object/problem identification and
  structured project decomposition (steps, tools, materials, quantities, cost, difficulty).
- **Product graph:** SKU catalog + embeddings mapping problems → materials → buyable SKUs,
  with retailer price/availability via affiliate APIs.
- **Rendering:** AR overlays for measurement, result preview, and step-by-step guidance.
- **Client:** React Native (iOS-first), native AR modules.
- **Backend:** API services, user/project store, analytics funnel instrumentation.

> Keep AI prompts and the decomposition tool schema versioned in-repo. The product graph and
> the calibrated problem→SKU mappings are the trade-secret asset — build them from real usage.

---

## 8. Brand identity

ARCHOICE looks like a **construction viewfinder** — you are sighting a problem and getting an
answer overlaid on reality.

| Token | Value | Use |
|---|---|---|
| Accent (construction orange) | `#FF6A1A` | CTAs, scan line, highlights |
| Ink (near-black) | `#0E0F12` | Backgrounds, text |
| Blueprint line | `#1E2A44` | Grid background |
| Signal white | `#F5F6F8` | Surfaces, body text |
| Mono accent | `#9AA3B2` | Spec / metadata text |

- **Display:** Barlow Condensed (industrial, signage).
- **Body:** Inter (neutral, legible).
- **Mono/spec:** Space Mono (measurements, technical readouts).
- **Signature motif:** an animated **viewfinder scan line** sweeping a blueprint grid — the
  app "scanning" reality.

---

## 9. Risks & mitigations

| Risk | Mitigation |
|---|---|
| AI mis-diagnoses a problem (safety/structural/electrical) | Confidence gating + explicit "consult a licensed pro" handoff for electrical, gas, structural, roofing. Never give unsafe DIY guidance. |
| Recommendations seen as pay-to-play | Hard labeling + always show a neutral best-fit option. Trust is the asset. |
| Incumbent (Houzz/Angi/IKEA) copies the loop | Speed + the proprietary problem→SKU product graph built from real usage. |
| LiDAR-only limits addressable devices early | iOS LiDAR beachhead now; widen to ARCore depth + photogrammetry later. |
| Affiliate/retail API dependency | Multi-retailer from day one; SDK strategy reduces single-channel risk. |
| Liability for DIY outcomes | Clear scope-of-advice terms; route regulated trades to licensed pros. |

---

## 10. 24-month roadmap

- **M0–3:** MVP — Diagnose + Measure + Plan for one category; waitlist → TestFlight.
- **M3–6:** Choose mode + affiliate buy-buttons; AR result preview.
- **M6–9:** Execute mode (AR step guidance); expand to 3–4 categories.
- **M9–12:** Brand placement; Contractor Pro pilot in one metro.
- **M12–18:** Multi-metro contractor network; broaden product graph; funnel optimization.
- **M18–24:** SDK/white-label pilot; Android; internationalization groundwork.

---

## 11. Open questions (resolve, don't assume)

1. **Beachhead category** — which single high-frequency problem proves the loop fastest?
2. **Diagnosis accuracy bar** — what confidence threshold is safe to ship per category?
3. **Conversion assumptions** — the 4–5% free→Pro and the 42% AR decision-speed stat both
   need first-party validation before they drive the model.
4. **Regulated-trade boundary** — exactly which categories must force a licensed-pro handoff?
5. **Retail partnerships** — which affiliate/retail API first; terms; price-data freshness.

> _Build the conservative path; leave a marker rather than guessing where these are unresolved._
