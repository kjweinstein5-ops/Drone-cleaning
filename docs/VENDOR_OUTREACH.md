# Vendor Outreach — draft letters

> Send the **Integration Qualification Questionnaire** (`LAUNCH_PLAYBOOK.md` §1.0) to every
> manufacturer. These are the cover letters, tuned per vendor.
>
> **Rules for all outreach (CLAUDE.md §5, §7, §10):**
> - Be **transparent** — we integrate *with* vendors and *within* FAA Part 107. Never imply
>   covert automation or a plan to circumvent regulation.
> - **Don't overclaim** — no "fully autonomous," no "multispectral/mold detection." We say
>   thermal + RGB proxy, operator in command.
> - Ask for answers **in writing**. A verbal "we support integration" isn't an answer to Q8.
> - Replace `[bracketed]` fields before sending. Keep it short — busy people skim.

---

## 1. Lucid Bots — *partnership-first* (they're closed; we want them to open)

**Subject:** Integration partnership — AI verification layer for Sherpa operators

> Hi [Name],
>
> I'm [Kevin Weinstein], founder of [COMPANY] in Carlsbad, CA. We've built an AI orchestration
> and **verification** layer for exterior cleaning: we survey a property with a sensing drone,
> build a 3D thermal model, classify every surface (solar, glass, tile, stucco, gutter), and
> generate a per-zone cleaning prescription — then re-scan after the clean to produce a
> measured before/after result for the customer.
>
> We're planning to operate Sherpas ourselves, and our goal is to make each one more valuable:
> better-targeted jobs, documented outcomes, and an ROI report the building owner can act on.
> In short, we'd like to **drive more Sherpa utilization**, not compete with your autonomy work.
>
> Could we get 30 minutes with someone on the Refresh / partnerships side? I'd like to
> understand your integration surface. Specifically:
>
> 1. Does Lucid Refresh expose an API (REST/GraphQL/webhooks)?
> 2. Can we **read** job data programmatically — status, telemetry, completion, location?
> 3. Can we **push** structured work orders / job packets for an operator to execute?
> 4. Is the interface available to customers, or only to internal engineering partners?
> 5. Who owns the job and telemetry data generated on a customer's Sherpa?
> 6. Is there a developer, OEM, or reseller partnership program?
> 7. Longer term: any supported path for software-set pump/pressure parameters — under a
>    partnership, with the operator in command and the appropriate FAA pathway?
>
> Happy to sign an NDA and demo what we've built.
>
> Thanks,
> [Kevin] · [email] · [phone]

**Note:** Q7 is deliberately last and framed as *partnership + operator-in-command + FAA
pathway*. Never frame it as wanting to bypass their system.

---

## 2. DJI Enterprise — *developer program*

**Subject:** Payload SDK / Cloud API access — commercial exterior-cleaning application

> Hi [Name],
>
> I'm [Kevin], founder of [COMPANY] (Carlsbad, CA). We're building an AI system for commercial
> exterior cleaning: a survey drone maps a building in thermal + RGB, our software produces a
> per-surface condition model and cleaning plan, and we verify results with a post-clean re-scan.
>
> We're evaluating DJI for **both** roles — a Matrice 4T as the survey aircraft, and an
> M350/M400 with a third-party cleaning payload for execution. Before we commit, I'd like to
> confirm the developer surface:
>
> 1. Does Cloud API support programmatic ingest of imagery and real-time telemetry
>    (position, IMU, obstacle sensors, laser rangefinder)?
> 2. Can an external application upload **custom 3D flight paths / waypoint missions**?
> 3. Via Payload SDK, can our software control a third-party spray pump/nozzle — including
>    setpoints tied to position along a planned route?
> 4. Can we run an onboard companion computer (e.g., NVIDIA Jetson)? Supported mounting/power?
> 5. Do you support MAVLink or ROS 2 interoperability, or is integration PSDK-only?
> 6. Is PSDK/Cloud API access open to customers, or gated to partners? What's the approval path?
> 7. Does a third-party payload or custom software affect warranty or airworthiness?
> 8. Is there a developer/OEM partner program we should apply to?
>
> What's the right path to get these answered — a developer account, or a call with your
> enterprise/solutions team?
>
> Thanks,
> [Kevin] · [email] · [phone]

---

