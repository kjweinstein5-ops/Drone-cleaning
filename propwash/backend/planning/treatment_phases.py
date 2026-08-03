"""Multi-phase surface treatment + dwell pipelining.

Real exterior cleaning is not one pass. The professional soft-wash sequence is:

    PRE_SOAK  → wet the surface (protects substrate + landscaping, loosens
                debris, stops chemical flashing off dry/hot surfaces)
    CHEMICAL  → apply detergent at the prescribed mix
    DWELL     → chemical works. **No aircraft required** — this is dead time.
    RINSE     → wash it down

**The efficiency insight:** DWELL needs no aircraft. A single drone hovering
through dwell burns battery doing nothing. With more than one aircraft the phases
*pipeline* — pre-soak zone B while zone A dwells — which is a direct throughput
multiplier and precisely what a 107.35 waiver authorizes
(docs/WAIVER_107_35.md).

This module is aircraft-count agnostic: 1 aircraft runs the phases sequentially,
N aircraft overlap them. The scheduler computes both so the gain is measurable.

SAFETY: pre-soak and rinse are water-only by definition. Solar panels are
DI-water-only end to end (CLAUDE.md §9) — the phase plan must never introduce
detergent on a surface whose prescription forbids it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from propwash.backend.models.prescription import ChemicalType, Prescription


class TreatmentPhase(str, Enum):
    PRE_SOAK = "pre_soak"   # water only — wet the surface first
    CHEMICAL = "chemical"   # apply detergent
    DWELL = "dwell"         # no aircraft needed
    RINSE = "rinse"         # water only — wash down


#: Phases that occupy an aircraft. DWELL deliberately does not.
ACTIVE_PHASES = (TreatmentPhase.PRE_SOAK, TreatmentPhase.CHEMICAL, TreatmentPhase.RINSE)

#: Pressure multipliers per phase, relative to the prescribed cleaning pressure.
#: Pre-soak and rinse are gentler — they wet and flush, they don't strip.
_PHASE_PRESSURE_FACTOR: Dict[TreatmentPhase, float] = {
    TreatmentPhase.PRE_SOAK: 0.55,
    TreatmentPhase.CHEMICAL: 0.70,
    TreatmentPhase.RINSE: 0.85,
}

#: Phase duration as a fraction of the zone's active pass time.
_PHASE_TIME_FACTOR: Dict[TreatmentPhase, float] = {
    TreatmentPhase.PRE_SOAK: 0.45,
    TreatmentPhase.CHEMICAL: 0.60,
    TreatmentPhase.RINSE: 1.00,
}


@dataclass(frozen=True)
class PhaseStep:
    """One phase of one zone's treatment."""

    zone_id: str
    phase: TreatmentPhase
    duration_s: float
    pressure_bar: float
    chemical: ChemicalType
    chemical_mix_ratio: float

    @property
    def needs_aircraft(self) -> bool:
        return self.phase in ACTIVE_PHASES


def build_phase_plan(
    zone_id: str,
    prescription: Prescription,
    active_pass_seconds: float,
) -> List[PhaseStep]:
    """Expand a prescription into its treatment phases.

    Pre-soak and rinse are always water-only. The chemical phase carries the
    prescribed chemistry — which for solar (DI_WATER_ONLY) means the whole
    sequence stays water-only, as required.
    """
    water = ChemicalType.DI_WATER_ONLY
    steps: List[PhaseStep] = []

    for phase in (TreatmentPhase.PRE_SOAK, TreatmentPhase.CHEMICAL,
                  TreatmentPhase.DWELL, TreatmentPhase.RINSE):
        if phase is TreatmentPhase.DWELL:
            steps.append(PhaseStep(
                zone_id=zone_id, phase=phase,
                duration_s=float(prescription.dwell_seconds),
                pressure_bar=0.0, chemical=water, chemical_mix_ratio=0.0,
            ))
            continue

        is_chem = phase is TreatmentPhase.CHEMICAL
        steps.append(PhaseStep(
            zone_id=zone_id,
            phase=phase,
            duration_s=active_pass_seconds * _PHASE_TIME_FACTOR[phase],
            pressure_bar=round(
                prescription.pressure_bar * _PHASE_PRESSURE_FACTOR[phase], 3),
            chemical=prescription.chemical if is_chem else water,
            chemical_mix_ratio=prescription.chemical_mix_ratio if is_chem else 0.0,
        ))
    return steps


