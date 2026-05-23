"""Fetch and parse GitAgent definition files from a GitHub repository."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
import yaml

GITHUB_API = "https://api.github.com"
REQUIRED_FILES = ("agent.yaml", "SOUL.md")
OPTIONAL_FILES = ("RULES.md",)


@dataclass
class GitAgentDefinition:
    repo_url: str
    owner: str
    repo: str
    agent_path: str
    agent_yaml: dict[str, Any]
    soul_md: str
    rules_md: str | None
    raw_agent_yaml: str


class GitAgentParseError(Exception):
    def __init__(self, message: str, taxonomy: str = "MISSING_REQUIRED_FILE"):
        super().__init__(message)
        self.taxonomy = taxonomy


def parse_github_url(repo_url: str) -> tuple[str, str]:
    url = repo_url.strip().rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}"

    parsed = urlparse(url)
    if parsed.netloc not in ("github.com", "www.github.com"):
        raise GitAgentParseError(
            "Only github.com repository URLs are supported.",
            taxonomy="INVALID_REPO_URL",
        )

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        raise GitAgentParseError(
            "URL must be https://github.com/{owner}/{repo}",
            taxonomy="INVALID_REPO_URL",
        )

    return parts[0], parts[1].removesuffix(".git")


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def _get_json(client: httpx.AsyncClient, path: str) -> Any:
    resp = await client.get(f"{GITHUB_API}{path}", headers=_github_headers())
    if resp.status_code == 404:
        raise GitAgentParseError(f"GitHub resource not found: {path}", taxonomy="REPO_NOT_FOUND")
    if resp.status_code != 200:
        raise GitAgentParseError(
            f"GitHub API error ({resp.status_code}): {resp.text[:200]}",
            taxonomy="GITHUB_API_ERROR",
        )
    return resp.json()


async def _get_file_content(client: httpx.AsyncClient, owner: str, repo: str, path: str) -> str:
    data = await _get_json(client, f"/repos/{owner}/{repo}/contents/{path}")
    if isinstance(data, list):
        raise GitAgentParseError(f"Expected file at {path}, got directory.", taxonomy="PARSE_ERROR")

    encoding = data.get("encoding")
    content = data.get("content", "")
    if encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="replace")
    return content


async def _search_agent_yaml(client: httpx.AsyncClient, owner: str, repo: str) -> str | None:
    """Find agent.yaml path via GitHub code search (falls back to common paths)."""
    query = f"filename:agent.yaml repo:{owner}/{repo}"
    resp = await client.get(
        f"{GITHUB_API}/search/code",
        params={"q": query, "per_page": 5},
        headers=_github_headers(),
    )
    if resp.status_code == 200:
        items = resp.json().get("items", [])
        if items:
            return items[0]["path"]

    for candidate in ("agent.yaml", "my-agent/agent.yaml", "agent/agent.yaml"):
        check = await client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{candidate}",
            headers=_github_headers(),
        )
        if check.status_code == 200:
            return candidate

    return None


def _agent_dir(agent_yaml_path: str) -> str:
    if "/" in agent_yaml_path:
        return agent_yaml_path.rsplit("/", 1)[0]
    return ""


def _join_path(directory: str, filename: str) -> str:
    return f"{directory}/{filename}" if directory else filename


def validate_agent_yaml(raw: str, parsed: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in ("name", "version", "description"):
        if not parsed.get(field):
            issues.append(f"agent.yaml missing required field: {field}")
    if not isinstance(parsed, dict):
        issues.append("agent.yaml must parse to a YAML object")
    if raw.strip() and not parsed:
        issues.append("agent.yaml is empty or invalid YAML")
    return issues


async def fetch_gitagent(repo_url: str) -> GitAgentDefinition:
    owner, repo = parse_github_url(repo_url)

    async with httpx.AsyncClient(timeout=60.0) as client:
        agent_yaml_path = await _search_agent_yaml(client, owner, repo)
        if not agent_yaml_path:
            raise GitAgentParseError(
                "No agent.yaml found in repository.",
                taxonomy="MISSING_REQUIRED_FILE",
            )

        agent_dir = _agent_dir(agent_yaml_path)
        raw_yaml = await _get_file_content(client, owner, repo, agent_yaml_path)

        try:
            agent_data = yaml.safe_load(raw_yaml) or {}
        except yaml.YAMLError as e:
            raise GitAgentParseError(
                f"Invalid agent.yaml: {e}",
                taxonomy="SCHEMA_INVALID",
            ) from e

        schema_issues = validate_agent_yaml(raw_yaml, agent_data)
        if schema_issues:
            raise GitAgentParseError(
                "; ".join(schema_issues),
                taxonomy="SCHEMA_INVALID",
            )

        soul_path = _join_path(agent_dir, "SOUL.md")
        try:
            soul_md = await _get_file_content(client, owner, repo, soul_path)
        except GitAgentParseError as e:
            raise GitAgentParseError(
                f"Required SOUL.md not found at {soul_path}",
                taxonomy="MISSING_REQUIRED_FILE",
            ) from e

        if not soul_md.strip():
            raise GitAgentParseError(
                "SOUL.md must contain at least one non-empty paragraph.",
                taxonomy="SCHEMA_INVALID",
            )

        rules_path = _join_path(agent_dir, "RULES.md")
        rules_md: str | None = None
        try:
            rules_md = await _get_file_content(client, owner, repo, rules_path)
        except GitAgentParseError:
            rules_md = None

        return GitAgentDefinition(
            repo_url=repo_url,
            owner=owner,
            repo=repo,
            agent_path=agent_dir or ".",
            agent_yaml=agent_data,
            soul_md=soul_md,
            rules_md=rules_md,
            raw_agent_yaml=raw_yaml,
        )


async def parse_agent_repo(repo_url: str) -> dict[str, Any]:
    """Parse repo into metadata + raw file contents for eval agents."""
    defn = await fetch_gitagent(repo_url)
    files: dict[str, str] = {
        "agent.yaml": defn.raw_agent_yaml,
        "SOUL.md": defn.soul_md,
    }
    if defn.rules_md:
        files["RULES.md"] = defn.rules_md

    return {
        "owner": defn.owner,
        "repo": defn.repo,
        "repo_url": defn.repo_url,
        "agent_path": defn.agent_path,
        "files": files,
    }
