# Payload Build Spec — the complete wash kit

> **Rev B · 4 Sep 2026.** Supersedes Rev A (airborne payload only).
> Aircraft, airborne payload, ground rig, water train and chemistry — one costed kit.
>
> Prices are public list, **subject to quote — none of this is a bid.** Pressure and dwell
> values come from `prescriptions/surface_treatment_v1.json` and remain **uncalibrated
> starting assumptions** (CLAUDE.md §9). Nothing here is legal, aviation-regulatory or
> insurance advice.
>
> Rendered version with drawings: `samples/payload_build.html`

---

## 0. The three answers

### 0.1 Which aircraft — and why the bigger one is worse

**Inspired Flight IF1200A.**

The counter-intuitive part: the Freefly Alta X advertises **33.2 lb** of payload against the
IF1200A's **19.1 lb**, and it is still the wrong choice — because the Alta X only reaches that
number *above* the 55 lb Part 107 ceiling.

### 0.2 No second rig for foam — but a second water path

Two findings got tangled together in the question.

- **Foam:** at soft-wash pressure you cannot make clinging foam with hardware. Venturi foam
  cannons need roughly **1,000+ psi**; we run **60–100 psi**. Cling comes from the chemistry —
  a thickened surfactant package. **A purchase-order change, not an equipment change.**
- **The real split is DI vs. detergent**, driven by solar, not glass. A second hose would cost
  the entire payload budget, so: **one hose, two sources, and a sequencing rule.**

### 0.3 Inside houses — no

The IF1200A is 1.2 m across the frame, ~1.6 m across the props. There is a real indoor market,
but it is **dry work** on a **small caged aircraft with visual-inertial navigation**, sharing no
parts with this build. Separate program.

---

## 1. The aircraft

Part 107 caps the **whole aircraft** at 55 lb / 25 kg — airframe, batteries, payload, everything.
So the only payload number that means anything is **25 kg minus what the aircraft weighs with the
batteries it needs to be useful.** Advertised "max payload" figures are quoted at maximum gross
takeoff weight, which for larger airframes sits well above the Part 107 line.

| Aircraft | Airframe + batteries | Usable under Part 107 | Advertised max |
|---|---|---|---|
| **IF1200A** (hexacopter) | 16.3 kg | **8.66 kg / 19.1 lb** | 28.7 lb with certification |
| Alta X (quadcopter) | 19.8 kg | ~5.20 kg | 33.2 lb @ 34.9 kg MTOW |

**The smaller aircraft gives 66% more usable payload.** Inspired Flight publishes 19.1 lb as its
Part 107 figure, meaning they have already done this subtraction. A tethered wash payload needs
4–5 kg, so 8.66 kg is comfortable and 5.2 kg is not.

### 1.1 Deliberately not on the list: prop guards

The instinct near a wall is to cage the props. On a 1.2 m hexacopter a full guard set is
**0.8–1.5 kg** — 10–17% of the entire payload budget — and it buys less than it appears to,
because a guard that touches stucco still upsets the aircraft.

**Standoff is the better control:** the co-aligned rangefinder feeding a deterministic Tier-1
minimum-distance hold (CLAUDE.md §2). A safety check that cannot be talked out of its job by an
agent, and it weighs nothing.

`TODO(PROPWASH): revisit if field data shows contact incidents.`

---

## 2. The airborne payload

### ⚠️ The constraint that shapes everything: the hose is the payload

Equipment comes to **4.10 kg**, leaving **4.56 kg** of the aircraft's 8.66 kg limit. A 3/8" hose
full of water weighs **0.211 kg per metre**.

**That is 21 metres of unsupported hose and no more.** At 40 m the hose alone is 8.4 kg — it
exceeds the entire payload before you attach a single fitting.

**So the ground tether-management system is a load-bearing structural element, not an accessory.**
It must carry the hose weight and present near-zero tension at the aircraft.

| Hose ID | Charged mass | Max unsupported @ 4.56 kg |
|---|---|---|
| 1/2" | 0.347 kg/m | 13.1 m |
| **3/8"** | **0.211 kg/m** | **21.6 m** |
| 5/16" | 0.160 kg/m | 28.5 m |

