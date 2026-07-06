# `safety/` — display + relay ONLY

This directory is **not** a safety layer. Per CLAUDE.md §2, the authoritative,
deterministic safety layer lives in:

- **Tier 1** — on-aircraft / safety supervisor (geofence, collision, pump/valve abort).
- **Tier 2** — backend `propwash/backend/safety/` (pressure ceilings, keep-away rules).

What this folder does:

- **Renders** conservative advisory limits so the operator can spot an obviously
  wrong prescription (e.g. detergent on a solar panel, over-pressure). See §9.
- **Relays** the operator's manual abort/override intent to the backend.

What this folder must **never** do:

- Compute a setpoint that hardware acts on.
- Be the only thing standing between a prescription and the pump.
- Suppress or override a Tier-0/Tier-1 check.

If a change would make this file authoritative for hardware behaviour, stop and
flag it (`TODO(PROPWASH): needs Kevin/Lucid/attorney decision`).
