/**
 * WebSocket client for /jobs/ws/telemetry.
 *
 * Tier-2 -> operator, READ ONLY. The operator observes live execution; the app
 * never sends control setpoints back through this channel (CLAUDE.md §2).
 */
import type { TelemetryEvent } from '@/api/types';

const WS_URL = process.env.EXPO_PUBLIC_WS_URL ?? 'ws://localhost:8000';

export type TelemetryListener = (event: TelemetryEvent) => void;

export interface TelemetrySocket {
  close: () => void;
}

/**
 * Connect with automatic reconnect + exponential backoff. Returns a handle
 * whose close() stops reconnection.
 */
export function connectTelemetry(onEvent: TelemetryListener): TelemetrySocket {
  let ws: WebSocket | null = null;
  let closedByCaller = false;
  let backoff = 500;

  const open = () => {
    ws = new WebSocket(`${WS_URL}/jobs/ws/telemetry`);

    ws.onmessage = (e) => {
      try {
        onEvent(JSON.parse(e.data as string) as TelemetryEvent);
      } catch {
        /* ignore non-JSON keepalives */
      }
    };
    ws.onopen = () => {
      backoff = 500;
    };
    ws.onclose = () => {
      if (closedByCaller) return;
      setTimeout(open, backoff);
      backoff = Math.min(backoff * 2, 16_000);
    };
    ws.onerror = () => ws?.close();
  };

  open();

  return {
    close: () => {
      closedByCaller = true;
      ws?.close();
    },
  };
}
