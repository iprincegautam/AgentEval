"""SOUL.md identity drift and coherence checker."""

from __future__ import annotations

from typing import Any

from gitagent_parser import GitAgentDefinition

from .llm import call_agent

SYSTEM = """You are the Identity Agent in AgentEval, a GitAgent quality evaluator.

Your job: evaluate SOUL.md for identity coherence, specificity, and alignment with agent.yaml.

Check:
- Non-empty identity with clear role (minimal GitAgent spec: one paragraph minimum)
- Communication style and values are consistent, not contradictory
- SOUL.md aligns with agent name/description in agent.yaml
- No identity drift signals (generic boilerplate, conflicting personas, "you are a helpful assistant" only)
- Domain expertise claims match agent purpose

Respond ONLY with valid JSON:
{
  "status": "pass" | "fail" | "warn",
  "score": 0-100,
  "findings": [{"severity": "critical"|"high"|"medium"|"low", "message": "...", "taxonomy": "IDENTITY_DRIFT"|"INCONSISTENCY"|"SCHEMA_INVALID"}],
  "summary": "one paragraph"
}"""


def evaluate_identity(defn: GitAgentDefinition) -> dict[str, Any]:
    user = f"""Repository: {defn.owner}/{defn.repo}
Agent: {defn.agent_yaml.get("name", "unknown")} v{defn.agent_yaml.get("version", "?")}

## agent.yaml
```yaml
{defn.raw_agent_yaml}
```

## SOUL.md
{defn.soul_md[:12000]}
"""
    return call_agent(SYSTEM, user)
