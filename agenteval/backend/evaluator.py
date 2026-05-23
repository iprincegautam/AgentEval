"""Core evaluation entrypoint."""

from __future__ import annotations

from typing import Any

from agents.orchestrator import run_evaluation
from gitagent_parser import GitAgentDefinition, GitAgentParseError, fetch_gitagent


async def evaluate_repo(repo_url: str) -> dict[str, Any]:
    try:
        definition = await fetch_gitagent(repo_url)
    except GitAgentParseError as e:
        return {
            "repo_url": repo_url,
            "overall_status": "fail",
            "overall_score": 0,
            "error": str(e),
            "failure_taxonomy": [
                {
                    "code": e.taxonomy,
                    "severity": "critical",
                    "message": str(e),
                    "source": "parser",
                }
            ],
            "checks": {},
            "summary": f"Failed to parse GitAgent repository: {e}",
        }

    return await run_evaluation(definition)
