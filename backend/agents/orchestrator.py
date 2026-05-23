"""Master eval agent — synthesizes sub-agent results into final report."""

from __future__ import annotations

import json
from typing import Any

from .llm import call_agent

SYSTEM = """You are the Orchestrator in AgentEval. Synthesize rules, probe, and identity eval results
into a final executive report for a GitAgent repository.

Respond ONLY with valid JSON:
{
  "overall_score": 0-100,
  "grade": "A|B|C|D|F",
  "verdict": "short pass/fail headline",
  "executive_summary": "2-3 sentences",
  "top_3_issues": ["issue 1", "issue 2", "issue 3"],
  "top_3_strengths": ["strength 1", "strength 2", "strength 3"],
  "failure_taxonomy": {
    "RULES_VIOLATION": 0,
    "IDENTITY_DRIFT": 0,
    "PROBE_FAILURE": 0,
    "INCONSISTENCY": 0,
    "SCHEMA_INVALID": 0,
    "MISSING_REQUIRED_FILE": 0
  },
  "recommendation": "one actionable next step"
}

failure_taxonomy values must be non-negative integer counts derived from the inputs."""


def _grade_from_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _fallback_final(
    rules: dict[str, Any],
    probe: dict[str, Any],
    identity: dict[str, Any],
) -> dict[str, Any]:
    scores = [
        int(rules.get("score", 0)),
        int(identity.get("score", 0)),
    ]
    overall = round(sum(scores) / len(scores)) if scores else 0
    issues = (rules.get("issues") or []) + (identity.get("issues") or [])
    strengths = (rules.get("strengths") or []) + (identity.get("strengths") or [])
    taxonomy: dict[str, int] = {
        "RULES_VIOLATION": len(rules.get("issues") or []),
        "IDENTITY_DRIFT": len(identity.get("issues") or []),
        "PROBE_FAILURE": len(
            [p for p in (probe.get("probes") or []) if p.get("severity") in ("critical", "high")]
        ),
        "INCONSISTENCY": 0,
        "SCHEMA_INVALID": 0,
        "MISSING_REQUIRED_FILE": 0,
    }
    return {
        "overall_score": overall,
        "grade": _grade_from_score(overall),
        "verdict": "Pass" if overall >= 70 else "Needs work",
        "executive_summary": rules.get("summary", "Evaluation complete."),
        "top_3_issues": issues[:3] or ["No critical issues identified."],
        "top_3_strengths": strengths[:3] or ["Definition provides a baseline identity."],
        "failure_taxonomy": taxonomy,
        "recommendation": "Review RULES.md and SOUL.md for alignment.",
    }


def run_orchestrator(
    rules_result: dict[str, Any],
    probe_result: dict[str, Any],
    identity_result: dict[str, Any],
    repo_meta: dict[str, Any],
) -> dict[str, Any]:
    user = f"""Repository: {repo_meta.get('owner')}/{repo_meta.get('repo')}
Agent path: {repo_meta.get('agent_path', '.')}
Files: {', '.join(repo_meta.get('files', {}).keys())}

## Rules eval
{json.dumps(rules_result, indent=2)[:4000]}

## Probe eval
{json.dumps(probe_result, indent=2)[:4000]}

## Identity eval
{json.dumps(identity_result, indent=2)[:4000]}
"""
    try:
        return call_agent(SYSTEM, user)
    except Exception:
        return _fallback_final(rules_result, probe_result, identity_result)