### 2.1 How the gun attaches — forward boom, not drop bracket

A drop mount puts the nozzle **inside the rotor downwash**, which atomises the spray and blows it
back over the aircraft, and it sets a **90 mm moment arm** below the CG that the flight controller
must trim against continuously. A **340 mm forward boom** pushes the nozzle past the rotor disc and
cuts the arm to about **28 mm**.

Jet reaction force: `F(lbf) = 0.0745 × gpm × √psi` → ~12 N at our pressures. **It is the moment,
not the force, that costs control authority.**

### 2.2 The mounting plate

One carbon or aluminium belly plate bolts to the aircraft's **Universal Payload Interface**
(M600-compatible spacing). Everything else hangs off that plate — so the plate, not the airframe,
is the part you fabricate.

- Wet components sit **forward** along the water path: clamp → solenoid → flow sensor → boom → gun.
- **Companion computer aft in an IP66 enclosure**, as far from the nozzle and its drift as the
  plate allows.
- **Rangefinder co-aligned with the spray axis**, so the standoff it measures is the standoff the
  prescription specified.
- **The hose clamp is deliberately not on this plate.**

### 2.3 ⚠️ The single most important fabrication rule

**Hose tension must never pass through the gimbal or the payload plate.** It goes straight into the
airframe's structural rail via its own clamp, with a slack service loop between the clamp and the
gun.

Get this wrong and every hose tug becomes a torque on the gimbal servo and a bending load on your
mounting bolts — the two things most likely to fail in flight.

---

## 3. Where the load actually goes

The powered reel — **not the aircraft** — carries the hose. It pays out and takes up to hold
near-zero tension at the drone, which is what makes working height independent of payload. At the
aircraft the hose lands on a clamp bolted to the **airframe rail**; only a slack loop continues to
the gun, so gimbal motion and hose motion are mechanically decoupled.

---

## 4. The fluid system — where the foam question lands

One aircraft, one hose, four surfaces with incompatible requirements. The design problem is not how
to make foam; it is **how to keep detergent away from the solar panels** when everything shares a
single line.

```
  RO ──▶ DI resin ──▶ DI TANK ──┐
                                 ├──▶ 3-WAY VALVE ──▶ PUMP ──▶ PROPORTIONER ──▶ PSM ──▶ hose ──▶ gun
              BULK TANK ────────┘                                  ▲                    └─ TDS check point
              (tap · roof + walls)                             chem drum
                                              └──────── SHARED WETTED VOLUME ────────┘
                                          once detergent is in here, it is in here
```

**THE RULE: DI-only zones run first, every day — before chemistry has ever entered the shared
volume.** Reverse that order and the only way back is a verified flush (§4.3).

Switching source is trivial; the shared volume downstream of the proportioner is not. Detergent
that has been through the pump, hose, boom and gun is still there on the next zone, which is why
**sequence, not plumbing, is the primary control.**

### 4.1 Why solar drives this and glass does not

- **Glass wants 0 ppm so it dries without spots.** Get it wrong and you get water spots — a
  cosmetic failure, visible, and fixable by doing it again.
- **Solar wants 0 ppm *and* zero surfactant, because residue costs the customer generating
  capacity.** Get it wrong and you have measurably degraded the asset you were paid to improve —
  and it is invisible until someone reads the inverter.

That asymmetry is why the sequencing rule is written around solar. It is also the one surface where
the failure is **silent**, which is exactly the case verification exists for: the Post-Clean agent
should be reading **panel output**, not just thermal residual.

`TODO(PROPWASH): inverter API integration — needs Kevin's call on scope.`

### 4.2 Enforce the order in software, not in a checklist

This is a scheduling constraint, and the Supervisor agent already sequences zones. Encoding it there
makes it **structural rather than procedural** — the work order cannot be emitted in an order that
puts a chemical zone ahead of a DI-only zone. A laminated card in the truck is not the same
guarantee, and it is the sort of rule that gets skipped at 4pm on the third job.

### 4.3 If you do have to switch back mid-day