## 3. Foxtech / drone-payload (cleaning payloads) — *specs + price*

**Subject:** Quote + integration specs — AeroClean payload for M350/M400

> Hi [Name],
>
> I'm [Kevin] with [COMPANY] (Carlsbad, CA). We're speccing a drone-based exterior cleaning
> system for commercial buildings and solar arrays, and your [AeroClean P3 (T50) / T-M400C /
> RT-AP3] looks like a strong fit.
>
> Could you send pricing and lead time, plus answers to a few technical questions? Our software
> generates per-surface cleaning plans, so **programmatic control of the payload** is the
> deciding factor for us:
>
> 1. **Price and lead time**, and which airframes are supported (M350 RTK / M400)?
> 2. Pressure range, flow rate, hose length, max working height, coverage rate?
> 3. Is there a **control interface** (serial/CAN/MAVLink/PSDK) for our software to set
>    pressure or pump state — including varying it during a flight?
> 4. Can we read back **actual** pressure/flow telemetry?
> 5. Could we integrate our own electronic pressure regulator / nozzle module into the
>    payload's water path? Any spec or support for that?
> 6. Tethered vs. onboard-tank configurations available?
> 7. Warranty terms, and whether third-party integration affects them?
> 8. Do you support integrators/OEM customers, and is there documentation we can review?
>
> Thanks,
> [Kevin] · [email] · [phone]

---

## 4. Freefly Systems — *open platform / US-made*

**Subject:** Astro + Smart Dovetail — custom cleaning payload integration

> Hi [Name],
>
> I'm [Kevin], founder of [COMPANY] (Carlsbad, CA). We build AI software for commercial
> exterior cleaning — 3D surface mapping, per-surface cleaning plans, and post-clean
> verification. We're evaluating platforms where our software can be a first-class integration,
> and Astro's open approach (Smart Dovetail, Pixhawk Payload Bus, MAVSDK) is exactly the
> architecture we want. US-made is a plus for us.
>
> Questions:
>
> 1. Astro pricing/availability, and payload capacity for a liquid-delivery payload?
> 2. Smart Dovetail / Payload Bus specs — power, data, mounting envelope?
> 3. Via MAVSDK, can we command a custom payload (pump/valve setpoints) and read telemetry?
> 4. Can an external app upload **custom 3D flight paths / waypoint missions**?
> 5. Can we run an onboard companion computer (Jetson-class)? Supported power/data?
> 6. ROS 2 support or reference integrations?
> 7. Does a custom payload affect warranty or certification?
> 8. Is there a developer/OEM partner program, and can we get SDK docs to review?
>
> Would love 30 minutes with your solutions team.
>
> Thanks,
> [Kevin] · [email] · [phone]

---

## 5. Short universal version (for any vendor / web contact form)

> Hi — I'm [Kevin] with [COMPANY] in Carlsbad, CA. We build AI software for commercial exterior
> cleaning (3D surface mapping → per-surface cleaning plans → verified results) and we're
> selecting hardware platforms. Integration capability matters more to us than raw pressure, so
> before we buy, could you answer these in writing?
>
> 1. Do you provide a public SDK or API?
> 2. Can an external application upload custom 3D flight paths or waypoint missions?
> 3. Can we command velocity, heading, altitude, and standoff distance programmatically?
> 4. Is there real-time telemetry — position, IMU, obstacle sensors, range data?
> 5. Can we run an onboard NVIDIA Jetson or companion computer?
> 6. Can our software control the spray pump/nozzle based on location?
> 7. Do you support ROS 2, MAVLink, PX4, or Auterion APIs?
> 8. Is the interface available to customers, or only internal/engineering partners?
> 9. Will custom software void the warranty or certification?
> 10. Is there a supported developer or OEM partnership program?
>
> Happy to sign an NDA. Thanks — [Kevin], [email], [phone]

---

## Tracking

Log every reply in `docs/decisions/CLEANING_DRONE_PLATFORM.md` and score each vendor
**Open / Semi-open / Closed** per the rubric in `LAUNCH_PLAYBOOK.md` §1.0.

| Vendor | Sent | Replied | Score | Notes |
|---|---|---|---|---|
| Lucid Bots | | | | |
| DJI Enterprise | | | | |
| Foxtech | | | | |
| drone-payload | | | | |
| Freefly | | | | |
| Skydio | | | | |
