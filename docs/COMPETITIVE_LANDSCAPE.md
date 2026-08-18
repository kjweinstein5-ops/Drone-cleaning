# Competitive Landscape — California & the Southwest

> Who is already doing drone exterior cleaning in our target geography, and what that means
> for positioning.
>
> **Screened 2026-08-16 by web scan. Not exhaustive.** This market is fragmented and fast-moving;
> most operators are 1–3 person outfits that never rank in search. Treat the counts as a
> **floor, not a census** — the real number is higher.

---

## 0. The headline

**The service layer is crowded. The intelligence layer is empty.**

We found **~18 identified drone exterior-cleaning operators across CA + AZ**, including
**three already working San Diego County — one of which names Carlsbad as a core market.**

But none of them appear to be doing what PROPWASH's moat actually is: the closed
sense → fuse → prescribe → execute → verify → re-queue loop. The companies that *do* have
inspection-grade thermal analytics are **inspection companies, not cleaning companies**.

That gap is the whole strategic finding of this document.

---

## 1. California — ~14 identified

### San Diego County — our base market, already contested

| Company | What they do | Threat |
|---|---|---|
| **DronePower1** | Drone solar cleaning, DI water, purpose-built fleet. **Explicitly names Carlsbad a core San Diego market**, citing *high solar adoption on Spanish-tile roofs*. Veteran-owned | 🔴 **Direct.** That is our stated wedge, our stated base market, and our stated roof type — someone got there first |
| **CleanEdge Technologies** | Drone exterior + solar, San Diego. Targets hotels, HOAs, logistics roofs, corporate/stadium solar, municipal campuses | 🔴 **Direct.** The commercial-solar wedge |
| **South Bay Solar Cleaning** | Commercial drone washing, San Diego + SoCal; Tesla Solar Roof specialty | 🟠 Adjacent-direct |
| **California Drone Cleaning** | LA-based, services **San Diego to San Francisco** | 🟠 Statewide coverage |
| *Advanced Solar Cleaning* | Solar panel cleaning, San Diego (not drone-based) | 🟡 Incumbent to displace |

### Los Angeles / SoCal

| Company | Note |
|---|---|
| **Los Angeles Drone Wash** | Facades, rooftops, high-rise; CA + Miami |
| **Drone Wash Los Angeles** | Franchise location of DRONEWASH+ |
| **Droneworx Pro-Washing** | SoCal, "premier power washing" |
| **WashMeDrone** | Roof, window, **solar**, high-rise — SoCal **and Phoenix** |
| **AltitudeWash** | Drone window cleaning, streak-free glass |
| **Advanced Drone Solutions** | LA drone cleaning |
| **RayAccessPro** | LA drone window cleaning |

### Northern California

| Company | Note |
|---|---|
| **Maxx ECO Wash** | **FAA-certified**, positions as NorCal's leading aerial drone building-washing firm. SF Bay, Silicon Valley, Sacramento. The most professionalised operator found in CA |

---

## 2. Arizona — ~5 identified

| Company | Note |
|---|---|
| **Phoenix Drone Pros** | **10+ years flying in the Valley.** Buildings, windows, roofs, solar |
| **The Eco Drone** | Commercial across AZ — Phoenix, Mesa, Chandler |
| **Desert Drone Services** | Buildings, hotels, hospitals, stadiums, schools, churches, apartments |
| **Drone Wash Phoenix** | Franchise location of DRONEWASH+ |
| **WashMeDrone** | SoCal operator also covering Phoenix |

**Nevada, New Mexico, Utah, Colorado: not separately confirmed.** Absence of search results is
not absence of operators — assume similar density in Las Vegas and Albuquerque and verify before
treating them as open territory.

---

## 3. National players pushing into the Southwest

| Company | Why it matters |
|---|---|
| **Lucid Bots** | Not a competitor — **the category leader and our assumed vendor.** ~$34M raised, **400+ active operators across 40+ states, >$75M in operator revenue.** Every one of those operators is a potential competitor *and* a potential SaaS customer |
| **DRONEWASH+** (2021) | Nationwide, **franchise model**, already has LA and Phoenix locations. Franchising is how this market consolidates — and it moves fast |
| **Spinoff Robotics** | Tethered aerial robots: façade + **solar panel washing**. Closest to our solar wedge technically |
| **Apellix** | Tethered industrial power-wash and coating |
| **SkyWash Drones** (Houston, 2022) | Windows, façade, roof — Southwest-adjacent |

---

## 4. The adjacent category nobody has connected to cleaning

There *is* a mature drone-thermal-analytics industry. It just doesn't clean anything:

| Company | What they do |
|---|---|
| **Sitemark** | Solar inspection + drone thermography software |
| **MapperX** | AI-powered PV thermal inspection |
| **Anvil Labs** | Drone digital twins for predictive maintenance |
| **Inspekt AI** | AI drone inspections for building maintenance |
| **Folio3 AI** | Drone inspection + analytics |

These platforms already do things we have not built: automatic classification of thermal
anomalies (hotspots, diode failures, open circuits) **and visual anomalies including soiling**,
pixel-precise measurement, historical digital twins with change tracking.

**Read this carefully — it cuts both ways.**

- ❌ **Against us:** "we detect soiling from thermal + RGB" is *not* novel. It is a shipping
  feature in commercial PV inspection software. Any patent or marketing claim resting on
  soiling detection alone is weak.
