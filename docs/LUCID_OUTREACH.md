# Lucid Bots — partnership outreach & questions

> Purpose: resolve the single biggest strategic unknown in PROPWASH (CLAUDE.md §7, §15.1).
> Posture: **transparent partnership**, not circumvention. We integrate *with* Lucid and *within*
> FAA Part 107. Prefer a vendor-friendly relationship over clever workarounds.

## Who to contact
- Lucid Bots — partnerships / developer relations / Lucid Refresh product team.
- Goal of first contact: a 30-minute intro call to understand the integration surface.

## The framing (lead with value to them)
> "We've built an AI orchestration + verification layer for exterior cleaning that produces
> measured before/after results. We want our customers to buy and run more Sherpas, and we want to
> integrate transparently with Lucid Refresh. We're exploring whether we can read job data — and
> ideally hand structured work orders to operators — through your platform."

Position PROPWASH as **demand generation for Sherpas**, not a threat to their autonomy stack.

## Questions to ask (in priority order)

### A. Lucid Refresh API (Path A — what we build first)
1. Does Lucid Refresh expose an API? REST/GraphQL/webhooks?
2. Can we **read** job data programmatically (status, telemetry, completion, location)?
3. Can we **push** structured work orders / job packets into Refresh for an operator to execute?
4. What auth model (API keys, OAuth, per-fleet tokens)? Rate limits? Sandbox?
5. Data ownership — who owns the job/telemetry data generated on a customer's Sherpa?

### B. Control surface (Path B — best case, unverified)
6. Is there any supported way to send pump/pressure/dwell setpoints to the Sherpa?
7. Any MAVLink or documented control endpoint, even partner-gated?
8. If not today — is it on the roadmap? Under what partnership terms?

### C. Companion / retrofit (Path C — last resort, constrained)
9. What is Lucid's policy on companion computers or third-party hardware on owned Sherpas?
10. Warranty implications? Required reviews?
11. Would Lucid co-develop a sanctioned operator-assist capability (with the appropriate FAA pathway)?

### D. Commercial / partnership
12. Is there a partner/reseller program? Referral economics?
13. Would Lucid co-sell to operators who want our intelligence layer on their fleet?
14. Any exclusivity or restrictions we should know before we build on Refresh?

## What we will NOT ask for / build
- Anything that conceals autonomous operation from Lucid or the FAA.
- Anything that circumvents Part 107 or keeps the operator out of genuine command (§7, §10).

## Decision gate (after the call)
- **API to read + push work orders** → double down on Path A; it's a real integration.
- **Read-only** → Path A with manual work-order handoff; revisit B later.
- **Open to control partnership** → scope Path B behind a feature flag + capability check.
- **No partnership appetite** → reassess: license our platform to their operator base *with* their
  blessing, or treat Lucid as one swappable transport among several drone vendors.
