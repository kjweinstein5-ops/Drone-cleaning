/**
 * Drives one zone through the operator loop:
 *   assigned -> executing -> verifying -> (done | reflagged)
 *
 * Status changes are enqueued to the durable outbox first (so an LTE drop can't
 * lose them) and then flushed. The operator remains in command throughout (§10);
 * this hook only records intent and reflects backend truth.
 */
import { useCallback, useState } from 'react';
import { enqueue } from '@/offline/queue';
import { flushOutbox } from '@/offline/sync';
import type { WorkOrderStatus } from '@/api/types';

export type ZonePhase = 'ready' | 'spraying' | 'verifying' | 'done';

export function useZoneExecution(jobId: string) {
  const [phase, setPhase] = useState<ZonePhase>('ready');
  const [syncing, setSyncing] = useState(false);

  const advance = useCallback(
    async (status: WorkOrderStatus, nextPhase: ZonePhase) => {
      enqueue({ kind: 'status_update', jobId, status });
      setPhase(nextPhase);
      setSyncing(true);
      try {
        await flushOutbox();
      } finally {
        setSyncing(false);
      }
    },
    [jobId],
  );

  return {
    phase,
    syncing,
    beginSpray: () => advance('executing', 'spraying'),
    beginVerify: () => advance('verifying', 'verifying'),
    complete: () => advance('done', 'done'),
    /** Operator abort — always available (§2, §10). */
    abort: () => advance('assigned', 'ready'),
  };
}
