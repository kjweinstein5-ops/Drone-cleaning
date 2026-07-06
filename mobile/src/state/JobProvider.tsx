/**
 * Holds the current job packet in memory + cache. Loads from the backend when
 * online, falls back to the last cached packet when offline (field reality).
 */
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { listJobs } from '@/api/jobs';
import { storage, KEYS } from '@/offline/storage';
import { flushOutbox } from '@/offline/sync';
import type { WorkOrder } from '@/api/types';

interface JobContextValue {
  jobs: WorkOrder[];
  loading: boolean;
  offline: boolean;
  refresh: () => Promise<void>;
}

const JobContext = createContext<JobContextValue | null>(null);

export function JobProvider({ children }: { children: React.ReactNode }) {
  const [jobs, setJobs] = useState<WorkOrder[]>(
    () => storage.getJSON<WorkOrder[]>(KEYS.jobPacket) ?? [],
  );
  const [loading, setLoading] = useState(false);
  const [offline, setOffline] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      // Opportunistically flush anything queued while offline, then reload.
      await flushOutbox();
      const fresh = await listJobs();
      setJobs(fresh);
      storage.setJSON(KEYS.jobPacket, fresh);
      setOffline(false);
    } catch {
      // Stay on cached packet; mark offline so the UI can show a banner.
      setOffline(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <JobContext.Provider value={{ jobs, loading, offline, refresh }}>
      {children}
    </JobContext.Provider>
  );
}

export function useJobs(): JobContextValue {
  const ctx = useContext(JobContext);
  if (!ctx) throw new Error('useJobs must be used within <JobProvider>');
  return ctx;
}