| Segment | Volume | ×3 flush |
|---|---|---|
| 40 m of 3/8" hose | 2.85 L | 8.6 L |
| Pump, proportioner, PSM, boom, gun | ≈0.6 L | 1.8 L |
| **Total** | **≈3.5 L** | **≈10.4 L · 2.7 gal · ~30 s at 6 gpm** |

A flush is **cheap** — the reason to sequence instead is not cost, it is that a flush is only as
good as its verification. Catch the discharge in a bucket and read it: **under 10 ppm before you
point the gun at a panel.** A $25 handheld TDS meter is the whole quality system here.

---

## 5. Foam, and why you are not going to make any

| Method | What it needs | Verdict |
|---|---|---|
| Venturi foam cannon | ~1,000+ psi to draw air through the orifice | ✗ We run 60–100 psi. It will dribble |
| Compressed-air injection (CAFS) | A second line up the tether, plus a compressor | ✗ Air line is more hose weight — the entire constraint |
| Onboard mini-compressor | Compressor + power + plumbing on the aircraft | ✗ ~1 kg of your 4.56 kg, to make foam |
| **Thickened surfactant chemistry** | A different drum | **✓ Cling from the formulation. No hardware, no weight** |

**Buy the cling, don't build it.** Soft-wash surfactants are formulated for exactly this — cling and
dwell at low pressure, because the chemistry is doing the work and it has to stay on a vertical
surface long enough to do it. It also removes a failure mode: a foamer is one more wetted component
to cross-contaminate and flush before you touch a panel.

---

## 6. Water — the part that will surprise you

Two of four surfaces need deionised water, and **Carlsbad has some of the least convenient feed
water in the state for making it.** Published figures put local TDS at roughly **474–611 ppm** with
hardness around **18 grains per gallon** — "very hard." DI resin capacity scales inversely with feed
TDS.

| Configuration | Feed TDS | Gal per refill | Resin cost/gal | 120-gal job |
|---|---|---|---|---|
| DI resin alone | ≈550 ppm | ~150 | ~$0.66 | ~$79 |
| **RO → DI resin** | ≈15 ppm | ~5,500 | ~$0.02 | ~$2 |

### ⚠️ The RO stage pays for itself in about a month

RO removes 95–99% of dissolved solids *before* the resin sees them, extending resin life roughly
**30×** on Carlsbad water. On one 120-gallon solar job that is a **~$77 swing**; at three jobs a week
it is on the order of **$11,000 a year** in resin you would otherwise throw away.

**Treat the RO stage as mandatory, not an upgrade.** These are published averages — **put a $25 TDS
meter on your own tap before you buy anything.**

### 6.1 RO is slow, so the tank is the real equipment

A 300–600 GPD RO unit produces **0.2–0.4 gpm**. Your gun consumes **4–8 gpm** — twenty times faster
than you can make water. You never make DI water at the job; **you make it overnight at the shop and
haul it.**

| Job type | DI needed | Tank | Water weight | Vehicle |
|---|---|---|---|---|
| Residential — array + glass | 60–90 gal | 100 gal | 834 lb | 3/4-ton bed or light trailer |
| Small commercial | 150–250 gal | 275 gal | 2,294 lb | Braked trailer |
| Commercial solar farm | 500–1,000 gal | — | 4,170–8,340 lb | ⚠️ Needs on-site high-flow RO. Phase 2 |

**Water is the heaviest thing you own.** A 275-gallon tote outweighs the entire rest of the kit,
aircraft included. **Commercial solar farms do not close on this configuration** — a 0.4 gpm RO
cannot feed a 1,000-gallon day, and hauling it is four tons.

---

## 7. The four surfaces, and what each actually asks for

| Surface | Pressure | Water | Chemical | Tip | Limiting factor |
|---|---|---|---|---|---|
| Composite shingle roof | 5.0–6.5 bar | Tap | Degreaser *or* biocide (§8) | 40° fan, 0.5 mm | Dwell. Industry soft wash is 15–20 min, our table says 35 s |
| Solar panel | 1.5–2.0 bar | ⚠️ **DI only** | **None. Ever.** | 25° narrow, 0.35 mm | Residue and cell damage. Hard ceiling in the safety layer |
| Window glass | 2.0–2.4 bar | **DI** | Ammonia-free | 20° jet | ⚠️ No agitation — see below |
| Stucco / gutter | 3.5–7.0 bar | Tap | Degreaser (+ solvent, gutters) | 40–45° fan, 0.6–0.7 mm | Overspray and containment |

