"""RULES.md compliance checker."""

from __future__ import annotations

from .llm import call_agent

SYSTEM = """You are the Rules Agent in AgentEval, a GitAgent quality evaluator.

Analyze RULES.md against SOUL.md for clarity, completeness, and testability.

Respond ONLY with valid JSON:
{
  "score": 0-100,
  "passed": true|false,
  "summary": "one paragraph",
  "issues": ["specific issue strings"],
  "strengths": ["specific strength strings"]
}"""


def run_rules_agent(rules: str, soul: str) -> dict:
    rules_section = rules.strip() or "(RULES.md not present)"
    user = f"""## SOUL.md
{soul[:8000]}

## RULES.md
{rules_section[:8000]}
"""
    return call_agent(SYSTEM, user)
