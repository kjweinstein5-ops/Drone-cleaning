# ARCHOICE

> **A separate venture, not part of PROPWASH.** This folder is intentionally isolated from the
> drone-cleaning platform in the rest of this repository. ARCHOICE is its own business and will
> likely move to its own repo.

**ARCHOICE** = **AR** + **CHOICE** — an AR-first home-improvement app. Point your phone at a
broken thing; AI diagnoses the problem, plans the fix, recommends exactly what to buy, and
guides execution or hands off to a vetted pro.

**Point → Diagnose → Plan → Choose → Execute / Delegate → Verify.**

## Contents

| File | What |
|------|------|
| `business-plan.md` | Master business plan: problem, product, competitive landscape, model, projections, GTM, tech, brand, risks, roadmap. |
| `landing/index.html` | Self-contained marketing landing page (no build step). |

## View the landing page

Open `landing/index.html` in a browser, or serve it:

```bash
cd archoice/landing && python3 -m http.server 8000
# → http://localhost:8000
```

The waitlist form stores emails in browser `localStorage` only — **no backend is wired yet.**

## Honesty notes (read before quoting anything)

- All financials in the business plan are **projections**, not traction.
- The "42% faster decision-to-purchase" stat is a **secondary-source estimate** pending
  first-party validation.
- Regulated trades (electrical, gas, structural, roofing) must route to **licensed pros** —
  the app does not give unsafe DIY guidance.