### ⚠️ The honest limit on glass: a drone cannot scrub

Water-fed-pole window cleaning works because of the **brush**. The pure water rinses; the bristles
break the bond. **You have no brush**, so on glass you are relying on chemistry, dwell and rinse
alone.

**That is fine for light atmospheric soil and useless on bonded soil** — hard-water spotting,
construction film, mineral etch. Competitors market "streak-free"; treat that as a claim to verify
on your own glass before you put it in a quote. Contact cleaning means a drone that pushes against
the building — a force-control problem on a different aircraft. **Not year one.**

### 7.1 One head, two tips

Four surfaces want four tips, and hand-changing nozzles per zone destroys the makespan the scheduler
is built to protect. A full rotating selector costs **0.50 kg** of a 4.56 kg budget. The cheaper
answer covers the spread: **a two-tip head with a solenoid selector, about 0.20 kg** — a 25°/0.35 mm
for solar and glass, and a 40° fan for roof and stucco. The gutter case falls back to a hand change,
which is once a job, not once a zone.

---

## 8. ⚠️ The regulatory fork you have not priced yet

Everything so far assumed Part 107. **Dispensing changes that.** FAA Part 137 governs agricultural
aircraft operations, which the FAA defines to include dispensing **"economic poisons"** from an
aircraft, manned or unmanned — and the FAA's own guidance frames it as covering dispensed substances
**including disinfectants**.

Sodium hypochlorite on a roof is not being used as a soap. **It is being used to kill gloeocapsa
magma** — that is pest control, and a reasonable reading puts it inside Part 137. Many drone
soft-wash operators already hold the certificate.

| | Path A — no biocide | Path B — biocide |
|---|---|---|
| Chemistry | DI, surfactant, degreaser | Sodium hypochlorite + surfactant |
| Roof result | Removes surface soil. **Algae returns fast** | Kills the organism. Industry-standard result |
| FAA | Part 107 | **Part 137 AAOC — 90–180 days** |
| California | — | DPR applicator licensing + county Ag Commissioner registration |
| Insurance | Easier | Chemical application changes the conversation |
| Time to first roof job | Immediate | **Two to six months** |

**Why this is the decision, not a footnote.** It sets your **launch date**. If roofs need Path B, the
roof product cannot ship until the certificate does — which argues for opening on **solar, glass and
scan-only work**, all Path A, and adding roofs when the paperwork lands.

It also resolves the open dwell question in `prescriptions/surface_treatment_v1.json`: the 35 s roof
dwell is only defensible with a biocide doing the work. Path A roofs need the full 15–20 minute soak,
which changes the schedule, the water volume and the tank sizing above.

`TODO(PROPWASH): needs an aviation attorney, not a search result.`

---

## 9. Indoor work — the answer, and the better version of the question

| Blocker | Why it does not resolve with a smaller payload |
|---|---|
| **Size** | 1.2 m frame, ~1.6 m across props. Residential rooms and stairwells are not survivable geometry |
| **Navigation** | No GPS indoors. Position hold needs VIO or LiDAR SLAM — a different autonomy stack, not a payload |
| **Downwash** | Outdoors the air leaves. Indoors it recirculates, lifting dust and pushing overspray back through the room |
| **Liquid** | Water near furnishings, electrical and drywall. The liability question that ends the conversation with an underwriter |
| **Tether** | A charged hose through a doorway is a snag path with no clear line back to the reel |

### The market you probably meant is real — and it is dry

**High interior volumes** — warehouse and hangar ceilings, atriums, gymnasiums, stadium concourses,
church naves — are genuine and underserved, currently served by scissor lifts and scaffolding at real
cost. In some jurisdictions overhead **combustible-dust removal is a fire-code obligation**, which
means a budget line and a schedule.

