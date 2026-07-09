"""Planning — bridges the drone-scan pipeline into the cleaning plan.

Turns classified scan zones into safety-gated work orders: the "Plan" leg of
Sense → Fuse → Plan → Execute → Verify. Exclusion zones (HVAC, chimneys, people)
never become work orders. The prescription baseline comes from the versioned
surface table (data, not code — CLAUDE.md §9); the LLM Supervisor refines on top.
"""
