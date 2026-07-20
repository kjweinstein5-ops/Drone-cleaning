"""Cleaning-drone platform cost model — Sherpa vs. owned DJI retrofit.

Reproducible 1–3 year total-cost-of-ownership comparison for the platform
decision in docs/decisions/CLEANING_DRONE_PLATFORM.md.

⚠️ ALL NUMBERS ARE ESTIMATES TO VALIDATE, not facts (CLAUDE.md §15.5). The
retrofit cleaning-payload price is the biggest unknown (vendors quote privately) —
tune `Assumptions` and re-run. Shared running costs (chemicals, water, insurance,
labor) are the SAME across platforms, so they wash out of a comparison and are
deliberately excluded; this models platform cost only.

    python -m propwash.backend.reports.drone_platform_cost
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Assumptions:
    # ── Lucid Sherpa (purpose-built, Path A) ──
    sherpa_subscription_monthly: float = 2_950.0   # Lucid Refresh, incl. maintenance
    sherpa_outright_capex: float = 75_000.0
    sherpa_outright_maint_annual: float = 5_000.0  # parts/service after warranty (est.)

    # ── Owned DJI retrofit (Path B/C, unlocks PSM/IHM) ──
    dji_airframe: float = 14_000.0        # Matrice 350 RTK (est.)
    cleaning_payload: float = 18_000.0    # Foxtech/drone-payload kit — ⚠ NOT public, mid-range est.
    ground_water_system: float = 3_000.0  # pump + hose reel
    integration_labor: float = 5_000.0    # one-time setup/mounts/calibration
    psm_ihm_build: float = 4_000.0        # PSM + IHM installed on one rig (DYNAMIC_PRESSURE_HARDWARE.md)
    retrofit_maint_annual: float = 3_000.0  # batteries/wear (est.)


# ── TCO functions: cumulative platform cost at end of year N ──────────────────

def sherpa_subscription_tco(years: int, a: Assumptions) -> float:
    """No capex — pure opex; maintenance included in the subscription."""
    return a.sherpa_subscription_monthly * 12 * years


def sherpa_outright_tco(years: int, a: Assumptions) -> float:
    return a.sherpa_outright_capex + a.sherpa_outright_maint_annual * years


def retrofit_capex(a: Assumptions, include_psm_ihm: bool = True) -> float:
    base = a.dji_airframe + a.cleaning_payload + a.ground_water_system + a.integration_labor
    return base + (a.psm_ihm_build if include_psm_ihm else 0.0)


def retrofit_tco(years: int, a: Assumptions, include_psm_ihm: bool = True) -> float:
    return retrofit_capex(a, include_psm_ihm) + a.retrofit_maint_annual * years


# ── Break-even: months until owned (retrofit) undercuts subscription ──────────

def breakeven_months_retrofit_vs_subscription(a: Assumptions, include_psm_ihm: bool = True) -> float:
    """Month at which cumulative owned-retrofit cost drops below subscription."""
    capex = retrofit_capex(a, include_psm_ihm)
    sub_monthly = a.sherpa_subscription_monthly
    retrofit_monthly = a.retrofit_maint_annual / 12.0
    # capex + retrofit_monthly*m  <=  sub_monthly*m  →  m >= capex / (sub - retrofit_monthly)
    denom = sub_monthly - retrofit_monthly
    if denom <= 0:
        return float("inf")
    return capex / denom


def breakeven_months_outright_vs_subscription(a: Assumptions) -> float:
    capex = a.sherpa_outright_capex
    sub_monthly = a.sherpa_subscription_monthly
    outright_monthly = a.sherpa_outright_maint_annual / 12.0
    denom = sub_monthly - outright_monthly
    if denom <= 0:
        return float("inf")
    return capex / denom


def comparison_table(a: Assumptions | None = None, years: List[int] | None = None) -> Dict[str, Dict[int, float]]:
    a = a or Assumptions()
    years = years or [1, 2, 3]
    return {
        "sherpa_subscription": {y: sherpa_subscription_tco(y, a) for y in years},
        "sherpa_outright": {y: sherpa_outright_tco(y, a) for y in years},
        "retrofit_with_psm_ihm": {y: retrofit_tco(y, a, True) for y in years},
        "retrofit_base_only": {y: retrofit_tco(y, a, False) for y in years},
    }


def main() -> None:
    a = Assumptions()
    table = comparison_table(a)

    print("\nPROPWASH — cleaning-drone platform TCO (platform cost only; estimates)\n")
    print(f"{'PLATFORM':<28}{'Year 1':>12}{'Year 2':>12}{'Year 3':>12}")
    print("-" * 64)
    labels = {
        "sherpa_subscription": "Sherpa subscription",
        "sherpa_outright": "Sherpa outright",
        "retrofit_with_psm_ihm": "DJI retrofit + PSM/IHM",
        "retrofit_base_only": "DJI retrofit (base only)",
    }
    for key, label in labels.items():
        row = table[key]
        print(f"{label:<28}" + "".join(f"${row[y]:>10,.0f} " for y in [1, 2, 3]))
    print("-" * 64)

    be_r = breakeven_months_retrofit_vs_subscription(a, True)
    be_o = breakeven_months_outright_vs_subscription(a)
    print(f"\nRetrofit (+PSM/IHM) undercuts subscription after ~{be_r:.0f} months")
    print(f"Sherpa outright undercuts subscription after ~{be_o:.0f} months")
    print(f"Retrofit capex (+PSM/IHM): ${retrofit_capex(a, True):,.0f} "
          f"vs Sherpa outright capex: ${a.sherpa_outright_capex:,.0f}\n")
    print("⚠ Estimates to validate (esp. cleaning-payload price). Shared running")
    print("  costs (chem/water/labor/insurance) excluded — identical across platforms.\n")


if __name__ == "__main__":
    main()