But that work is **dusting and blow-down, not washing**: no water, no tether, no chemistry. Different
aircraft (small, caged, VIO-navigated), different payload, different sale.

**It shares one thing with this build, and it is the valuable thing:** the map, the per-surface model
and the verification loop are method, not plumbing. They port. The hardware does not.
**Phase 3, separate program.**

---

## 10. The complete kit

### A · Aircraft

| # | Item | Note | Cost |
|---|---|---|---|
| A1 | **IF1200A airframe** | Blue + Green UAS. PX4. 43 min. ⚠️ Recently listed sold out — ask about lead time first | $32,000 |
| A2 | **GCS + battery sets** | Bundle delta. 3+ sets for a field day | $8,000–$20,000 |
| A3 | **Skydio X10D scout** | The mapping half of the loop. FLIR Boson+ radiometric, 30 mK | $16,000 |
| A4 | Scout batteries, case, controller | | $4,000–$6,000 |
| A5 | Corrosion kit + rinse station | Conformal coat, dielectric grease, stainless, freshwater rinse | $500–$1,000 |
| A6 | Spare arms, motors, props | Near-surface work eats props | $1,500–$3,000 |
| | **Aircraft subtotal** | | **$62,000–$78,000** |

### B · Airborne payload — 4.10 kg

| # | Part | Spec / note | Mass | Cost |
|---|---|---|---|---|
| B1 | **Soft-wash gun / lance** | Rated ≥20 bar (4× our ceiling). Brass or SS wetted parts | 1.20 kg | $200–$400 |
| B2 | **Single-axis pitch gimbal** | Pitch only — the aircraft yaws | 0.60 kg | $300–$600 |
| B3 | **Boom, ~340 mm** | CF tube 25 mm OD. Length set by rotor-disc clearance | incl. | $80 |
| B4 | **Belly plate** | 3 mm CF or 5052 alu. 4× M4 to Universal Payload Interface | 0.70 kg | $150–$400 |
| B5 | **Two-tip head + selector solenoid** | 25°/0.35 mm and 40° fan (§7.1) | 0.20 kg | $150–$300 |
| B6 | **Main solenoid valve** | 12 V, ≥8 gpm, low ΔP. Driven by `PUMP_CHANNEL` | 0.30 kg | $60–$150 |
| B7 | **Flow sensor** | Closes the loop on delivered volume vs ground speed | 0.10 kg | $40–$90 |
| B8 | **Laser rangefinder** | **Co-aligned with spray axis.** Standoff hold — why you skip prop guards | 0.10 kg | $150–$400 |
| B9 | **Companion computer** | ARM SBC, **IP66 enclosure, mounted aft** | 0.50 kg | $200–$500 |
| B10 | **Hose clamp / strain relief** | **Bolts to airframe rail, NOT the plate** | 0.40 kg | $80–$200 |
| | **Airborne equipment** | **Leaves 4.56 kg for hose = 21.6 m unsupported** | **4.10 kg** | **$1,410–$3,120** |

### C · Ground rig — where the IP lives

| # | Item | Why | Cost |
|---|---|---|---|
| C1 | **Soft-wash pump**, 4–8 gpm @ 60–100 psi | Commodity 12 V rig. **60–100 psi *is* 4–7 bar** — our exact table | $1,500–$2,500 |
| C2 | **Electronic pressure regulator** | **This is the PSM.** It never flies | $1,500–$4,000 |
| C3 | **Firmware pressure ceiling** | Must **refuse** an over-ceiling command in hardware — not trust software | incl. C2 |
| C4 | **Powered hose reel** | ⚠️ **Load-bearing.** Holds the hose so the drone doesn't have to | $800–$2,000 |
| C5 | **3/8" hose, 60 m** | 0.211 kg/m charged. Reel carries it; only 21 m may hang free | $200–$500 |
| C6 | **Chemical proportioner** | Per-zone mix ratio, driven by the prescription | $400–$1,200 |
| C7 | **3-way source valve** | DI tank vs bulk tank, upstream of the pump (§4) | $80–$250 |
| C8 | **Containment / recovery** | Detergent to a storm drain is a regulated discharge in California | $500–$1,500 |
| | **Ground rig subtotal** | | **$4,980–$11,950** |

