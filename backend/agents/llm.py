"""Multi-provider LLM client with automatic fallback."""

from __future__ import annotations

import json
import os
import re
from typing import Callable

import httpx

MAX_TOKENS = 4096
_PLACEHOLDER_FRAGMENTS = ("your_", "_here", "sk-ant-your", "example", "placeholder")


def _valid_key(key: str | None) -> bool:
    if not key or not key.strip():
        return False
    lower = key.lower()
    return not any(p in lower for p in _PLACEHOLDER_FRAGMENTS)


def extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _chat_openai_compatible(
    *,
    url: str,
    api_key: str,
    model: str,
    system: str,
    user: str,
    extra_headers: dict[str, str] | None = None,
) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise RuntimeError(f"{model} HTTP {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _chat_anthropic(*, api_key: str, model: str, system: str, user: str) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    block = message.content[0]
    if block.type != "text":
        raise RuntimeError("Unexpected non-text response from Anthropic")
    return block.text


def _provider_chain() -> list[tuple[str, Callable[[str, str], str]]]:
    preferred = os.environ.get("LLM_PROVIDER", "auto").lower()
    chain: list[tuple[str, Callable[[str, str], str]]] = []

    def add(name: str, fn: Callable[[str, str], str]) -> None:
        if preferred == "auto" or preferred == name:
            chain.append((name, fn))

    openai_key = os.environ.get("OPENAI_API_KEY")
    if _valid_key(openai_key):
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

        def openai_fn(system: str, user: str, _k=openai_key, _m=model) -> str:
            return _chat_openai_compatible(
                url="https://api.openai.com/v1/chat/completions",
                api_key=_k,
                model=_m,
                system=system + "\n\nRespond with valid JSON only.",
                user=user,
            )

        add("openai", openai_fn)

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if _valid_key(openrouter_key):
        model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")

        def openrouter_fn(system: str, user: str, _k=openrouter_key, _m=model) -> str:
            return _chat_openai_compatible(
                url="https://openrouter.ai/api/v1/chat/completions",
                api_key=_k,
                model=_m,
                system=system + "\n\nRespond with valid JSON only.",
                user=user,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "AgentEval",
                },
            )

        add("openrouter", openrouter_fn)

    deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
    if _valid_key(deepseek_key):
        model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

        def deepseek_fn(system: str, user: str, _k=deepseek_key, _m=model) -> str:
            return _chat_openai_compatible(
                url="https://api.deepseek.com/v1/chat/completions",
                api_key=_k,
                model=_m,
                system=system + "\n\nRespond with valid JSON only.",
                user=user,
            )

        add("deepseek", deepseek_fn)

    groq_key = os.environ.get("GROQ_API_KEY")
    if _valid_key(groq_key):
        model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

        def groq_fn(system: str, user: str, _k=groq_key, _m=model) -> str:
            return _chat_openai_compatible(
                url="https://api.groq.com/openai/v1/chat/completions",
                api_key=_k,
                model=_m,
                system=system + "\n\nRespond with valid JSON only.",
                user=user,
            )

        add("groq", groq_fn)

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if _valid_key(anthropic_key):
        model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

        def anthropic_fn(system: str, user: str, _k=anthropic_key, _m=model) -> str:
            return _chat_anthropic(api_key=_k, model=_m, system=system, user=user)

        add("anthropic", anthropic_fn)

    return chain


_active_provider: str | None = None


def get_active_provider() -> str | None:
    return _active_provider


def has_llm_provider() -> bool:
    return len(_provider_chain()) > 0


def call_agent(system: str, user: str) -> dict:
    global _active_provider
    errors: list[str] = []
    chain = _provider_chain()

    if not chain:
        raise RuntimeError("No valid LLM API key configured in backend/.env")

    for name, fn in chain:
        try:
            text = fn(system, user)
            _active_provider = name
            return extract_json(text)
        except Exception as e:
            errors.append(f"{name}: {e}")

    raise RuntimeError("All LLM providers failed — " + " | ".join(errors))
