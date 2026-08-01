# FAA Waiver Package — 14 CFR 107.35 (Multiple sUAS, One RPIC)

> **Draft working document — NOT a filed application.** Have an aviation attorney review and
> finalize before submitting via **[FAADroneZone](https://faadronezone.faa.gov/)**.
> `[Bracketed]` fields must be completed with real operational data.
>
> **Why this waiver first:** 107.35 is the single constraint that breaks the linear
> labor↔revenue coupling in `SCALING_TO_10M.md`. Every other core capability we need is
> already legal under Part 107 (`REGULATORY_STRATEGY.md` §0–1).

---

## 1. What 107.35 says and what we're asking

**The rule:** *"A person may not manipulate flight controls or act as a remote pilot in command
or visual observer in the operation of more than one unmanned aircraft at the same time."*

**Our request:** authorize **one RPIC to supervise up to [N] sUAS simultaneously** during
exterior-cleaning operations, supported by visual observers, where each aircraft flies a
**pre-programmed, pre-validated flight path** and the RPIC retains the ability to intervene on
any aircraft at any time.

**Note:** autonomous/pre-programmed flight itself already complies with Part 107 (FAA AC 107-2)
— this waiver addresses *only* the one-pilot-one-aircraft limitation.

---

## 2. Concept of operations (ConOps)

| Element | Description |
|---|---|
| Operation | Exterior cleaning of buildings/solar arrays at a fixed, surveyed site |
| Airspace | [Class G / controlled w/ LAANC auth]; [altitude], within 400 ft of the structure per **107.51(b)** |
| Aircraft | [N] × [make/model], each [weight] |
| Flight profile | Pre-programmed coverage paths generated from a site survey; low speed ([~0.2–0.35 m/s]), short standoff, confined to the property |
| Crew | 1 RPIC + [4] Visual Observers (VOs) + [1] ground crew |
| Site | Private property, access-controlled during operations |
| Duration | [X] hours per job |

**Risk-reducing characteristics inherent to this operation:** aircraft fly *slowly*, at *low
altitude*, in *close proximity to a structure*, on *fixed pre-validated paths*, over *private
property under our control* — a materially lower-risk profile than free-flight or BVLOS survey.

---

## 3. Safety mitigations (the core of the application)

> Each mitigation below is **implemented and tested in software** — not aspirational. Test
> counts refer to the automated suite (117 passing).

### 3.1 Pre-validated flight paths
- Paths are generated from a 3D site survey, not improvised (`planning/coverage_path.py`).
- Every path is computed at a fixed standoff from the surface, at bounded speed.
- **Keep-out volumes** are auto-generated around obstacles (chimneys, HVAC, vents) and the path
  is checked against them before flight (`KeepOut`, verified 0 violations in test).
- Paths are reviewed on the ground before upload (`mavlink_transport.build_mission()` runs with
  hardware disconnected).

### 3.2 Deterministic safety layer (cannot be overridden by software agents)
- Hard **pressure ceilings** per surface, enforced independently of any AI output.
- An unsafe parameter causes the work order to be **rejected, not adjusted** — no mission is
  emitted at all (`safety/checks.py`; test: over-pressure request is blocked).
- AI components are **advisory only** and sit outside the safety path (CLAUDE.md §2 tiering).

### 3.3 Human-presence detection
- Thermal detection halts dispatch when a human signature is detected in a work zone
  (`safety/human_detection.py`), independent of operator attention.

### 3.4 Loss-of-control watchdog
- Independent heartbeat monitoring of companion computer, C2 link, payload link, and telemetry.
- **Any** loss of positive control cuts the spray and commands a safe state.
- **Fail-closed:** a channel that has never reported is treated as failed.
- **Latching, no auto-resume:** a restored link does not resume operations; explicit human
  re-arm is required (`safety/watchdog.py`; 13 tests incl. every-channel coverage).

### 3.5 Tamper-evident audit logging
- Hash-chained, append-only record of every safety decision and execution event
  (`safety/audit_log.py`; 12 tests covering alteration, deletion, reordering, and forgery).
- Produces a verifiable **compliance export** — the FAA or a customer can confirm no record was
  edited after the fact.

### 3.6 Positive RPIC control of every aircraft
- RPIC ground station displays, per aircraft, **live position, altitude, attitude, groundspeed,
  and battery state**.
- RPIC can, for any individual aircraft at any time: **hold**, **change routing/altitude**,
  **command immediate landing**, and **cut the spray**.
- Always-available **Abort/Override** in the operator application.
- Aircraft are **visually separated** by assigned work zones so their paths cannot intersect.

---

## 4. Crew, roles, and training

### Roles
| Role | Responsibility |
|---|---|
| **RPIC** | Final authority for all [N] aircraft; monitors telemetry; intervenes; sole authority to arm spraying |
| **Visual Observers ([4])** | Maintain VLOS on assigned aircraft; scan for intruding aircraft/persons; report to RPIC on continuous comms |
| **Ground crew** | Site security, chemical/water handling, no flight duties |

### Communication
All crew on continuous two-way radio. Standard call-outs for: intruder aircraft, person entering
the site, aircraft anomaly, and **ABORT** (any crew member may call an abort).

### Training (before any waiver operation)
Each RPIC and VO completes documented training covering:
1. Part 107 regulations
2. **The specific limitations and conditions of this waiver**
3. Proper visual scanning techniques
4. PROPWASH system operation, failsafes, and abort procedures
5. Emergency and lost-link procedures

Each completes a **written test ([20] questions)**; records retained and available to the FAA.

---

## 5. Emergency & contingency procedures

| Scenario | Response |
|---|---|
| Lost link (one aircraft) | Aircraft enters programmed failsafe (hold → RTL → land); spray cut automatically; RPIC announces; remaining aircraft continue or are held per RPIC judgment |
| Multiple aircraft anomaly | RPIC commands **all** aircraft to hold/land; operation suspended |
| Manned aircraft intrusion | VO calls out; RPIC immediately descends/lands all aircraft |
| Person enters operating area | Any crew member calls abort; spray cut; aircraft hold/land |
| Watchdog trip | Spray cut automatically; aircraft holds; requires human re-arm to resume |
| Adverse weather | Operations suspended below [minimums]; pre-flight weather check documented |

---

## 6. Proposed waiver conditions (we volunteer these)

Offering conditions strengthens an application:
1. Maximum **[N]** aircraft per RPIC.
2. Minimum **[4]** VOs; operations cease if VO staffing drops below minimum.
3. Operations only over **private property under operator control**, with public access excluded.
4. All aircraft on **pre-programmed paths** with pre-flight keep-out validation.
5. Aircraft assigned to **non-overlapping work zones**.
6. Daylight VLOS only [unless separately waived].
7. Documented crew training + testing retained and available on request.
8. Audit logs retained for **[24] months** and available to the FAA on request.

---

## 7. Application checklist

- [ ] FAADroneZone account created
- [ ] Part 107 certificate(s) current; aircraft registered
- [ ] Aircraft make/model/weight/performance documented
- [ ] Site(s) and airspace class identified; LAANC authorization if controlled
- [ ] ConOps finalized (§2) with real numbers
- [ ] Safety mitigations documented (§3) — attach architecture + test evidence
- [ ] Crew training curriculum + written test drafted (§4)
- [ ] Emergency procedures documented (§5)
- [ ] Insurance in place
- [ ] **Aviation attorney review**
- [ ] Submit; expect **[60–90+] days**; be responsive to FAA questions

---

## 8. Why this application should be strong

Most 107.35 applications are prose descriptions of intent. This one can attach:
- a **deterministic safety architecture** that structurally prevents unsafe operation,
- **117 automated tests** demonstrating those safeguards function,
- **tamper-evident logs** proving compliance in operation, and
- a **low-risk flight profile** (slow, low, fixed paths, private property).

That is a materially different quality of evidence — and it is the competitive moat: a
competitor cannot copy a waiver, and cannot quickly build the evidence to earn one.

---

## 9. Follow-on waivers (after 107.35)
1. **107.31 (BVLOS)** — larger campuses and solar farms; heaviest lift; Part 108 may supersede.
2. **107.39 (over people)** — only if job types require it.
3. Track **Part 108** — may replace this waiver path entirely with a standing framework
   (`COMMUNICATION_AND_AUTONOMY.md` §4).

## Sources
- [14 CFR 107.35 (Cornell)](https://www.law.cornell.edu/cfr/text/14/107.35) · [FAA — certificated remote pilots / waivers](https://www.faa.gov/uas/commercial_operators) · [FAADroneZone](https://faadronezone.faa.gov/)
- [Sample 107.35 waiver — Pilot Institute](https://pilotinstitute.com/multiple-drones-waiver/) · [Sample 107.35 application — Rupprecht Law](https://jrupprechtlaw.com/sample-107-35-waiver-application-swarming-drones/) · [FAA AC 107-2](https://www.faa.gov/documentlibrary/media/advisory_circular/ac_107-2.pdf)