# ── scheduling ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ScheduledStep:
    zone_id: str
    phase: TreatmentPhase
    aircraft: Optional[int]      # None during DWELL — no aircraft occupied
    start_s: float
    end_s: float


@dataclass
class Schedule:
    steps: List[ScheduledStep] = field(default_factory=list)
    aircraft_count: int = 1

    @property
    def makespan_s(self) -> float:
        return max((s.end_s for s in self.steps), default=0.0)

    @property
    def dwell_seconds_hidden(self) -> float:
        """Dwell time overlapped with active work on other zones."""
        hidden = 0.0
        for d in (s for s in self.steps if s.phase is TreatmentPhase.DWELL):
            busy = [
                s for s in self.steps
                if s.aircraft is not None and s.start_s < d.end_s and s.end_s > d.start_s
            ]
            for b in busy:
                hidden += max(0.0, min(d.end_s, b.end_s) - max(d.start_s, b.start_s))
        return hidden


def schedule_phases(
    phase_plans: List[List[PhaseStep]],
    aircraft_count: int = 1,
) -> Schedule:
    """Schedule zone phase-plans across N aircraft, pipelining through dwell.

    Rules enforced:
      * a zone's phases run strictly in order (can't rinse before you soak);
      * an aircraft does one thing at a time;
      * DWELL blocks its own zone but occupies NO aircraft — so other zones can
        be worked during it. That overlap is the entire throughput gain.

    Greedy earliest-start assignment: good schedules, no solver dependency.
    """
    if aircraft_count < 1:
        raise ValueError("aircraft_count must be >= 1")

    free_at = [0.0] * aircraft_count          # when each aircraft is next free
    scheduled: List[ScheduledStep] = []
    # (plan, next step index, when that zone is ready to continue)
    pending: List[Tuple[List[PhaseStep], int, float]] = [(p, 0, 0.0) for p in phase_plans]

    while pending:
        # Pick the step that can start earliest; tie-break on longer duration first.
        best_i = 0
        best_start = float("inf")
        best_ac: Optional[int] = None
        for i, (plan, idx, ready) in enumerate(pending):
            step = plan[idx]
            if step.needs_aircraft:
                ac = min(range(aircraft_count), key=lambda a: free_at[a])
                start = max(ready, free_at[ac])
            else:
                ac, start = None, ready
            if start < best_start or (
                start == best_start and step.duration_s > pending[best_i][0][pending[best_i][1]].duration_s
            ):
                best_i, best_start, best_ac = i, start, ac

        plan, idx, _ = pending[best_i]
        step = plan[idx]
        end = best_start + step.duration_s
        scheduled.append(ScheduledStep(
            zone_id=step.zone_id, phase=step.phase,
            aircraft=best_ac, start_s=best_start, end_s=end,
        ))
        if best_ac is not None:
            free_at[best_ac] = end

        if idx + 1 < len(plan):
            pending[best_i] = (plan, idx + 1, end)
        else:
            pending.pop(best_i)

    scheduled.sort(key=lambda s: (s.start_s, s.zone_id))
    return Schedule(steps=scheduled, aircraft_count=aircraft_count)


def throughput_gain(phase_plans: List[List[PhaseStep]], aircraft_count: int) -> float:
    """Speed-up of N aircraft vs 1 (e.g. 1.6 = 60% faster)."""
    solo = schedule_phases(phase_plans, 1).makespan_s
    multi = schedule_phases(phase_plans, aircraft_count).makespan_s
    return (solo / multi) if multi > 0 else 1.0
