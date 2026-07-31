# Deep Dive — Flight Software Stack (ROS 2 / PX4 / MAVLink / Auterion / Jetson)

> The layer that decides whether PROPWASH's tech can actually **command** an aircraft.
> Directly answers Q1–Q10 of the Integration Qualification Questionnaire
> (`LAUNCH_PLAYBOOK.md` §1.0).
>
> ⚠️ **Regulatory line (CLAUDE.md §2, §7, §10):** everything below describes *technical*
> capability. Autonomous **flight** requires the appropriate FAA pathway/waiver with the
> operator in command. **Payload** control (pump/nozzle), gated by our Tier-1 safety layer, is
> the near-term target; flight autonomy is a separate, regulated step. No covert automation.

---

## 0. The headline

**On an open PX4 stack, all ten questions answer "yes" — and each is a documented,
off-the-shelf capability.** This is the strongest technical validation yet for the
open-platform direction (`decisions/OPEN_PLATFORM_INTEGRATION.md`).

| Your question | Open PX4 answer | Mechanism |
|---|---|---|
| 1. Public SDK/API? | ✅ Yes | MAVSDK (C++/**Python**/Swift/Kotlin), ROS 2, MAVLink |
| 2. Upload custom 3D flight paths? | ✅ Yes | **PX4 ROS 2 Waypoint Missions** / MAVSDK Mission API |
| 3. Command velocity/heading/altitude? | ✅ Yes | **Offboard Mode** (⚠️ FAA-gated — see §4) |
| 4. Real-time telemetry (pos/IMU/obstacle/range)? | ✅ Yes | uORB topics → ROS 2 (`px4_msgs`) / MAVLink streams |
| 5. Onboard Jetson/companion computer? | ✅ Yes, **officially supported** | Holybro Pixhawk **Jetson Baseboard**; Auterion Skynode |
| 6. Software pump/nozzle control by location? | ✅ Yes | **ActuatorServos / ActuatorMotors**; payloads triggerable **in missions** |
| 7. ROS 2 / MAVLink / PX4 / Auterion? | ✅ All four | native |
| 8. Customer-available or partner-gated? | ✅ **Open source** — no gate | PX4/Dronecode |
| 9. Warranty/certification impact? | ⚠️ You're the integrator | you own airworthiness (§5) |
| 10. Developer/OEM program? | ✅ Dronecode + Auterion partners | — |

**Compare:** Lucid Sherpa answers *no* to 1, 2, 6, 8. That contrast is the whole platform
argument in one table.

---

## 1. The layers (what each thing actually is)

| Layer | What it is | PROPWASH uses it for |
|---|---|---|
| **PX4** | Open-source flight-control firmware (the autopilot) | Tier 0 — flight stabilization. **We never touch this** (CLAUDE.md §2) |
| **MAVLink** | Lightweight open messaging protocol (drone ↔ GCS ↔ payload) | The wire protocol; vendor-neutral |
| **MAVSDK** | High-level SDK over MAVLink (**Python** bindings) | Simplest path: missions, telemetry, payload commands |
| **ROS 2** | Robotics middleware (nodes, topics, DDS) | Deeper integration: real-time control, sensor fusion |
| **Auterion OS / Skynode** | Commercial enterprise PX4 + mission computer in one module | Turnkey hardware+software; NDAA-compliant option |
| **Companion computer** (Jetson) | Onboard Linux computer running our code | Edge autonomy, CV, payload logic |

**Key relationship:** ROS 2 ↔ PX4 is bridged via **micro-RTPS / uXRCE-DDS**, exposing PX4's
internal uORB messages as ROS 2 topics (`px4_msgs`). Auterion has invested heavily in making
ROS 2 first-class for flying robots.

---

## 2. How PROPWASH's pipeline maps onto it (the important part)

Our Stage-5 output (`planning/coverage_path.py`) already emits waypoints + spray flags +
per-zone pressure. Here's the concrete mapping:

```
FlightPlan (ours)                    →  PX4/ROS 2 mechanism
────────────────────────────────────────────────────────────────
ZonePath.waypoints (x,y,z)           →  ROS 2 Waypoint Mission / MAVSDK Mission items
Waypoint.spraying (bool)             →  ActuatorServos setpoint (pump ON/OFF) at that item
Prescription.pressure_bar            →  ActuatorServos value → our PSM regulator setpoint
Prescription.nozzle_id               →  ActuatorServos → IHM turret position
traverse_speed_mps                   →  mission item cruise speed
KeepOut volumes                      →  geofence / mission planning exclusion
telemetry (actual pressure, pos)     →  uORB/ROS 2 topics → our deviation log + verify loop
```

**This is the "tech that communicates between them"** you've been describing — and on an open
stack it's a documented integration, not an R&D project.

### Two implementation routes
- **MAVSDK-Python (recommended start).** Simplest; matches our Python backend; covers
  missions, telemetry, and actuator/payload commands. This is what `execution/
  mavlink_transport.py` should target first.
- **ROS 2 (later, if we need edge autonomy).** Deeper access, real-time control loops, and the
  natural home for on-aircraft CV — but heavier. Use if/when Tier-1 logic moves onboard.

