# PROPWASH — How to Protect Your IP (so it can't be copied)

> ⚠️ **This is founder strategy, NOT legal advice.** Patents, trademarks, and trade-secret
> enforcement are jurisdiction- and fact-specific. **Engage a registered patent attorney and an IP
> attorney before filing or relying on any of this.** (CLAUDE.md §11.) This doc tells you *what to
> protect and how to think about it* so your conversation with counsel is fast and cheap.

---

## 0. The honest headline

**Nothing is 100% theft-proof.** Anyone telling you otherwise is selling something. What you *can*
build is **layered protection** where each layer covers a different attack, so copying you becomes
slow, expensive, legally risky, and — most importantly — **always one data-cycle behind.** That last
part is the real moat. Read §2 carefully.

---

## 1. The five kinds of IP and how each maps to PROPWASH

| IP type | Protects | Lasts | Your PROPWASH asset | Strength here |
|---|---|---|---|---|
| **Trade secret** | Secret, valuable info | Forever (while secret) | Grime/fusion scoring model, calibrated surface/pressure table, learning model, verification thresholds | ⭐⭐⭐⭐⭐ **Your #1** |
| **Utility patent** | A novel, non-obvious *method* | ~20 yrs | The closed loop: sense→fuse→prescribe→execute→verify→**re-queue with adjusted params** | ⭐⭐⭐⭐ |
| **Copyright** | Code & written expression | Life+ / 95 yrs | The codebase, ROI reports, docs | ⭐⭐⭐ (automatic) |
| **Trademark** | Brand identifiers | Forever (while used) | The name **PROPWASH**, logo | ⭐⭐⭐ |
| **Contracts** | Relationships/people | Per contract | IP assignment, NDAs, customer data rights | ⭐⭐⭐⭐ (the glue) |

---

## 2. The genius move: patent vs. trade secret (you can't do both for the same thing)

A patent **requires public disclosure** — you teach the world how it works in exchange for ~20 years
of exclusivity. A trade secret is the opposite: it's protected **only as long as it's secret.** So
the strategic question for *each* piece of IP is: **can a competitor figure this out by watching your
product work?**

- **If YES (observable / reverse-engineerable) → patent it.** A drone flying a sense→clean→re-scan→
  re-clean loop in a customer's backyard is *observable*. Someone will see the method. Patenting the
  **method** (especially "verification-driven parameter adjustment" — re-cleaning failed zones with
  automatically-adjusted pressure/chemistry) stakes your claim before a competitor can.
- **If NO (hidden inside your servers) → keep it a trade secret.** Your **grime-scoring model, the
  calibrated surface/pressure numbers, the learning weights, the verification thresholds** never leave
  your backend. Nobody can see them by watching a drone. Patenting them would just *teach competitors
  your secret sauce.* **Keep these as trade secrets — possibly forever.**

> **Rule of thumb:** Patent the *choreography*. Keep the *brain* secret.

This split is exactly what CLAUDE.md §11 already intends — this doc just makes the reasoning explicit.

---

## 3. The strongest moat isn't legal — it's the data flywheel

Patents and secrets are defense. The **data flywheel** is offense, and for an AI/ML business it's
usually more defensible than either:

```
more jobs → more thermal+RGB+outcome data → better-calibrated prescriptions
→ higher first-pass PASS rate → cheaper, better cleans → win more jobs → (repeat)
```

A competitor who copies your *method* still starts at **zero data**. Your surface/pressure table and
learning model are calibrated on every real job you've ever run (your trade secrets, §11). They can't
replicate that without running the same volume of jobs — which takes years. **Protect the data itself:**

- Lock the database (encryption at rest + in transit, least-privilege access, audit logging).
- In customer contracts, secure **your right to use job/sensor data** to improve your models.
- Treat the accumulated dataset as a crown-jewel trade secret: need-to-know access only.

---

## 4. Trade-secret protection — the checklist (this is where 80% of your moat lives)

Trade-secret law (e.g. the US Defend Trade Secrets Act + state UTSA) **only protects you if you took
reasonable steps to keep it secret.** Do these, and document that you did:

- [ ] **Mark it.** Label the model code, prescription tables, and thresholds `CONFIDENTIAL — PROPWASH TRADE SECRET`.
- [ ] **Access control.** Need-to-know only. Separate the secret model/data from the rest of the repo; restrict who can read it.
- [ ] **Encrypt** secrets at rest and in transit; no secrets in public repos, screenshots, or marketing.
- [ ] **NDAs** with every employee, contractor, advisor, investor (mutual), and vendor (incl. Lucid before deep talks).
- [ ] **IP assignment** in every employee/contractor agreement (see §7) — so what they build is *yours*.
- [ ] **Offboarding.** Revoke access immediately; exit interview reminding of continuing obligations.
- [ ] **Don't publish the secret sauce.** No patent, blog, talk, or pitch deck that reveals the scoring model, calibration numbers, or thresholds. (Reinforces CLAUDE.md §5/§11: also don't *overclaim* — honesty protects you legally too.)
- [ ] **Vendor/cloud hygiene.** Review that your cloud/API providers don't acquire rights to your data.

