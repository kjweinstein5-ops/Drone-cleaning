# Airframe contenders — the full screened field

> *"What other drones might be a contender to envelop this tech stack?"*
>
> Extends `VERDICT_AND_PRICES.md` with everything screened, including three not looked at before.
> Screened 2026-08-16.

---

## ⚠️ Correction: the Raptor IS a real drone

Last turn I said no cleaning drone called Raptor exists and assumed you meant Raptor Maps.
**Both were half right.** There is a real aircraft: the **Anzu Robotics Raptor** and **Raptor T**.

**But the answer is still no, for four independent reasons:**

| | |
|---|---|
| **Discontinued** | Anzu announced in **Feb 2026** that the Raptor line is **no longer available** — component shortages stalled production. They are pivoting to a "next generation" product |
| **DJI-derived** | Built under a **technology licensing agreement with DJI**, manufactured in Malaysia. The whole premise was being a DJI alternative — which is a fragile place to stand given §0 of `FLEET_ARCHITECTURE.md` |
| **NDAA status "mixed"** | Chinese-sourced components remain, including **the thermal sensor on the Raptor T**. Anzu acknowledged the concern |
| **Wrong class entirely** | Mavic-3-class small aircraft. Not a heavy lifter — it could never carry a cleaning payload |

**Verdict: ❌ dead on arrival.** Discontinued, compliance-ambiguous, and the wrong size regardless.

---

## ⭐ The strongest contender I had not screened: Harris Aerial Carrier H6 Hybrid

A **gas-electric hybrid** heavy-lift hexacopter, and the endurance figures are in a different league.

| | Carrier H6 Hybrid EFI |
|---|---|
| Power | **H2400 EFI gas-electric generator** — also runs fully electric |
| Endurance | **2.5 hours @ 4 kg payload** · 1.5 hours @ 5 kg max |
| Deploy | Folds; flight-ready in **under two minutes** |
| Family | **Carrier H6HL** (40 kg heavy-lift) · **H6 Hydrone** (hydrogen fuel cell) · H6 Electric |
| NDAA / Blue | ⚠️ **Not confirmed** |
| Price | ⚠️ **Not published** |

**Our airborne payload with tethered water is 3–5 kg — right in its sweet spot.**

### But I checked the actual benefit, and it's smaller than it sounds

| Job | Alta X (20 min) | IF1200A (43 min) | H6 Hybrid (150 min) |
|---|---|---|---|
| **Reference house** — 114 min spray | 4.7 swaps, **14 min lost** | 1.7 swaps, **5 min lost** | **0 swaps** |
| **Large commercial** — 8 h flight | 23 swaps, **69 min lost** | 10 swaps, **30 min lost** | 2.2 swaps, **7 min lost** |

**On a house, endurance saves ~14 minutes of a ~3.7 hour day — about 6%.** Fixed setup, briefing,
pre-flight and pack-down (~100 min) dominate, so swaps barely move the total.

**On an 8-hour commercial job it saves about an hour** — and that is exactly the segment
`GO_NO_GO.md` re-aimed at.

### ⚠️ Three problems specific to *our* use

1. **Exhaust over freshly cleaned surfaces.** A petrol generator hovering above glass and solar
   panels you have just cleaned deposits combustion products on them. **This may be
   disqualifying for solar and glass work** and I have seen nothing addressing it.
2. **Noise.** A gas engine over a residential or commercial property is an HOA and neighbour
   problem in a way an electric multirotor is not.
3. **Water + fuel + electronics on one airframe** is a materially worse risk profile than
   batteries alone.

**The H6 Hydrone (hydrogen fuel cell) sidesteps exhaust and noise** — worth asking about — but
adds hydrogen logistics, which is its own operational world.

> **Verdict: ❌ RULED OUT — Kevin's decision, 2026-08-16.** No hybrid cleaning drone.
>
> The endurance was real, but it was buying ~14 minutes on a house (6% of the day), and the
> exhaust question was never answered. **The propulsion decision is now: all-electric, battery.**
> That also takes the **H6 Hydrone** off the table — hydrogen is not a hybrid, but it is not a
> battery either, and it carries its own fuel logistics. *(Say so if you want hydrogen kept live.)*
>
> **This closes the propulsion question. It does not change the buy list** — both recommended
> aircraft were already all-electric.

---

## Ascent AeroSystems Spirit — the compliance outlier

