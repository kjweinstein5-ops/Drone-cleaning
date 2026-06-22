// Thin API client for the PROPWASH backend (FastAPI).
// In dev, Vite proxies these paths to http://localhost:8000 (see vite.config.js).

export async function listJobs() {
  const res = await fetch("/jobs");
  if (!res.ok) throw new Error(`listJobs failed: ${res.status}`);
  return res.json();
}

export async function getJob(jobId) {
  const res = await fetch(`/jobs/${jobId}`);
  if (!res.ok) throw new Error(`getJob failed: ${res.status}`);
  return res.json();
}

export async function updateJobStatus(jobId, status) {
  const res = await fetch(`/jobs/${jobId}/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(`updateJobStatus failed: ${res.status}`);
  return res.json();
}

// Live telemetry stream. onEvent receives parsed JSON events.
export function connectTelemetry(onEvent) {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/jobs/ws/telemetry`);
  ws.onmessage = (e) => {
    try { onEvent(JSON.parse(e.data)); } catch { /* ignore non-JSON */ }
  };
  return ws;
}