---

## 5. Patent strategy — concrete steps

1. **Document invention dates now.** Your git history + dated design notes establish when you invented
   what. Keep them.
2. **Don't publicly disclose before filing.** Public demos, sales pitches, or posts can start clocks or
   destroy novelty in some countries. **File before you broadly disclose.** (The US has a limited
   1-year grace period; many countries have *none* — so file first if you want international rights.)
3. **File a provisional** on the *method* (sense→fuse→prescribe→execute→verify→re-queue, with
   verification-driven parameter adjustment). Low cost, gives ~12 months + "patent pending," sets a
   priority date. **Verify current USPTO fees** and have an attorney draft/scope claims.
4. **Within 12 months**, convert to a full **utility** application once the method is field-proven.
5. **Consider international** (PCT) only if you'll operate/license abroad — it's expensive.
6. **Be honest in claims (§11).** Don't claim "multispectral detection" (you have thermal+RGB only, §5)
   or "fully autonomous" (operator in command, §7). Overclaiming can invalidate a patent and create
   liability. Honest, narrow, defensible claims beat broad fragile ones.

> A provisional is a **priority placeholder, not enforceable protection by itself.** It buys you time
> and a date. Real protection comes from the granted utility patent.

---

## 6. Copyright & trademark — cheap, do them

- **Copyright** is automatic the moment you write the code/reports. For stronger enforcement (and
  statutory damages in the US), **register** key works with the Copyright Office — inexpensive.
- Put a copyright notice + a `LICENSE` (keep the repo **private/proprietary** — no open-source license).
- **Trademark PROPWASH**: search first (USPTO TESS + common-law), then file in likely classes —
  **37** (cleaning/maintenance services) and **42** (software/SaaS), per §11. Use the ™ symbol now; ®
  only after registration. You trademark the **brand**, never "the idea."

---

## 7. Contracts — the glue that makes the rest enforceable

This is where founders lose IP without realizing it. Get these in place **before** anyone touches the code or data:

- **Employee/contractor IP assignment + invention assignment:** everything they create for PROPWASH
  belongs to PROPWASH. *Especially critical for any contractor/freelancer* — absent this, a contractor
  may *own* what they build for you.
- **Confidentiality / NDA** for everyone with access.
- **California note (important — you're in San Diego):** California generally **bans non-compete
  agreements** (Bus. & Prof. Code §16600). So **do not rely on non-competes.** Rely instead on
  trade-secret law, IP-assignment agreements, NDAs, and access control. This is a real constraint —
  confirm with counsel.
- **Customer contracts:** secure your right to capture and use job/sensor data for model improvement;
  clarify data ownership.
- **Founder IP assignment:** if PROPWASH is/becomes a company, **assign your own pre-formation IP to
  the entity** so the company (not you personally) owns it — investors will require this anyway.

---

## 8. Operational security (don't get robbed the dumb way)

- Private repos; 2FA everywhere; least-privilege cloud roles; secrets in a vault, never in code.
- Separate the trade-secret model/data behind tighter access than the rest of the codebase.
- Be careful what goes in pitch decks, demos, and conference talks — assume anything shown publicly is public.
- Background-check key technical hires; stagger access to crown-jewel data.

---

## 9. What to do THIS QUARTER (priority order)

1. **IP assignment + NDA** for yourself and anyone who has touched this (cheap, urgent, prevents the worst losses).
2. **Lock down trade secrets** (§4 checklist) — especially separating the scoring model/calibration data.
3. **Talk to a patent attorney** about a provisional on the method **before** any public demo/pitch.
4. **Trademark search** on PROPWASH; file classes 37 + 42.
5. **Register copyright** on the core codebase.
6. **Secure data rights** language in your first customer contracts.

---

## 10. The mental model to remember

- **Patent** the loop a competitor can *see*.
- **Keep secret** the brain a competitor *can't* see.
- **Out-run** everyone with the **data flywheel** they can't replicate without your job history.
- **Contract** every human so the IP is unambiguously yours.
- **Stay honest** in every claim — overclaiming is itself a legal risk (§5, §7, §11).

Layered like this, copying PROPWASH means: reinventing the method (you patented it), guessing the
models (you kept them secret), AND collecting years of field data from scratch (your flywheel) —
all while you keep pulling further ahead. That's as close to "can't be stolen" as a real business gets.