### D · Water & chemistry

| # | Item | Why | Cost |
|---|---|---|---|
| D1 | **RO unit, 300–600 GPD** | ⚠️ **Mandatory on Carlsbad water** — ~30× resin life (§6) | $400–$1,200 |
| D2 | **DI resin vessel + first fill** | Mixed bed, 1.6–3.6 ft³. Polishes RO permeate to 0 ppm | $400–$900 |
| D3 | **DI buffer tank, 100–275 gal** | You make water 20× slower than you spray it. Fill overnight | $250–$700 |
| D4 | **Bulk tank, 100–200 gal** | Untreated water for roof and stucco | $200–$500 |
| D5 | **Trailer, braked** | ⚠️ 275 gal of water is **2,294 lb**. Axle rating is a real spec | $2,500–$6,000 |
| D6 | **Handheld TDS meter ×2** | The entire quality system for §4.3 | $50 |
| D7 | **Thickened soft-wash surfactant** | **This is your "foam."** Cling from chemistry (§5) | $150–$400 |
| D8 | **Eco degreaser, ammonia-free glass** | Path A chemistry — no Part 137 exposure | $200–$500 |
| D9 | *Sodium hypochlorite + injector* | ⚠️ **Path B only.** Do not buy until §8 is decided | $300–$800 |
| | **Water & chemistry subtotal** | | **$4,150–$11,050** |

### Kit total — $72,500 to $104,000

Against a single Lucid Sherpa at **$75,000**, which maps nothing, integrates nothing, and leaves you
with no scout, no ground rig and no water system.

---

## 11. Buy it in this order

| Phase | What | Proves | Cost |
|---|---|---|---|
| **1** | **Ground rig on a bench** — C1, C2, C3, D6, gun on a stand | The per-surface pressure loop and the firmware ceiling. **The actual IP.** No aircraft, no licence, no liability | $3,100–$6,600 |
| **2** | **Water train** — D1–D4, D6 | Your real TDS, real resin cost, real fill time. All of §6 replaced with measurements | $1,300–$3,300 |
| **3** | **Scout + photogrammetry** — A3, A4 | **Scan-only revenue.** No spray, no water, no damage exposure — the differentiated half | $20,000–$22,000 |
| **4** | **Cleaner + payload** — A1, A2, A5, A6, B1–B10, C4–C8, D5 | The closed loop | $48,000–$72,000 |

**Phases 1 and 2 cost under $10,000, need no aircraft and no certificate, and test the only thing
that can't be bought:** whether per-surface prescription and verification actually hold up against
real dirt. If the pressure loop doesn't work on a bench, none of the $70,000 above it matters.

---

## 12. ⚠️ Before you cut metal or sign anything

1. **Will Inspired Flight support a liquid spray payload?** Warranty and airworthiness.
   *A "no" ends this build — ask before anything else.*
2. **Exact Universal Payload Interface bolt pattern and load rating.** The plate can't be drawn to
   scale until you have their drawing.
3. **Insurance for a self-integrated spray drone.** Still unasked, still likely the deciding number —
   and §8 changes the quote.
4. **Part 137 applicability to hypochlorite soft washing.** An aviation attorney, not a search result.
5. **Your own tap water TDS.** A $25 meter, ten minutes, and it re-prices all of §6. **Do this today.**

---

## Sources

- [Inspired Flight IF1200A](https://shop.inspiredflight.com/products/if1200a-heavy-lift)
- [Freefly Alta X specifications](https://freeflysystems.com/alta-x/specs)
- [FAA — Dispensing Chemicals and Agricultural Products (Part 137) with UAS](https://www.faa.gov/uas/advanced_operations/dispensing_chemicals)
- [Puretec — DI tank capacity vs feed TDS](https://puretecwater.com/resources/how-many-gallons-of-deionized-water-will-a-di-tank-produce/)
- [Fusion Spray — selecting soft-wash surfactants](https://fusionspray.com/blogs/blogs-basics-and-faqs/selecting-the-best-surfactant-for-pressure-washers-and-soft-washing)
