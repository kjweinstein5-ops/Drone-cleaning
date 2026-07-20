"""Platform payback model — when each drone path turns cash-positive.

Ties the platform cost model (drone_platform_cost) to per-crew revenue
(revenue_model): runs one crew's ramped monthly cash flow against each
platform's cash outlay and finds the payback month.

⚠️ Goals to validate, not facts (CLAUDE.md §15.5). Revenue assumptions come from
revenue_model (already flagged); utilization ramp and non-platform opex are new
assumptions below. The point is the *shape* of the answer, not decimal precision.

    python -m propwash.backend.reports.platform_payback
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from propwash.backend.reports.revenue_model import (
    Assumptions as RevenueAssumptions,
    crew_annual_capacity_revenue,
)
from propwash.backend.reports.drone_platform_cost import Assumptions as PlatformAssumptions


@dataclass
class PaybackAssumptions:
    # Utilization ramp for a single crew, year 1 / 2 / 3 (VALIDATE).
    utilization_ramp: tuple = (0.35, 0.60, 0.75)
    # Share of revenue kept after EVERYTHING except the drone platform
    # (labor, chemicals, travel, insurance, misc gear). VALIDATE.
    contribution_margin_ex_platform: float = 0.55
    horizon_months: int = 36


def crew_annual_revenue(year: int, rev: RevenueAssumptions, pay: PaybackAssumptions) -> float:
    cap = crew_annual_capacity_revenue(rev)
    ramp = pay.utilization_ramp
    util = ramp[min(year - 1, len(ramp) - 1)]
    return cap * util


def _platform_cash(path: str, month: int, pf: PlatformAssumptions) -> float:
    """Cash outflow for the platform in a given month (capex hits month 0)."""
    from propwash.backend.reports.drone_platform_cost import retrofit_capex
    if path == "subscription":
        return pf.sherpa_subscription_monthly
    if path == "outright":
        return (pf.sherpa_outright_capex if month == 0 else 0.0) + pf.sherpa_outright_maint_annual / 12.0
    if path == "retrofit":
        return (retrofit_capex(pf, True) if month == 0 else 0.0) + pf.retrofit_maint_annual / 12.0
    raise ValueError(f"unknown path '{path}'")


def cumulative_cashflow(
    path: str,
    rev: Optional[RevenueAssumptions] = None,
    pf: Optional[PlatformAssumptions] = None,
    pay: Optional[PaybackAssumptions] = None,
) -> List[float]:
    """Monthly cumulative net cash for one crew on a given platform."""
    rev = rev or RevenueAssumptions()
    pf = pf or PlatformAssumptions()
    pay = pay or PaybackAssumptions()

    series: List[float] = []
    cum = 0.0
    for m in range(pay.horizon_months):
        year = m // 12 + 1
        monthly_rev = crew_annual_revenue(year, rev, pay) / 12.0
        contribution = monthly_rev * pay.contribution_margin_ex_platform
        cum += contribution - _platform_cash(path, m, pf)
        series.append(cum)
    return series


def payback_month(path: str, **kw) -> Optional[int]:
    """First month (1-indexed) where cumulative cash flow is >= 0, else None."""
    series = cumulative_cashflow(path, **kw)
    for i, v in enumerate(series):
        if v >= 0:
            return i + 1
    return None


def summary(rev=None, pf=None, pay=None) -> Dict[str, dict]:
    rev = rev or RevenueAssumptions()
    pf = pf or PlatformAssumptions()
    pay = pay or PaybackAssumptions()
    out: Dict[str, dict] = {}
    for path in ("subscription", "outright", "retrofit"):
        series = cumulative_cashflow(path, rev, pf, pay)
        out[path] = {
            "payback_month": payback_month(path, rev=rev, pf=pf, pay=pay),
            "cash_y1": series[11],
            "cash_y2": series[23],
            "cash_y3": series[35],
        }
    return out


def main() -> None:
    rev, pf, pay = RevenueAssumptions(), PlatformAssumptions(), PaybackAssumptions()
    cap = crew_annual_capacity_revenue(rev)
    s = summary(rev, pf, pay)

    print("\nPROPWASH — platform payback (one crew, base pricing; estimates)\n")
    print(f"Crew capacity @ full util: ${cap:,.0f}/yr  |  ramp {pay.utilization_ramp}  |  "
          f"contribution ex-platform {pay.contribution_margin_ex_platform:.0%}")
    y1 = crew_annual_revenue(1, rev, pay)
    print(f"Year-1 crew revenue (@{pay.utilization_ramp[0]:.0%}): ${y1:,.0f}\n")

    labels = {"subscription": "Sherpa subscription", "outright": "Sherpa outright",
              "retrofit": "DJI retrofit + PSM/IHM"}
    print(f"{'PLATFORM':<26}{'Payback':>9}{'Cum cash Y1':>14}{'Y2':>14}{'Y3':>14}")
    print("-" * 77)
    for path, label in labels.items():
        d = s[path]
        pb = f"{d['payback_month']} mo" if d["payback_month"] else ">36 mo"
        print(f"{label:<26}{pb:>9}${d['cash_y1']:>12,.0f}${d['cash_y2']:>12,.0f}${d['cash_y3']:>12,.0f}")
    print("-" * 77)
    print("\nRead: once a crew is working, platform cost is small vs revenue — every path")
    print("pays back fast. The subscription's real value is protecting cash BEFORE revenue")
    print("ramps (zero capex); the retrofit wins long-run AND builds the hardware IP.\n")


if __name__ == "__main__":
    main()
