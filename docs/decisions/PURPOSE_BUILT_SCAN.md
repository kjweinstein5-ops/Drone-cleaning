# Deep dive — every purpose-built cleaning drone, and why none of them fit

> *"Do a deep dive and find a drone that fits perfectly with what I want."*
>
> This is the search I should have run before recommending a self-integration. Screened
> 2026-08-16 across **every** purpose-built cleaning-drone manufacturer I could identify.

---

## The finding, up front

**Not one purpose-built cleaning drone manufacturer publishes an SDK, an API, or any third-party
software integration path. Not one.**

That is not a gap in my search. **It is the structure of the industry.** Every maker of a cleaning
drone is trying to own the intelligence layer themselves, because the intelligence layer is where
the value is. They will sell you the aircraft. They will not let your software drive it.

**So "a cleaning drone that fits perfectly" does not exist to be bought.** The closest thing is an
open general-purpose airframe with our payload on it — which is the IF1200A recommendation, now
supported by evidence rather than assumption.

---

## Every maker, checked

| Manufacturer | Where | Electric? | Sells the aircraft? | Integration path | Verdict |
|---|---|---|---|---|---|
| **Lucid Bots** — Sherpa | Charlotte, NC | ✅ | ✅ $75K / $2,950 mo | ❌ **No API.** Autonomy in-house; acquired an AI company | ❌ |
| **Apellix** — Power/Soft Wash | Jacksonville, FL | ✅ **8 batteries + 2 rapid chargers** | ✅ **B1 $34K · X1 tethered $79K** | ❌ None documented — **and they sell competing AI software** | 🔬 Worth one call, lower odds |
| **Foxtech** — AeroClean | China | ✅ | ✅ | ❌ DJI PSDK only | ❌ 100–200 bar, DJI-mount |
| **Spinoff Robotics** — ALICE, METRON | Singapore | ✅ tethered | ❌ **Managed service only** | ❌ You never own hardware | ❌ Competitor, not supplier |
| **Aerones** | Latvia | — | — | — | ❌ **Drone projects on hold indefinitely** |
| **Aquiline Drones** | Hartford, CT | ✅ | ✅ | ⚠️ not surfaced | 🔬 Unscreened |
| **Kärcher** | Germany | — | — | ⚠️ not surfaced | 🔬 Unscreened |
| **Kite Robotics** | Netherlands | — | — | ⚠️ not surfaced | 🔬 Window-focused |
| **SIR Robotics** | — | — | — | ⚠️ not surfaced | 🔬 Unscreened |
| **Skyline Robotics** — Ozmo | US/Israel | — | ❌ crane-mounted, not a drone | — | ❌ Different machine |
| **SkyWash · DRONEWASH+ · MWE · Alpha Drones** | US | — | equipment/services | ❌ | ❌ Operators, not platforms |

**Market context:** Apellix's Power Wash Drone is **the most widely deployed commercial cleaning
drone worldwide** — active operators in 21 countries across 5 continents. Lucid's Sherpa is the
most deployed in **North America** — 400+ operators, 40+ states. Those two are the category.
Neither will let our stack in.

---

## ⭐ The one worth a phone call: Apellix

Everything about Apellix fits **except** the integration path, and unlike Lucid there is reason to
think that is negotiable.

| | Apellix |
|---|---|
| Origin | **US — Jacksonville, Florida** |
| Power | ✅ **All-electric.** 8 batteries + 2 rapid chargers shipped with each drone, ~32 min per battery — **explicitly designed for continuous all-day operation** |
| Products | Power & Soft Wash (up to 4,000 PSI, 11 GPM) · Spray Painting & Coating · CBRN Decon |
| Pressure | "**Up to** 4,000 PSI" implies a variable range that should reach our 1.8–7 bar soft-wash band — **needs confirming** |
| Model | **Sells the aircraft.** B2B equipment sales, customers build businesses on them |
| Deployment | **Most widely deployed cleaning drone in the world** |
| Integration | ❌ **No API/SDK documented** |

### Why they might say yes where Lucid says no

- **Their positioning is software-controlled aerial robotics**, not "a drone with a hose." That is
  philosophically our argument.
- **They are not racing us.** Lucid raised $20M explicitly to build "America's leading exterior
  cleaning platform" and is shipping autonomy (Lavo AI, Avianna acquisition). Apellix shows no such
  play — which makes an intelligence partner *complementary* rather than competitive.
- **Their battery architecture already solves our field problem.** 8 batteries and 2 rapid chargers
  per aircraft is exactly the answer to the swap burden, shipped as standard.
- **They are smaller.** Smaller companies do bespoke integrations.

### 💰 Apellix pricing — found

