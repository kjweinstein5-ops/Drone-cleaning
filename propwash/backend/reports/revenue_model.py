"""Bottoms-up revenue model for the path to $10M/year.

PURPOSE: make the $10M target reproducible and tweakable instead of a vibe.
Every assumption is a GOAL TO VALIDATE (CLAUDE.md §15.5), not a fact. Some inputs
(e.g. Sherpa unit cost) are UNVERIFIED and flagged as such — confirm before relying.

Run: python -m propwash.backend.reports.revenue_model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Assumptions (EDIT THESE — all are goals-to-validate, not facts)
# ---------------------------------------------------------------------------

@dataclass
class Assumptions:
    # --- Commercial solar services (the wedge) ---
    price_per_kw_per_clean: float = 12.0      # $/kW per clean (commercial). VALIDATE.
    cleans_per_site_per_year: int = 2         # recurring biannual
    crew_kw_per_day: float = 300.0            # cleaning throughput per crew/day. VALIDATE.
    crew_working_days_per_year: int = 200
    services_gross_margin: float = 0.50       # after labor, chem, travel, depreciation

    # --- Platform / SaaS licensing to other operators ---
    saas_arr_per_fleet: float = 27_000.0      # ~$2.25K/mo per operator fleet. VALIDATE.
    saas_gross_margin: float = 0.80

    # --- Multi-surface upsell + verification premium on existing accounts ---
    # Modeled as an uplift fraction on top of own-services revenue.
    upsell_uplift_fraction: float = 0.48

    # --- Capital (UNVERIFIED — confirm vendor pricing) ---
    sherpa_unit_cost: float = 60_000.0        # Lucid Sherpa, UNVERIFIED estimate
    autel_unit_cost: float = 9_500.0          # Autel EVO II 640T
    truck_and_kit_per_crew: float = 35_000.0


def crew_annual_capacity_revenue(a: Assumptions) -> float:
    """Max gross services revenue one fully-utilized crew can produce per year."""
    return a.crew_kw_per_day * a.price_per_kw_per_clean * a.crew_working_days_per_year


def capex_per_crew(a: Assumptions) -> float:
    return a.sherpa_unit_cost + a.autel_unit_cost + a.truck_and_kit_per_crew


@dataclass
class RevenueStream:
    name: str
    revenue: float
    gross_margin: float

    @property
    def gross_profit(self) -> float:
        return self.revenue * self.gross_margin


@dataclass
class ScaleScenario:
    label: str
    own_crews: int
    saas_fleets: int
    assumptions: Assumptions = field(default_factory=Assumptions)

    def services_revenue(self) -> float:
        return self.own_crews * crew_annual_capacity_revenue(self.assumptions)

    def saas_revenue(self) -> float:
        return self.saas_fleets * self.assumptions.saas_arr_per_fleet

    def upsell_revenue(self) -> float:
        return self.services_revenue() * self.assumptions.upsell_uplift_fraction

    def streams(self) -> List[RevenueStream]:
        a = self.assumptions
        return [
            RevenueStream("Own services (recurring commercial)", self.services_revenue(), a.services_gross_margin),
            RevenueStream("Platform SaaS (licensed operators)", self.saas_revenue(), a.saas_gross_margin),
            RevenueStream("Multi-surface upsell + verification premium", self.upsell_revenue(), a.services_gross_margin),
        ]

    def total_revenue(self) -> float:
        return sum(s.revenue for s in self.streams())

    def total_gross_profit(self) -> float:
        return sum(s.gross_profit for s in self.streams())

    def total_capex(self) -> float:
        return self.own_crews * capex_per_crew(self.assumptions)


def owner_operated_volume_route() -> ScaleScenario:
    """OWNER-OPERATED, no licensing — reach $10M on crews + multi-surface upsell alone.

    Base pricing. This is the brute-force services route (more crews, more ops).
    """
    return ScaleScenario(label="Owner-operated — VOLUME route (Year ~5)", own_crews=10, saas_fleets=0)


def owner_operated_premium_route() -> ScaleScenario:
    """OWNER-OPERATED, no licensing — RECOMMENDED.

    Fewer crews by raising revenue-per-crew: a verification premium on price/kW,
    larger commercial sites, and heavier multi-surface bundling. Higher margin,
    less operational sprawl than the volume route.
    """
    premium = Assumptions(
        price_per_kw_per_clean=16.0,   # verification/ROI-proof premium vs $12 base. VALIDATE.
        upsell_uplift_fraction=0.55,   # stronger multi-surface bundling per account
    )
    return ScaleScenario(
        label="Owner-operated — PREMIUM route (recommended, Year ~5)",
        own_crews=7,
        saas_fleets=0,
        assumptions=premium,
    )


def licensing_upside_later() -> ScaleScenario:
    """OPTIONAL FUTURE upside — software licensing as a Phase 3+ second business model.

    Not part of the owner-operated plan. Shown only to size the later opportunity.
    """
    return ScaleScenario(label="Later upside — add licensing (Phase 3+)", own_crews=6, saas_fleets=140)


# Back-compat alias (older callers/tests) — points at the recommended owner-operated route.
def default_route_to_10m() -> ScaleScenario:
    return owner_operated_premium_route()


def _print_scenario(scenario: ScaleScenario) -> None:
    print(f"--- {scenario.label} ---")
    fleets = f"  |  Licensed SaaS fleets: {scenario.saas_fleets}" if scenario.saas_fleets else ""
    print(f"  Own crews: {scenario.own_crews}{fleets}")
    print()
    print(f"  {'Stream':<46}{'Revenue':>14}{'Gross profit':>16}")
    print("  " + "-" * 74)
    for s in scenario.streams():
        if s.revenue <= 0:
            continue
        print(f"  {s.name:<46}${s.revenue:>12,.0f}${s.gross_profit:>14,.0f}")
    print("  " + "-" * 74)
    print(f"  {'TOTAL':<46}${scenario.total_revenue():>12,.0f}${scenario.total_gross_profit():>14,.0f}")
    print(f"  Blended gross margin: {scenario.total_gross_profit()/scenario.total_revenue():.0%}")
    print(f"  Crew capex to stand up {scenario.own_crews} crews: ${scenario.total_capex():,.0f}")
    print()


def print_report() -> None:
    a = Assumptions()
    print("=" * 68)
    print("PROPWASH — bottoms-up revenue model (goals to validate, not facts)")
    print("OWNER-OPERATED company — no licensing in the core plan")
    print("=" * 68)
    print(f"One crew's annual capacity at base pricing (gross): ${crew_annual_capacity_revenue(a):,.0f}")
    print(f"Capex per crew (UNVERIFIED Sherpa price): ${capex_per_crew(a):,.0f}")
    print()
    _print_scenario(owner_operated_premium_route())
    _print_scenario(owner_operated_volume_route())
    print("(For reference only — NOT the current plan:)")
    _print_scenario(licensing_upside_later())
    print("=" * 68)


if __name__ == "__main__":
    print_report()
