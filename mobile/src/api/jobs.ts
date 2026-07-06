/** Job / work-order endpoints. Matches propwash/backend/app/routers/jobs.py. */
import { api } from './client';
import type { WorkOrder, WorkOrderStatus, VerificationResult } from './types';

/** GET /jobs */
export function listJobs(): Promise<WorkOrder[]> {
  return api.get<WorkOrder[]>('/jobs');
}

/** GET /jobs/{job_id} */
export function getJob(jobId: string): Promise<WorkOrder> {
  return api.get<WorkOrder>(`/jobs/${encodeURIComponent(jobId)}`);
}

/** POST /jobs/{job_id}/status  — operator advances the work order through its states. */
export function updateJobStatus(jobId: string, status: WorkOrderStatus): Promise<WorkOrder> {
  return api.post<WorkOrder>(`/jobs/${encodeURIComponent(jobId)}/status`, { status });
}

/** GET /jobs/{job_id}/verifications  — Post-Clean agent results (PASS/FAIL history). */
export function getVerifications(jobId: string): Promise<VerificationResult[]> {
  return api.get<VerificationResult[]>(`/jobs/${encodeURIComponent(jobId)}/verifications`);
}
