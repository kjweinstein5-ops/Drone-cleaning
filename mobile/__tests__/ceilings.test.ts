import { safetyNotesFor, DISPLAY_PRESSURE_CEILING_BAR } from '@/safety/ceilings';
import type { Prescription } from '@/api/types';

function rx(overrides: Partial<Prescription>): Prescription {
  return {
    zone_id: 'Z1',
    pressure_bar: 5,
    chemical: 'standard_degreaser',
    chemical_mix_ratio: 0.3,
    dwell_seconds: 30,
    nozzle_id: 3,
    standoff_m: 1.2,
    coverage_pattern: 'sweep_ns',
    safety_margin_m: 0.15,
    requeue_on_fail_pressure_delta: 0.5,
    ...overrides,
  };
}

describe('safety display ceilings (§9)', () => {
  it('flags detergent on a solar panel as critical', () => {
    const notes = safetyNotesFor('solar_panel', rx({ chemical: 'standard_degreaser', pressure_bar: 1.8 }));
    expect(notes.some((n) => n.level === 'critical' && /Do NOT proceed/.test(n.message))).toBe(true);
  });

  it('does not flag DI-only water on a solar panel for chemical', () => {
    const notes = safetyNotesFor('solar_panel', rx({ chemical: 'di_water_only', pressure_bar: 1.8 }));
    expect(notes.some((n) => /Do NOT proceed/.test(n.message))).toBe(false);
  });

  it('flags over-pressure above the display ceiling', () => {
    const surface = 'composite_shingle';
    const over = DISPLAY_PRESSURE_CEILING_BAR[surface] + 1;
    const notes = safetyNotesFor(surface, rx({ pressure_bar: over }));
    expect(notes.some((n) => /exceeds/.test(n.message))).toBe(true);
  });

  it('is silent for an in-spec standard clean', () => {
    const notes = safetyNotesFor('composite_shingle', rx({ pressure_bar: 5.5 }));
    expect(notes).toHaveLength(0);
  });
});
