"""Base class for all PROPWASH Claude-powered agents (Tier 3).

Agents are ADVISORY ONLY. They read/write the DB and queue.
They NEVER write flight-controller setpoints or suppress safety checks.
See CLAUDE.md §2.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List

import anthropic

_PROMPTS_DIR = Path(__file__).parent / "prompts"

logger = logging.getLogger(__name__)


class PropwashAgent:
    """Stateless Claude-powered agent base. Subclass and set `prompt_file`."""

    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    prompt_file: str  # filename inside agents/prompts/

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self._system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        path = _PROMPTS_DIR / self.prompt_file
        if not path.exists():
            raise FileNotFoundError(f"Agent prompt not found: {path}")
        return path.read_text()

    def _call(self, user_content: str, extra_system: str = "") -> str:
        system = self._system_prompt
        if extra_system:
            system = f"{system}\n\n{extra_system}"

        message = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user_content}],
        )
        return message.content[0].text

    def _call_with_tools(
        self,
        user_content: str,
        tools: List[Dict[str, Any]],
        extra_system: str = "",
    ) -> anthropic.types.Message:
        system = self._system_prompt
        if extra_system:
            system = f"{system}\n\n{extra_system}"

        return self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            tools=tools,
            messages=[{"role": "user", "content": user_content}],
        )
