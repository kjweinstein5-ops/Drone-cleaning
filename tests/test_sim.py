"""Integration test: run the full simulation loop without hardware or LLM calls."""

import asyncio
import pytest
from sim.scenario import SimScenario


@pytest.mark.asyncio
async def test_sim_full_loop_no_fails():
    scenario = SimScenario(fail_zones=[])
    await scenario.run()


@pytest.mark.asyncio
async def test_sim_full_loop_with_fail():
    scenario = SimScenario(fail_zones=["STUCCO-N"])
    await scenario.run()
