"""Multi-aircraft spatial deconfliction.

Answers: *can two cleaning drones operate at the same time?*
**Yes — but only on zones far enough apart, and that must be enforced, not assumed.**

Two aircraft working the same building is a throughput multiplier (measured 1.91×
for two, 2.79× for three — see treatment_phases). The safety condition is simple
and absolute:

    Two aircraft may never work zones whose operating volumes come within the
    minimum separation distance.

Each zone's operating volume is its surface extent expanded by the standoff and
the spray reach — an aircraft working that zone can be anywhere inside it. So
separation is computed volume-to-volume, not point-to-point.

This is Tier-1 (CLAUDE.md §2): deterministic, no agent involvement, and it can
only *reduce* concurrency, never grant it. Feeds the 107.35 waiver requirement
that aircraft occupy non-overlapping work zones (docs/WAIVER_107_35.md §6).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple

Vec3 = Tuple[float, float, float]

#: Minimum distance between two aircraft operating volumes. Conservative default
#: covering position error, spray drift, gusts and reaction time.
DEFAULT_MIN_SEPARATION_M = 10.0

#: Extra radius beyond standoff to account for spray reach and drift.
SPRAY_REACH_M = 2.0


def _dist(a: Vec3, b: Vec3) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


@dataclass(frozen=True)
class ZoneVolume:
    """Bounding sphere of everywhere an aircraft may be while working a zone."""

    zone_id: str
    center: Vec3
    radius_m: float

    @staticmethod
    def from_points(zone_id: str, points: Sequence[Vec3], standoff_m: float) -> "ZoneVolume":
        """Build the operating volume from a zone's waypoints/vertices."""
        if not points:
            raise ValueError(f"zone {zone_id}: no points")
        n = len(points)
        center = (
            sum(p[0] for p in points) / n,
            sum(p[1] for p in points) / n,
            sum(p[2] for p in points) / n,
        )
        extent = max(_dist(center, p) for p in points)
        return ZoneVolume(
            zone_id=zone_id,
            center=center,
            radius_m=extent + standoff_m + SPRAY_REACH_M,
        )


def separation(a: ZoneVolume, b: ZoneVolume) -> float:
    """Gap between two operating volumes. Negative = the volumes overlap."""
    return _dist(a.center, b.center) - a.radius_m - b.radius_m


def can_work_concurrently(
    a: ZoneVolume,
    b: ZoneVolume,
    min_separation_m: float = DEFAULT_MIN_SEPARATION_M,
) -> bool:
    """True only if two aircraft can safely work these zones simultaneously."""
    return separation(a, b) >= min_separation_m


class ConflictMap:
    """Which zone pairs may NOT be worked at the same time.

    Precomputed once per job, then consulted by the scheduler.
    """

    def __init__(
        self,
        volumes: Iterable[ZoneVolume],
        min_separation_m: float = DEFAULT_MIN_SEPARATION_M,
    ) -> None:
        self.min_separation_m = min_separation_m
        self._volumes: Dict[str, ZoneVolume] = {v.zone_id: v for v in volumes}
        self._conflicts: Set[FrozenSet[str]] = set()
        for a, b in combinations(self._volumes.values(), 2):
            if not can_work_concurrently(a, b, min_separation_m):
                self._conflicts.add(frozenset((a.zone_id, b.zone_id)))

    def conflicts(self, zone_a: str, zone_b: str) -> bool:
        if zone_a == zone_b:
            return True                      # a zone never runs concurrently with itself
        return frozenset((zone_a, zone_b)) in self._conflicts

    def compatible_with_all(self, zone_id: str, active: Iterable[str]) -> bool:
        """Can `zone_id` start while `active` zones are being worked?"""
        return not any(self.conflicts(zone_id, other) for other in active)

    def conflicting_pairs(self) -> List[Tuple[str, str]]:
        return sorted(tuple(sorted(p)) for p in self._conflicts)

    def max_concurrent_aircraft(self) -> int:
        """Largest set of mutually-compatible zones = concurrency ceiling.

        Greedy lower bound: enough aircraft beyond this cannot be used
        simultaneously no matter how work is scheduled.
        """
        best = 1
        ids = sorted(self._volumes)
        for start in ids:
            group = [start]
            for cand in ids:
                if cand == start:
                    continue
                if all(not self.conflicts(cand, g) for g in group):
                    group.append(cand)
            best = max(best, len(group))
        return best

    def separation_report(self) -> List[dict]:
        """Per-pair separations — waiver evidence that zones are non-overlapping."""
        rows = []
        for a, b in combinations(sorted(self._volumes), 2):
            gap = separation(self._volumes[a], self._volumes[b])
            rows.append({
                "zone_a": a,
                "zone_b": b,
                "separation_m": round(gap, 2),
                "concurrent_ok": gap >= self.min_separation_m,
            })
        return rows
