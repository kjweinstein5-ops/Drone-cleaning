"""Diagnosis + planning logic.

Two modes:
  * If ANTHROPIC_API_KEY is set, calls the Claude API (multimodal) for a real diagnosis.
  * Otherwise returns an honest, clearly-labeled STUB so the full loop runs with no key
    and no hardware (stub=True in the response).

Model ids are configurable via env. Defaults to a fast multimodal model; override with
ARCHOICE_MODEL for higher-capability runs.
"""
from __future__ import annotations

import json
import os

from models import (
    Diagnosis,
    Material,
    Plan,
    PlanStep,
    ProductSlot,
    Recommendation,
    Severity,
)

# Safety-critical domains that must always route to a licensed professional.
SAFETY_KEYWORDS = (
    "electrical", "wiring", "outlet", "breaker", "gas", "structural",
    "load-bearing", "roof", "roofing", "chimney", "foundation",
)

DIAGNOSE_PROMPT = """You are ARCHOICE's diagnosis engine for home-improvement problems.
Look at the image and the user's note. Identify the object, what is wrong, and how serious it is.

Return ONLY a JSON object with these keys:
  object_name (string), problem (string),
  severity (one of: none, minor, moderate, severe),
  confidence (number 0..1),
  requires_pro (boolean: true if this is electrical/gas/structural/roofing work,
                or if your confidence is below 0.6),
  reasoning (one short sentence).
Be conservative: if unsure or if there is any safety risk, set requires_pro=true."""

PLAN_PROMPT = """You are ARCHOICE's planning engine. Given a diagnosed home-improvement
problem, produce a safe DIY plan. Return ONLY a JSON object with keys:
  title (string),
  steps (array of {order:int, instruction:string}),
  tools (array of strings),
  materials (array of {name:string, quantity:string}),
  est_minutes (int), est_cost_usd (number),
  difficulty (int 1..5).
Keep it conservative and safe. Never recommend unsafe shortcuts."""


def _model() -> str:
    return os.environ.get("ARCHOICE_MODEL", "claude-haiku-4-5-20251001")


def _has_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


# --------------------------------------------------------------------------- #
# Real Claude-backed path
# --------------------------------------------------------------------------- #
def _claude_diagnose(image_b64: str | None, media_type: str, note: str) -> Diagnosis:
    import anthropic  # imported lazily so the stub path needs no dependency

    client = anthropic.Anthropic()
    content: list[dict] = []
    if image_b64:
        content.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": image_b64},
            }
        )
    content.append({"type": "text", "text": f"{DIAGNOSE_PROMPT}\n\nUser note: {note or '(none)'}"})

    msg = client.messages.create(
        model=_model(),
        max_tokens=512,
        messages=[{"role": "user", "content": content}],
    )
    data = json.loads(_text(msg))
    diag = Diagnosis(**data)
    # Hard safety override: regardless of model output, force pro routing on safety keywords.
    if _is_safety_critical(f"{diag.object_name} {diag.problem}"):
        diag.requires_pro = True
    return diag


def _claude_plan(diag: Diagnosis) -> Plan:
    import anthropic

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=_model(),
        max_tokens=900,
        messages=[
            {
                "role": "user",
                "content": f"{PLAN_PROMPT}\n\nDiagnosis: {diag.model_dump_json()}",
            }
        ],
    )
    return Plan(**json.loads(_text(msg)))


def _text(msg) -> str:
    """Pull the first text block out of a Claude response, tolerating markdown fences."""
    raw = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text").strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


# --------------------------------------------------------------------------- #
# Offline stub path (no key, no hardware) — clearly labeled
# --------------------------------------------------------------------------- #
def _is_safety_critical(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in SAFETY_KEYWORDS)


def _stub_diagnose(note: str) -> Diagnosis:
    note = (note or "").lower()
    if _is_safety_critical(note):
        return Diagnosis(
            object_name="possible electrical/structural element",
            problem="Detected a safety-critical keyword in the note",
            severity=Severity.severe,
            confidence=0.55,
            requires_pro=True,
            reasoning="Safety-critical domain — routed to a licensed pro by policy.",
        )
    return Diagnosis(
        object_name="bathtub-wall caulk line",
        problem="Failed, cracked sealant joint allowing water ingress",
        severity=Severity.moderate,
        confidence=0.94,
        requires_pro=False,
        reasoning="Visible cracking and gaps along a wet joint; DIY-feasible recaulk.",
    )


def _stub_plan(diag: Diagnosis) -> Plan:
    return Plan(
        title="Recaulk the joint",
        steps=[
            PlanStep(order=1, instruction="Cut and remove the old caulk with a removal tool."),
            PlanStep(order=2, instruction="Clean and dry the joint; wipe with rubbing alcohol."),
            PlanStep(order=3, instruction="Tape both edges for a clean line."),
            PlanStep(order=4, instruction="Apply a continuous bead of mildew-resistant silicone."),
            PlanStep(order=5, instruction="Tool the bead, pull tape, cure 24h before water exposure."),
        ],
        tools=["Caulk removal tool", "Caulk gun", "Finishing tool"],
        materials=[
            Material(name="Mildew-resistant silicone sealant", quantity="1 tube"),
            Material(name="Painter's tape", quantity="1 roll"),
            Material(name="Rubbing alcohol", quantity="small bottle"),
        ],
        est_minutes=45,
        est_cost_usd=31.0,
        difficulty=2,
    )


def _recommendations(diag: Diagnosis) -> list[Recommendation]:
    """Recommendation slots per advertising-spec.md: best_fit + optional sponsored + budget.
    Sponsored is suppressed for pro-handoff flows (no ads in safety-critical paths)."""
    if diag.requires_pro:
        return []
    return [
        Recommendation(
            need="sealant",
            slots=[
                ProductSlot(
                    slot="best_fit", name="Mildew-Shield Silicone, Clear", price_usd=8.97,
                    why="Ranked on fit only — mildew-rated, matches the measured joint.",
                ),
                ProductSlot(
                    slot="sponsored", name="BrandX Pro Kitchen & Bath", price_usd=11.48,
                    why="Paid placement — still passes the fit + safety floor.", sponsored=True,
                ),
                ProductSlot(
                    slot="budget", name="Value Tub & Tile Sealant", price_usd=5.24,
                    why="Lowest viable-quality option — never paid.",
                ),
            ],
        )
    ]


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def run_diagnose(image_b64: str | None, media_type: str, note: str) -> tuple[Diagnosis, bool]:
    if _has_key():
        return _claude_diagnose(image_b64, media_type, note), False
    return _stub_diagnose(note), True


def run_plan(diag: Diagnosis) -> tuple[Plan, list[Recommendation], bool]:
    if diag.requires_pro:
        # No DIY plan for safety-critical problems — caller surfaces the pro handoff.
        empty = Plan(
            title="Consult a licensed professional",
            steps=[PlanStep(order=1, instruction="This problem should be handled by a licensed pro.")],
            tools=[], materials=[], est_minutes=0, est_cost_usd=0.0, difficulty=5,
        )
        return empty, [], not _has_key()
    if _has_key():
        return _claude_plan(diag), _recommendations(diag), False
    return _stub_plan(diag), _recommendations(diag), True