| Configuration | Price |
|---|---|
| **B1 — battery, base model** | **$34,000** |
| **X1 — tethered** | **$79,000** (includes power station + 300 ft of wire) |
| Drone + accessories | $47,000–$75,000 |
| Complete startup package (incl. ~$30K window-capable ground equipment) | **$75,000–$105,000** |

Financing is offered. **Add-ons:** Night Flight LED bar · **Soft-wash Ball Valve** ·
**Apellix Intelligence (AI) Premium** · Certified Parachute System · Extended Warranty.

### B2 specifications

| | Apellix B2 Power & Soft Wash |
|---|---|
| Pressure | Up to **4,000 PSI** — ⚠️ **minimum not published** |
| Flow | Up to **11 GPM** |
| Power | Battery, **8 high-capacity batteries included** |
| Max height | 195 ft / 60 m |
| Weight | 21.5 lb bare · **55 lb all-up class** |
| **Payload** | **25 lb** |
| Autonomy | **"Obstacle detection and front distance hold"** |

**Two things stand out.** *Front distance hold* is **standoff hold** — one of the airborne items
on our own BOM, already solved. And a **Soft-wash Ball Valve** being a catalogue option means
soft-wash is a supported mode, not an improvisation.

### ⚠️ But: they sell "Apellix Intelligence — Autonomous cleaning software"

This materially lowers the odds of a partnership, and it is the honest downgrade to my
enthusiasm last turn.

**Apellix is building the intelligence layer too.** It is a priced add-on described as
*autonomous cleaning software*. That puts them on the same trajectory as Lucid — and it means
PROPWASH would not be a complementary partner but **a competitor to a product they already sell.**

The call is still worth making. The odds are now lower than I implied.

### 💵 Price comparison — closer than expected

| | Apellix B1 | Inspired Flight IF1200A |
|---|---|---|
| Aircraft | **$34,000** | **$32,000** |
| Cleaning payload | ✅ **included and proven** | ➕ ~$3,000–$6,000 in parts |
| Integration labour | ✅ none | ➕ ours |
| **All-in for a working cleaner** | **~$34,000** | **~$37,000+** |
| Batteries | ✅ 8 + 2 rapid chargers | ➕ extra |
| Standoff hold | ✅ front distance hold | ➕ we add a rangefinder |
| **Our software can drive it** | ❌ | ✅ |
| Blue UAS | ⚠️ unconfirmed | ✅ Blue + Green |

**Apellix is cheaper, all-in, for a working cleaning drone.** The entire premium on the IF1200A
buys one thing: **the right to run our own stack.**

Given `GO_NO_GO.md` concluded the software *is* the company, that is the right trade — but it is a
much narrower call than it looked, and it turns almost entirely on question #2 below.

### The three questions to ask them

1. **What is the minimum controllable pressure**, and can it be commanded — not just set by hand?
2. **Will you expose any control or telemetry interface** to a software partner: MAVLink,
   serial, an API, anything?
3. **Will you support a customer-integrated sensing payload** on the aircraft?

> **If Apellix answers yes to #2, they become the recommendation.** It would give us a purpose-built,
> all-electric, US-made, field-proven cleaning aircraft *and* an integration path — the perfect fit
> that does not otherwise exist.
>
> **If they answer no, the IF1200A stands**, and now on evidence: we asked the whole category.

---

## Why the category is closed — and why that is good news

Every one of these companies is doing the same thing: selling the *machine* while keeping the
*decisions*. Lucid keeps autonomy in-house. Apellix publishes no API. Spinoff won't even sell you
hardware — they fly it for you.

**They are all protecting the same thing we are building.** That is the strongest possible evidence
that the intelligence layer is the valuable part.

It also means the moat is not "we have a special drone." **Nobody has a special drone.** The moat is
that we are the only ones who will have the per-surface model, the safety-gated prescription, the
audit trail and the verification loop — and we can put it on any airframe that lets us in.

**That is why the airframe must be open, and why the open one is a general-purpose heavy lifter.**

---

## Where this lands

| | |
|---|---|
| **Buy** | **Inspired Flight IF1200A** — ~$32K, all-electric, Blue + Green certified, open PX4, 43 min |
| **Before that** | **Call Apellix.** One conversation, three questions. It is the only path to a purpose-built aircraft our stack can drive |
| **Ruled out** | Lucid (no API) · Foxtech (pressure + DJI) · Spinoff (service only) · Aerones (on hold) · hybrids (Kevin, 16 Aug) |
| **Still unscreened** | Aquiline Drones · Kärcher · Kite Robotics · SIR Robotics — smaller odds, worth a look if Apellix says no |

> `TODO(PROPWASH): call Apellix before ordering the IF1200A. Three questions, one call, and it
> either changes the recommendation or confirms it.`
