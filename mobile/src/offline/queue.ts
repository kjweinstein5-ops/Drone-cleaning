/**
 * Durable outbox of operator actions taken while offline.
 *
 * The operator's authority (CLAUDE.md §10) must never be lost to a network drop:
 * a "zone done" / status confirmation is queued locally and flushed on reconnect.
 */
import { storage, KEYS } from './storage';
import type { WorkOrderStatus } from '@/api/types';

export interface OutboxAction {
  id: string; // client-generated idempotency key
  kind: 'status_update';
  jobId: string;
  status: WorkOrderStatus;
  queuedAt: string;
}

export function readOutbox(): OutboxAction[] {
  return storage.getJSON<OutboxAction[]>(KEYS.outbox) ?? [];
}

export function enqueue(action: Omit<OutboxAction, 'id' | 'queuedAt'>): OutboxAction {
  const entry: OutboxAction = {
    ...action,
    id: `${action.jobId}:${action.status}:${Date.now()}`,
    queuedAt: new Date().toISOString(),
  };
  storage.setJSON(KEYS.outbox, [...readOutbox(), entry]);
  return entry;
}

export function remove(id: string): void {
  storage.setJSON(
    KEYS.outbox,
    readOutbox().filter((a) => a.id !== id),
  );
}
