"""Tests for the bottoms-up revenue model.

These lock in the *structure* of the model, not the (unvalidated) assumptions.
"""

import pytest

from propwash.backend.reports.revenue_model import (
    Assumptions,
    ScaleScenario,
    capex_per_crew,
    crew_annual_capacity_revenue,
    default_route_to_10m,
    licensing_upside_later,
    owner_operated_premium_route,
    owner_operated_volume_route,
)


def test_single_crew_capacity():
    a = Assumptions()
    # 300 kW/day * $12/kW * 200 days = $720,000
    assert crew_annual_capacity_revenue(a) == pytest.approx(720_000.0)


def test_capex_per_crew():
    a = Assumptions()
    assert capex_per_crew(a) == pytest.approx(104_500.0)


def test_owner_operated_premium_reaches_10m():
    scenario = owner_operated_premium_route()
    assert scenario.total_revenue() >= 10_000_000.0


def test_owner_operated_volume_reaches_10m():
    scenario = owner_operated_volume_route()
    assert scenario.total_revenue() >= 10_000_000.0


def test_owner_operated_has_no_licensing_revenue():
    # The core owner-operated plan must NOT depend on a SaaS/licensing stream.
    for scenario in (owner_operated_premium_route(), owner_operated_volume_route()):
        saas = next(s for s in scenario.streams() if "SaaS" in s.name)
        assert saas.revenue == 0.0


def test_premium_route_uses_fewer_crews_than_volume():
    assert owner_operated_premium_route().own_crews < owner_operated_volume_route().own_crews


def test_default_route_is_owner_operated_premium():
    # Back-compat alias should now point at the recommended owner-operated route.
    assert default_route_to_10m().own_crews == owner_operated_premium_route().own_crews
    assert default_route_to_10m().saas_fleets == 0


def test_services_margin_around_50pct():
    scenario = owner_operated_premium_route()
    margin = scenario.total_gross_profit() / scenario.total_revenue()
    assert 0.45 <= margin <= 0.55


def test_licensing_upside_is_reference_only_and_adds_saas():
    # The "later" reference scenario does include SaaS — to size the future upside.
    later = licensing_upside_later()
    saas = next(s for s in later.streams() if "SaaS" in s.name)
    assert saas.revenue > 0.0


def test_scenario_is_tunable():
    base = owner_operated_premium_route()
    leaner = ScaleScenario(label="lean", own_crews=3, saas_fleets=0, assumptions=base.assumptions)
    assert leaner.total_revenue() < base.total_revenue()
