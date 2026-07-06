/**
 * TypeScript mirror of the PROPWASH backend Pydantic models.
 *
 * ⚠ SOURCE OF TRUTH is propwash/backend/models/*.py — keep these in sync.
 *   zone.py -> ZoneSignature / SurfaceType / DataSource
 *   prescription.py -> Prescription / ChemicalType / CoveragePattern
 *   work_order.py -> WorkOrder / WorkOrderStatus
 *   verification.py -> VerificationResult / Verdict
 *
 * Note (CLAUDE.md §5): grimeConfidence / residualConfidence are PROXY scores
 * inferred from thermal + RGB only. They are NOT spectral biofilm measurements.
 */

export type SurfaceType =
  | 'composite_shingle'
  | 'clay_tile'
  | 'concrete_tile'
  | 'solar_panel'
  | 'window_glass'
  | 'stucco'
  | 'gutter_aluminum'
  | 'unknown';

export type DataSource = 'thermal' | 'rgb' | 'sfm';

export interface ZoneSignature {
  zone_id: string;
  label: string;
  surface_type: SurfaceType;
  pitch_deg: number;
  /** PROXY score 0..1 — thermal+RGB inference, not spectral. §5 */
  grime_confidence: number;
  moisture_index: number;
  geometry_ref?: string | null;
  source: DataSource[];
  property_id?: string | null;
  job_id?: string | null;
}

export type ChemicalType =
  | 'eco_degreaser'
  | 'standard_degreaser'
  | 'degreaser_solvent_blend'
  | 'ammonia_free'
  | 'di_water_only';

export type CoveragePattern = 'sweep_ns' | 'sweep_ew' | 'spiral_in' | 'spot';

export interface Prescription {
  zone_id: string;
  pressure_bar: number;
  chemical: ChemicalType;
  chemical_mix_ratio: number;
  dwell_seconds: number;
  nozzle_id: number;
  nozzle_angle_deg?: number | null;
  nozzle_orifice_mm?: number | null;
  standoff_m: number;
  coverage_pattern: CoveragePattern;
  safety_margin_m: number;
  requeue_on_fail_pressure_delta: number;
}

export type WorkOrderStatus =
  | 'queued'
  | 'assigned'
  | 'executing'
  | 'verifying'
  | 'done'
  | 'reflagged';

export interface WorkOrder {
  job_id: string;
  zone: ZoneSignature;
  prescription: Prescription;
  verify_thermal_post: boolean;
  status: WorkOrderStatus;
  attempt: number;
  operator_notes?: string | null;
  created_at: string;
  updated_at: string;
  execution_log?: Record<string, unknown> | null;
}

export type Verdict = 'PASS' | 'FAIL';

export interface VerificationResult {
  zone_id: string;
  job_id: string;
  attempt: number;
  /** Post-clean PROXY residual score 0..1. §5 */
  residual_confidence: number;
  threshold: number;
  verdict: Verdict;
  delta_applied?: Record<string, unknown> | null;
  execution_vs_prescription?: Record<string, unknown> | null;
  verified_at: string;
}

/** Telemetry frame broadcast by /jobs/ws/telemetry (see routers/jobs.py _broadcast). */
export interface TelemetryEvent {
  event: string; // e.g. "job_status"
  job_id?: string;
  status?: WorkOrderStatus;
  [key: string]: unknown;
}
