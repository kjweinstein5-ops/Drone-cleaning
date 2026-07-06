/**
 * Client-side safety DISPLAY helpers.
 *
 * ⚠ NOT AUTHORITATIVE. Per CLAUDE.md §2 the deterministic safety layer lives in
 * the backend (propwash/backend/safety/) and on-aircraft. These values exist only
 * to WARN the operator in the UI. Never gate hardware on this file.
 *
 * The numbers mirror the conservative ceilings in prescriptions/surface_treatment_v1.json
 * and CLAUDE.md §9. Solar is the most failure-sensitive surface (DI only, hard ceiling).
 */
import type { SurfaceType, Prescription } from '@/api/types';

/** Advisory display ceilings (bar). Backend enforces the real limits. */
export const DISPLAY_PRESSURE_CEILING_BAR: Record<SurfaceType, number> = {
  composite_shingle: 6.5,
  clay_tile: 6.0,
  concrete_tile: 6.0,
  solar_panel: 2.0, // hard ceiling — high pressure cracks cells (§9)
  window_glass: 2.4,
  stucco: 4.5,
  gutter_aluminum: 7.0,
  unknown: 4.0, // conservative default
};

export interface SafetyNote {
  level: 'info' | 'warn' | 'critical';
  message: string;
}

/** Produce operator-facing safety notes for a zone's prescription. */
export function safetyNotesFor(
  surface: SurfaceType,
  rx: Prescription,
): SafetyNote[] {
  const notes: SafetyNote[] = [];

  if (surface === 'solar_panel') {
    notes.push({
      level: 'critical',
      message: 'SOLAR — DI water only, no detergent. Detergent residue cuts panel output.',
    });
    if (rx.chemical !== 'di_water_only') {
      notes.push({
        level: 'critical',
        message: `Prescription chemical is "${rx.chemical}" on a solar panel. Do NOT proceed — flag to ops.`,
      });
    }
  }

  const ceiling = DISPLAY_PRESSURE_CEILING_BAR[surface];
  if (rx.pressure_bar > ceiling) {
    notes.push({
      level: 'critical',
      message: `Prescribed ${rx.pressure_bar} bar exceeds the ${ceiling} bar display ceiling for ${surface}. Verify with ops before spraying.`,
    });
  }

  return notes;
}
