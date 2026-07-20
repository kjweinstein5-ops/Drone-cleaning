"""Tests for the cleaning-drone platform cost model."""

from __future__ import annotations

from propwash.backend.reports.drone_platform_cost import (
    Assumptions,
    breakeven_months_outright_vs_subscription,
    breakeven_months_retrofit_vs_subscription,
    comparison_table,
    retrofit_capex,
    retrofit_tco,
    sherpa_outright_tco,
    sherpa_subscription_tco,
)


def test_subscription_is_linear_opex():
    a = Assumptions()
    assert sherpa_subscription_tco(1, a) == a.sherpa_subscription_monthly * 12
    assert sherpa_subscription_tco(3, a) == 3 * sherpa_subscription_tco(1, a)


def test_psm_ihm_adds_cost():
    a = Assumptions()
    assert retrofit_tco(1, a, include_psm_ihm=True) > retrofit_tco(1, a, include_psm_ihm=False)
    assert retrofit_capex(a, True) - retrofit_capex(a, False) == a.psm_ihm_build


def test_retrofit_capex_below_sherpa_outright():
    a = Assumptions()
    assert retrofit_capex(a, True) < a.sherpa_outright_capex


def test_year1_subscription_cheaper_year3_retrofit_cheaper():
    # The crossover: subscription wins early, owned retrofit wins later.
    a = Assumptions()
    t = comparison_table(a)
    assert t["sherpa_subscription"][1] < t["retrofit_with_psm_ihm"][1]
    assert t["retrofit_with_psm_ihm"][3] < t["sherpa_subscription"][3]


def test_breakevens_positive_and_finite():
    a = Assumptions()
    be_r = breakeven_months_retrofit_vs_subscription(a, True)
    be_o = breakeven_months_outright_vs_subscription(a)
    assert 0 < be_r < 120
    assert 0 < be_o < 120
    # Retrofit (cheaper capex) breaks even before Sherpa outright.
    assert be_r < be_o


def test_assumptions_are_tunable():
    # Halving the payload price lowers retrofit capex and speeds break-even.
    base = Assumptions()
    cheaper = Assumptions(cleaning_payload=9_000.0)
    assert retrofit_capex(cheaper, True) < retrofit_capex(base, True)
    assert (
        breakeven_months_retrofit_vs_subscription(cheaper, True)
        < breakeven_months_retrofit_vs_subscription(base, True)
    )


def test_outright_eventually_beats_subscription():
    a = Assumptions()
    t = comparison_table(a, years=[1, 2, 3])
    # By year 3 the outright purchase is cheaper than paying subscription.
    assert t["sherpa_outright"][3] < t["sherpa_subscription"][3]
