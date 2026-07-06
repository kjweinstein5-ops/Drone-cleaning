/** Subscribe to telemetry events for a single job (filters by job_id). */
import { useEffect, useState } from 'react';
import { useTelemetryContext } from './TelemetryProvider';
import type { TelemetryEvent } from '@/api/types';

export function useJobTelemetry(jobId: string | undefined) {
  const { subscribe, connected } = useTelemetryContext();
  const [latest, setLatest] = useState<TelemetryEvent | null>(null);

  useEffect(() => {
    if (!jobId) return;
    return subscribe((e) => {
      if (e.job_id === jobId) setLatest(e);
    });
  }, [jobId, subscribe]);

  return { latest, connected };
}
