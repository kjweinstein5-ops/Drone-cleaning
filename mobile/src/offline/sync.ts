/**
 * Flush the outbox to the backend. Server state is authoritative on conflict
 * (the operator's local action is replayed, but the server's returned WorkOrder
 * is the truth we cache afterwards).
 */
import { readOutbox, remove } from './queue';
import { updateJobStatus } from '@/api/jobs';
import { ApiError } from '@/api/client';

export async function flushOutbox(): Promise<{ sent: number; remaining: number }> {
  const pending = readOutbox();
  let sent = 0;

  for (const action of pending) {
    try {
      if (action.kind === 'status_update') {
        await updateJobStatus(action.jobId, action.status);
      }
      remove(action.id);
      sent += 1;
    } catch (err) {
      if (err instanceof ApiError) {
        // A real rejection (e.g. 404 job gone / server-wins conflict): drop the
        // stale action rather than retrying forever. Server state wins.
        // TODO(PROPWASH): surface dropped actions to an operator review list.
        remove(action.id);
        continue;
      }
      // Still offline — stop; try again on the next reconnect.
      break;
    }
  }

  return { sent, remaining: readOutbox().length };
}