---

## 3. Payload / pump control — how it actually works

The mechanism for Q6, and for PSM/IHM:

- **ActuatorServos / ActuatorMotors** let a companion computer or mission directly drive
  servo/motor outputs. A **pump, valve, or servo-driven nozzle turret is exactly this.**
- Payloads can be **triggered automatically within a mission** (i.e., spray ON at waypoint N),
  or commanded live via MAVLink/MAVSDK.
- So "spray at 4.0 bar along this sweep line, off during the repositioning leg" is a *native
  capability*, not a hack.

**Where our safety layer sits:** the Tier-1 `SafetyChecker` validates the pressure/nozzle
setpoint **before** any actuator command is emitted; the PSM firmware ceiling is the final
independent hardware guarantee (`DYNAMIC_PRESSURE_HARDWARE.md` §4). Agents never command an
actuator directly.

---

## 4. ⚠️ Offboard Mode — powerful, and the regulatory boundary

**Offboard Mode** is the PX4 flight mode where a companion computer commands
position/velocity/attitude — i.e., the software flies the aircraft. It's how Q3 is technically
answered "yes."

**But:**
- This is **autonomous flight**, which under Part 107 requires the operator in command and the
  appropriate FAA pathway/waiver for anything beyond that (CLAUDE.md §7, §10).
- It's also the highest-risk mode: a companion-computer fault becomes a flight-control fault.
  PX4 requires a continuous setpoint stream and fails safe if it stops.

**PROPWASH posture:** build the **payload** control path now (safe, useful, legal, and where
our IP lives). Treat Offboard flight control as a **later, waiver-gated** capability behind
`PROPWASH_ENABLE_PATH_C`. The coverage path remains **operator guidance** by default.

---

## 5. Hardware options for the companion computer

| Option | What it is | Notes |
|---|---|---|
| **Holybro Pixhawk Jetson Baseboard** | Pixhawk FC + NVIDIA **Orin** on one board | Officially documented in the PX4 guide; clean, integrated |
| **Auterion Skynode / Skynode S** | Flight controller + mission computer + video + networking + cellular, running Auterion OS (enterprise PX4) | Turnkey; **Skynode S is NDAA-compliant** → a real hedge against DJI regulatory risk |
| **Jetson Orin Nano/NX + separate FC** | DIY: Jetson + Pixhawk over serial/Ethernet | Cheapest, most flexible; you integrate it |

**Skynode is worth a serious look** — it collapses "flight controller + mission computer +
connectivity" into one supported module, and the NDAA compliance directly addresses the DJI
concentration risk flagged in `decisions/DJI_TWO_DRONE_ARCHITECTURE.md` §6.

---

## 6. What this changes strategically

1. **The open-platform path is technically de-risked.** Every capability PROPWASH needs is
   documented and supported on PX4 — no invention required at the integration layer.
2. **It sharpens the vendor comparison.** DJI = semi-open (PSDK, proprietary, vendor-gated).
   PX4/Auterion/Freefly = open (ROS 2 + MAVSDK + companion computers + actuator control, no
   gate). Lucid = closed. Score vendors against §1.0 with this in hand.
3. **It tells us what to build next in code:** implement `MavlinkPayloadTransport` against
   **MAVSDK-Python**, translating `FlightPlan` → mission items + `ActuatorServos` setpoints.
   The interface already exists and is flagged off.
4. **It's leverage with Lucid.** When you ask them Q1–Q10, you'll know exactly what an open
   platform provides — and can say so.

---

## 7. Open items
- [ ] Confirm MAVSDK-Python actuator API covers our pump/nozzle setpoint needs.
- [ ] Price Auterion Skynode / Skynode S; confirm NDAA status + partner terms.
- [ ] Decide MAVSDK-first vs ROS 2-first for `MavlinkPayloadTransport`.
- [ ] Spec the companion computer (Holybro Jetson baseboard vs Skynode vs DIY Orin).
- [ ] FAA: scope what a waiver would require before *any* Offboard-mode flight.

## Sources
- [PX4 Companion Computers](https://docs.px4.io/main/en/companion_computer/) · [PX4 ROS 2 Control Interface](https://docs.px4.io/main/en/ros2/px4_ros2_control_interface) · [PX4 ROS 2 Waypoint Missions](https://docs.px4.io/main/en/ros2/px4_ros2_waypoint_missions) · [PX4 Offboard Mode](https://docs.px4.io/main/en/flight_modes/offboard)
- [Holybro Pixhawk Jetson Baseboard](https://docs.px4.io/main/en/companion_computer/holybro_pixhawk_jetson_baseboard) · [Auterion Skynode (PX4 guide)](https://docs.px4.io/main/en/companion_computer/auterion_skynode)
- [Auterion — driving ROS 2 adoption](https://auterion.com/auterion-driving-ros-2-adoption-for-flying-robots/) · [Skynode S](https://auterion.com/product/skynode-s/) · [PX4 messages in ROS 2 (Auterion docs)](https://docs.auterion.com/app-development/app-framework/px4-messages-in-ros-2)
