# PROPWASH Operator App

React operator app for executing per-zone cleans and verification. The operator
stays in command at all times (FAA Part 107, CLAUDE.md §10) — every zone has an
always-available Abort/Override, and solar zones surface a hard safety banner.

## Run locally (dev)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

The app runs **standalone with a built-in demo job** if the backend isn't up.
To wire it to the FastAPI backend, run the API on :8000 (Vite proxies `/jobs`,
`/zones`, `/health` and the telemetry WebSocket) and swap `DEMO_JOB` in
`src/App.jsx` for `listJobs()` / `getJob()` from `src/api.js`.

## No-build demo

`samples/operator_app_demo.html` is a single self-contained file (React via CDN).
Open it directly in any browser — handy on an iPad with no toolchain.

## Flow (per zone)

1. **Brief** — nozzle, chemical, pressure, standoff, pattern checklist; confirm ready.
2. **Executing** — dwell countdown + live overlay; Abort always available.
3. **Verifying** — post-clean thermal re-scan.
4. **Verdict** — PASS (next zone) or RE-QUEUE (retry with adjusted pressure).
