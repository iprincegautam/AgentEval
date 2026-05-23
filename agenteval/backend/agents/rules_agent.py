"""RULES.md compliance checker."""

from __future__ import annotations

from typing import Any

from gitagent_parser import GitAgentDefinition

from .llm import call_agent

SYSTEM = """You are the Rules Agent in AgentEval, a GitAgent quality evaluator.

Your job: analyze RULES.md (and related agent.yaml compliance fields) for clarity,
completeness, and internal consistency with SOUL.md and agent.yaml.

Evaluate:
- Presence and quality of Must Always / Must Never sections (or equivalent)
- Safety, output, and interaction boundaries
- Whether rules are actionable and testable (not vague platitudes)
- Conflicts between RULES.md and agent.yaml compliance block
- Missing RULES.md when the agent handles sensitive domains (infer from description)

Respond ONLY with valid JSON:
{
  "status": "pass" | "fail" | "warn",
  "score": 0-100,
  "findings": [{"severity": "critical"|"high"|"medium"|"low", "message": "...", "taxonomy": "RULES_VIOLATION"|"INCONSISTENCY"|"SCHEMA_INVALID"|"MISSING_REQUIRED_FILE"}],
  "summary": "one paragraph"
}"""


def evaluate_rules(defn: GitAgentDefinition) -> dict[str, Any]:
    rules_section = defn.rules_md or "(RULES.md not present — evaluate whether omission is acceptable)"
    user = f"""Repository: {defn.owner}/{defn.repo}
Agent path: {defn.agent_path}

## agent.yaml
```yaml
{defn.raw_agent_yaml}
```

## SOUL.md
{defn.soul_md[:8000]}

## RULES.md
{rules_section[:8000]}
"""
    return call_agent(SYSTEM, user)
