"""Tests for the platform payback model."""

from __future__ import annotations

from propwash.backend.reports.platform_payback import (
    PaybackAssumptions,
    cumulative_cashflow,
    crew_annual_revenue,
    payback_month,
    summary,
)
from propwash.backend.reports.revenue_model import Assumptions as RevenueAssumptions


def test_summary_covers_all_paths():
    s = summary()
    assert set(s) == {"subscription", "outright", "retrofit"}
    for d in s.values():
        assert d["payback_month"] is not None


def test_subscription_pays_back_before_capex_paths():
    # No capex → subscription recovers first; retrofit (cheaper capex) before outright.
    sub = payback_month("subscription")
    retro = payback_month("retrofit")
    out = payback_month("outright")
    assert sub <= retro <= out


def test_cumulative_cash_grows_over_time():
    series = cumulative_cashflow("retrofit")
    assert series[35] > series[11]  # year 3 cum cash > year 1


def test_retrofit_retains_most_cash_by_year3():
    # Cheapest platform long-run → most cash retained by year 3.
    s = summary()
    assert s["retrofit"]["cash_y3"] >= s["subscription"]["cash_y3"]
    assert s["retrofit"]["cash_y3"] >= s["outright"]["cash_y3"]


def test_lower_utilization_stretches_payback():
    lean = PaybackAssumptions(utilization_ramp=(0.10, 0.15, 0.20))
    base_pb = payback_month("retrofit")
    lean_pb = payback_month("retrofit", pay=lean)
    assert lean_pb > base_pb


def test_revenue_ramps_by_year():
    rev, pay = RevenueAssumptions(), PaybackAssumptions()
    y1 = crew_annual_revenue(1, rev, pay)
    y2 = crew_annual_revenue(2, rev, pay)
    assert y2 > y1