| | |
|---|---|
| **Blue UAS** | **The only airframe on BOTH the Blue UAS Cleared List (complete system) AND the Blue UAS Framework (vetted component)** |
| Architecture | **MOSA-ready, open-system**, modular payload interface — reconfigure payloads without re-engineering the aircraft |
| Form | Coaxial rotor; **all-weather**; takes off from any terrain |
| Capacity | **10 lb for batteries *and* payload combined** |
| Origin | US (Massachusetts) |

**Too small to clean.** Ten pounds shared between batteries and payload leaves nothing for a gun,
hose and computer.

**But its dual Blue listing is the strongest compliance position of anything screened**, and
*all-weather* is interesting for a **scout** — our scan window is already narrow
(`FIELD_OPERATIONS.md` §2.1), and an aircraft that flies in conditions the X10D won't could widen it.

> **Verdict: 🔬 not a cleaner. Possible bad-weather scout.** Low priority.

---

## The complete field

| Aircraft | Role | Integrable | Compliance | Verdict |
|---|---|---|---|---|
| **Skydio X10D** | Scout | ✅ | ✅ Blue Cleared | ⭐ **BUY** — ~$16K |
| **Inspired Flight IF1200A** | Cleaner | ✅ open PX4 | ✅ Blue **+ Green** | ⭐ **BUY** — ~$32K |
| Freefly Alta X Gen2 | Cleaner | ✅ Auterion SDK | ⚠️ ETP lapsed Feb 2026 | Backup — best onboard-app story |
| Watts PRISM Sky | Cleaner | ✅ Auterion | ⚠️ Blue unconfirmed | Backup — rails top *or* bottom |
| ~~Harris Aerial H6 Hybrid~~ | Cleaner | ⚠️ | ⚠️ | ❌ **RULED OUT** — no hybrid (Kevin, 16 Aug) |
| ~~Harris H6 Hydrone~~ | Cleaner | ⚠️ | ⚠️ | ❌ Out under the same all-electric rule |
| Ascent Spirit | Scout | ✅ MOSA | ✅✅ **dual Blue listing** | 🔬 All-weather scout only; too small to clean |
| Parrot ANAFI USA | Scout | ⚠️ limited | ✅ Blue | Budget scout |
| Custom PX4 build | Cleaner | ✅ total control | ⚠️ your sourcing | Later — you own airworthiness |
| **Anzu Raptor / Raptor T** | — | ⚠️ | ⚠️ mixed | ❌ **Discontinued Feb 2026** |
| Lucid Sherpa | Cleaner | ❌ no API | ✅ | ❌ The thing we left |
| DJI M350 / M400 | Cleaner | ⚠️ PSDK only | ❌ **Covered List** | ❌ Closed |
| Apellix | Cleaner | ⚠️ vendor-closed | ✅ US | ❌ Industrial tanks, not façades |

---

## What actually decides this — ranked

After screening thirteen platforms, the ranking of what matters is **not** what a spec sheet
leads with:

1. **Will the vendor support a liquid spray payload?** ⚠️ Disqualifies faster than any spec.
   Water, electronics and rotors is not a camera gimbal.
2. **Compliance you can point at** — Blue listing or documented >65% US content. One of only two
   FCC exemptions, and **both expire 1 Jan 2027**.
3. **Openness** — can our code reach the actuators and read telemetry?
4. **Endurance** — matters ~6% on a house, ~1 hour on a commercial job.
5. **Payload** — barely matters. A tethered rig needs 3–5 kg, and everything here clears it.

**Payload capacity is the spec every vendor leads with and the one that matters least to us.**
That is what the water tether bought.

## ✅ DECIDED — propulsion

**All-electric, battery only. No hybrid, no combustion.** (Kevin, 2026-08-16.)

Rationale, recorded so it doesn't get re-litigated:

- **Exhaust over freshly cleaned glass and solar** was never resolved, and solar is the most
  failure-sensitive surface we touch. Depositing combustion products on a panel you just cleaned
  inverts the whole product.
- **The endurance gain was small where we actually work** — ~14 min of a 3.7 h house job.
- **Noise** over residential and commercial property is an HOA and neighbour problem.
- **Fuel + water + electronics** on one airframe is a worse risk profile, and we own the
  airworthiness of any self-integration.

Both recommended aircraft — **Skydio X10D** and **Inspired Flight IF1200A** — are already
all-electric, so **the buy list is unchanged.**

**The endurance problem doesn't go away; it moves to the ground.** Batteries and a fast charger
are the answer (`FIELD_OPERATIONS.md` §5.1), and at 43 min the IF1200A needs only ~2 swaps on a
house job. Buy enough batteries that swapping never blocks the job.
