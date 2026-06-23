# ARCHOICE — Advertising & Brand-Placement Spec

> v0.1 (2026-06-23). How ARCHOICE makes money from recommendations **without poisoning the
> diagnosis that makes the recommendation worth trusting.** Trust is the asset; this spec
> exists to protect it while monetizing intent.

---

## 0. First principle

ARCHOICE earns the right to recommend a product because it correctly diagnosed the problem.
The moment users believe the recommendation was bought rather than reasoned, the diagnosis
loses credibility and the whole loop collapses. Therefore:

> **Every monetized placement is labeled, and a neutral "best fit" option is always shown
> alongside it — never hidden, never out-ranked by payment alone.**

This is a hard product rule, not a preference. See §6.

---

## 1. The three monetized surfaces

| Surface | What it is | Who pays | Trust risk |
|---|---|---|---|
| **Sponsored SKU** | A specific product featured inside a recommendation set. | Manufacturers / brands | High — directly shapes a purchase |
| **Category sponsorship** | A brand becomes the default-featured option in a whole category (e.g., "caulk & sealants"). | Brands / retailers | High |
| **Affiliate buy-button** | Retailer link on any recommended SKU (sponsored or not). | Retailers (commission) | Low — user already chose |

Affiliate is the safe baseline (we get paid on purchases the user was making anyway).
Sponsored/category placement is higher-margin **and** higher-trust-risk — it gets the guardrails.

---

## 2. The recommendation slot model

Every "Choose" screen presents a **recommendation set** for one need (e.g., "exterior caulk
for a 1/4-inch gap"). A set has fixed, transparent slots:

```
┌────────────────────────────────────────────┐
│  RECOMMENDED FOR YOUR FIX                    │
│                                              │
│  [★ BEST FIT]   Neutral algorithmic pick     │  ← never paid; ranked on fit only
│  [SPONSORED]    Brand-paid placement (labeled)│  ← optional; capped at 1 per set
│  [BUDGET]       Lowest viable-quality option  │  ← never paid
│  [+ alternatives ▾]  full ranked list         │  ← affiliate links on all
└────────────────────────────────────────────┘
```

Rules:
- **Best Fit is computed only from fit signals** (problem match, surface, durability,
  reviews, quantity needed) — advertiser money cannot change its ranking.
- **At most one Sponsored slot** per recommendation set. No set is all-sponsored.
- **Budget and Best Fit always present**, even when a Sponsored slot is sold.
- If no advertiser is matched, the Sponsored slot **disappears** (no filler ads).

---

## 3. Eligibility — what's allowed to be sponsored

A product can occupy the Sponsored slot **only if** it clears a relevance floor:

1. It genuinely solves the diagnosed problem (passes the same fit check as Best Fit).
2. Its quality/review score is at or above the category median.
3. It does not contradict a safety constraint (e.g., no sponsored detergent for a surface
   that requires DI-water-only).

> An advertiser can buy *visibility*, never *suitability*. Unsuitable products cannot be
> bought into a recommendation. This keeps the loop honest and keeps us out of liability.

---

## 4. Advertiser pricing (how brands buy)

| Model | Unit | Best for |
|---|---|---|
| **CPM (sponsored impressions)** | per 1,000 qualified recommendation views | brand awareness |
| **CPC (qualified click)** | per tap-through to product detail | mid-funnel |
| **CPA (affiliate-style)** | per attributed purchase | performance buyers |
| **Category sponsorship** | flat monthly / category / region | category leaders |

Targeting dimensions offered to advertisers: **problem type, surface, project size,
DIY-vs-pro intent, region, season**. Never sold: raw user identity or address-level data —
targeting is contextual to the *project*, not the *person*.

---

## 5. "Steering users" — the honest version

The brief was to use the app to steer users toward products. The defensible way to do that:

- **Steer by relevance, disclose the sponsorship.** We surface the right product at the
  right moment (peak intent) and label what's paid.
- **Steer the journey, not the verdict.** ARCHOICE can promote *acting now* ("you have the
  tools — here's the 4-step fix") and route the purchase through our buy-buttons. That's
  legitimate conversion optimization.
- **What we don't do:** fabricate urgency, hide the neutral option, recommend an unsuitable
  sponsored product, or recommend a paid fix when "no action needed" is the truth.

> The line: optimize *which suitable product and when*; never distort *whether it's the right
> product*. Cross that line and the diagnosis — the only reason advertisers want in — stops
> being trusted.

---

## 6. Hard guardrails (product invariants)

1. Sponsored content is **always visibly labeled** `SPONSORED`.
2. A **neutral Best Fit** is always present and never out-ranked by payment.
3. **One sponsored slot max** per recommendation set.
4. Sponsored products must **pass the relevance + safety floor** (§3).
5. **No ads in safety-critical handoffs** — when a problem routes to a licensed pro
   (electrical/gas/structural/roofing), no product is sponsored into that flow.
6. Targeting is **contextual to the project**, not built on selling personal identity.

> Any change that weakens 1–6 needs an explicit founder decision. Leave a
> `# TODO(ARCHOICE): trust-guardrail change — needs Kevin` marker rather than quietly relaxing them.

---

## 7. Revenue interaction with the rest of the model

| Stream | Powered by this spec |
|---|---|
| Brand placement | §2 Sponsored slot + §4 CPM/CPC/category |
| Affiliate | §1 affiliate buy-button on every SKU |
| Freemium Pro | unaffected — Pro removes nothing about honesty, adds power features |
| Contractor Pro | §6.5 keeps ads out of the pro-handoff path |

Healthy-mix target _(projection, validate)_: affiliate as the dependable floor, brand
placement as the growth multiplier, with Best-Fit click-through monitored as the **trust
health metric** — if users stop clicking Best Fit, the loop is being gamed.

---

## 8. Open questions

1. **Best-Fit transparency** — do we show *why* something is Best Fit (explainability) to
   reinforce trust? (Leaning yes.)
2. **Sponsored frequency cap** — how often can a user see any sponsored slot before fatigue?
3. **Attribution window** for CPA across retailers.
4. **Disclosure copy** — exact wording/iconography that reads as honest, not buried.
