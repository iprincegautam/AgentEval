"""SOUL.md identity drift checker."""

from __future__ import annotations

from .llm import call_agent

SYSTEM = """You are the Identity Agent in AgentEval, a GitAgent quality evaluator.

Evaluate SOUL.md identity coherence and alignment with agent.yaml.

Respond ONLY with valid JSON:
{
  "score": 0-100,
  "passed": true|false,
  "identity_clarity": "high|medium|low",
  "summary": "one paragraph",
  "issues": ["specific issue strings"],
  "strengths": ["specific strength strings"]
}"""


def run_identity_agent(soul: str, yaml: str) -> dict:
    user = f"""## agent.yaml
```yaml
{yaml[:8000]}
```

## SOUL.md
{soul[:12000]}
"""
    return call_agent(SYSTEM, user)
