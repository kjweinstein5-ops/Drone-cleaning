# PROPWASH Operator — mobile app (React Native / Expo)

The **field client** for the PROPWASH operator (CLAUDE.md §10). It turns the
approved mockup in `samples/operator_app_demo.html` into a native app that walks
a Part-107 operator through the per-zone clean loop and reads back verification
results — while keeping the operator **in command** at all times.

This is a **separate client** from `frontend/` (the React _web_ ops dashboard).
Both talk to the same FastAPI backend; the contract lives in
`propwash/backend/app/routers/jobs.py` and is mirrored, typed, in `src/api/`.

## Where things live

| Path | Purpose |
|------|---------|
| `app/` | expo-router routes = the operator flow (login → jobs → job → zone → summary) |
| `src/api/` | typed mirror of `propwash/backend/models/*.py` + REST client |
| `src/telemetry/` | read-only WebSocket to `/jobs/ws/telemetry` (Tier-2 → operator) |
| `src/offline/` | durable outbox + cache so a dropped LTE link never loses a confirmation |
| `src/safety/` | **display + relay only** — NOT an authoritative safety layer (see its README) |
| `src/features/` | zone execution UI: nozzle prompt, prescription, dwell timer, verdict |
| `src/theme/` | tokens lifted from the operator demo mockup |

## Architectural guardrails (from CLAUDE.md)

- **§2 — three tiers, never collapsed.** This app is Tier-3-adjacent UI. It never
  writes a Tier-0 setpoint or suppresses a Tier-1 safety check. Telemetry is
  read-only; safety values are advisory display.
- **§5 — thermal + RGB only.** `grime_confidence` / `residual_confidence` are
  **proxy** scores; the UI labels them as such. No multispectral claims.
- **§7 — Path A.** The app emits/reads work orders and status. It does not control
  Lucid hardware. Paths B/C stay backend-side, behind flags.
- **§9 — conservative ceilings.** Solar = DI water only + hard pressure ceiling;
  the safety banner warns, the backend enforces.
- **§10 — operator in command.** Abort is always available; automation reduces
  required *skill*, never the operator's *authority*.

## Getting started

```bash
cd mobile
npm install
cp .env.example .env          # point EXPO_PUBLIC_API_URL/WS_URL at the backend
npm start                     # Expo dev server (dev client)
```

`react-native-mmkv` is a native module, so the first device run needs a dev
client / prebuild:

```bash
npm run prebuild              # generates ios/ + android/ (gitignored)
npm run ios                   # or: npm run android
```

## Checks

```bash
npm run typecheck
npm run lint
npm test
```

## Not built yet (intentional TODOs)

- Real auth + Part-107 pilot-on-record check (`app/index.tsx`).
- Live video + thermal overlay component (`ThermalOverlay`) — needs the streaming
  source decided with Lucid (§7).
- Network reachability listener to auto-flush the outbox (currently flushed on
  refresh / status change).

Grep for `TODO(PROPWASH)` for the full list.
