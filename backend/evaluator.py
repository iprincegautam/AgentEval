import asyncio

from agents.identity_agent import run_identity_agent
from agents.orchestrator import run_orchestrator
from agents.probe_agent import run_probe_agent
from agents.rules_agent import run_rules_agent
from gitagent_parser import parse_agent_repo


async def run_eval(repo_url: str) -> dict:
    # 1. Parse the GitAgent repo
    repo_meta = await parse_agent_repo(repo_url)
    files = repo_meta["files"]

    soul = files.get("SOUL.md", "")
    rules = files.get("RULES.md", "")
    yaml = files.get("agent.yaml", "")

    # 2. Run 3 agents in parallel
    loop = asyncio.get_event_loop()
    rules_result, probe_result, identity_result = await asyncio.gather(
        loop.run_in_executor(None, run_rules_agent, rules, soul),
        loop.run_in_executor(None, run_probe_agent, soul, rules),
        loop.run_in_executor(None, run_identity_agent, soul, yaml),
    )

    # 3. Orchestrator synthesizes
    final = run_orchestrator(rules_result, probe_result, identity_result, repo_meta)

    # 4. Return exactly the shape ReportCard expects
    return {
        "repo": f"{repo_meta['owner']}/{repo_meta['repo']}",
        "files_found": list(files.keys()),
        "rules_eval": rules_result,
        "probe_eval": probe_result,
        "identity_eval": identity_result,
        "final_report": final,
    }