- ✅ **For us:** none of them **prescribe a treatment, drive execution, or verify the result**.
  They produce a report and hand it to a human. The loop — prescription, safety gating,
  execution, verification, and *parameter adjustment from the outcome* — is still open.

**Our defensible claim is not "we see the dirt." It is "we close the loop on it."** The
sense→fuse→**prescribe→execute→verify→re-queue** chain is what nobody in either column is doing,
and CLAUDE.md §11 should be read with this in mind.

---

## 5. What this changes

### 5.1 Being "the drone cleaning company in Carlsbad" is not a position

Three operators already work San Diego County; one markets Carlsbad specifically on the
tile-roof-solar thesis. With Lucid at 400+ operators, buying a Sherpa is not a barrier to entry —
it is a purchase order. A services-only business here competes on **price, scheduling and
reputation**, none of which is defensible and none of which is what this codebase is.

### 5.2 The intelligence layer is the actual whitespace

Nobody in either column joins inspection-grade analytics to cleaning execution and verification.
That is the gap, it is where all the code in this repo already points, and it is consistent with
the SaaS line already modelled in `reports/revenue_model.py`.

### 5.3 Lucid's 400+ operators are the market, not the competition

This is the most actionable finding in the document. Those operators:

- already own the hardware — no capex to sell them;
- have no prescription intelligence, no per-surface model, no verification;
- are exactly who a licensing product is for.

**Selling to the operators beats out-competing them.** It also reframes the Lucid relationship:
we are not asking for a control API to compete with their customers, we are offering a layer
that makes their customers' fleets more valuable — a materially easier conversation
(`VENDOR_OUTREACH.md`).

### 5.4 The verification product may be the wedge, not the wash

`FIELD_OPERATIONS.md` §3 already found that scan-only is viable revenue with **no spray
liability**. This landscape strengthens that: the scanning/reporting layer is uncontested in
cleaning, needs no Part 107 spray operation, no water, no containment, no damage exposure — and
it is the half of the business that is actually differentiated.

---

## 5.5 Does the Sherpa map the building? **No.** ⭐

*Checked 2026-08-16 against Lucid's own product pages.*

This matters more than any other single capability question, so it was checked directly rather
than assumed.

| Question | Finding |
|---|---|
| Does the Sherpa map / 3D scan / survey? | **No.** No mapping, 3D scanning, reality capture or surveying appears anywhere in Lucid's Sherpa material |
| Is it autonomous? | **No.** *"The Sherpa Drone is operated by a single pilot with one ground crew member,"* requiring **FAA Part 107** certification |
| What sensing does it have? | Collision-avoidance radar (0.5–50 m per earlier vendor material). **Obstacle avoidance, not mapping** — the same distinction as laser rangefinder ≠ LiDAR |
| SDK / API / developer program? | **None published.** The only software offering on the product page is *Sherpa Academy*, a training course |
| Their `/platform` page | Returns **404** |
| The "Smarter, Swifter, and Open to All" post | An **industry roundup**, not a product announcement. Its RTK sub-inch site models and 3D Gaussian splatting language describes **competitors' drones**, not Lucid products |

### What this means

**1. The mapping layer is wide open.** The Sherpa is a spray tool that sprays where a pilot
points it. It has **no model of the building, no per-surface knowledge, and no record of what was
cleaned.** Everything PROPWASH does upstream of the nozzle is uncontested by the category leader.

**2. It validates the two-drone architecture** (CLAUDE.md §6). Scout maps, cleaner sprays, both
sync through the plan. **Lucid has no scout.** To close the loop they would need a sensing
aircraft, a photogrammetry pipeline, a per-surface model and a verification stage — which is the
entire contents of this repository.

**3. It reframes "Lucid doesn't allow integration."** They are not blocking you. **There is
nothing to integrate into** — no API, no addressable onboard compute, no map to enrich. The
Sherpa is a well-built end-effector on a human-piloted airframe.

### ⚠️ The caveat that keeps this honest

**Lavo AI is marketed as an autonomous pressure-washing robot.** A ground robot that navigates
autonomously needs SLAM — so **mapping competence exists inside Lucid**, it is simply not in the
Sherpa product. They also acquired the autonomy company Avianna, and just raised $20M.

**So this is a current-product gap, not a capability gap.** It is a real opening, and it is the
opening most likely to close from their side. That is already logged as a kill criterion in
`GO_NO_GO.md` §3 — *"Lucid ships per-surface prescription + verification inside Lucid Refresh."*
Add mapping to that trigger.

---

## 6. Honest limits of this scan

- **Web search only.** No state business registries, no trade-association lists, no USPTO.
- **Undercounts badly.** Small operators without SEO are invisible here. The true CA + AZ count
  is likely **2–3× what we found**.
- **NV / NM / UT / CO unverified.** Do not treat as open territory.
- **No revenue, headcount or fleet data** for any regional operator — we cannot tell a
  one-drone side business from a real firm.
- **Capability claims are their marketing**, not verified. "AI-powered" on a cleaning company's
  site usually means route planning, not a fusion model.

**Before acting on this:** pull the state business registries for CA and AZ, and — the fastest
signal available — **ask Lucid how many of their 400+ operators are in Southern California.**
That single number tells you more about the competitive density of the base market than any
amount of searching.
