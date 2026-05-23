"""AgentEval FastAPI backend."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.llm import get_active_provider, has_llm_provider
from demo import run_eval_demo
from evaluator import run_eval
from gitagent_parser import GitAgentParseError

_BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(_BACKEND_DIR / ".env")
load_dotenv(_BACKEND_DIR.parent / ".env")


def _demo_mode_enabled() -> bool:
    return os.environ.get("DEMO_MODE", "true").lower() in ("1", "true", "yes")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if has_llm_provider():
        print("AgentEval: LLM provider(s) configured — live eval enabled")
    elif _demo_mode_enabled():
        print("AgentEval: no LLM keys — DEMO_MODE mock eval enabled")
    else:
        print("Warning: no LLM keys — set DEMO_MODE=true or add keys to backend/.env")
    yield


app = FastAPI(
    title="AgentEval API",
    description="GitAgent quality evaluator — multi-agent eval pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

def _cors_origins() -> list[str]:
    defaults = [
        "http://localhost:3000",
        "https://agenteval.vercel.app",
    ]
    extra = os.environ.get("CORS_ORIGINS", "")
    if extra:
        return [o.strip() for o in extra.split(",") if o.strip()]
    return defaults


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluateRequest(BaseModel):
    repo_url: str = Field(..., examples=["https://github.com/open-gitagent/gitagent"])


@app.get("/")
async def root():
    return {
        "service": "agenteval",
        "docs": "/docs",
        "llm_configured": has_llm_provider(),
        "demo_mode": _demo_mode_enabled() and not has_llm_provider(),
        "endpoints": {
            "GET /health": "Health check",
            "POST /evaluate": 'Body: {"repo_url": "https://github.com/owner/repo"}',
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "agenteval",
        "llm_configured": has_llm_provider(),
        "demo_mode": _demo_mode_enabled() and not has_llm_provider(),
    }


@app.post("/evaluate")
async def evaluate(body: EvaluateRequest):
    if not has_llm_provider():
        if _demo_mode_enabled():
            return await run_eval_demo(body.repo_url)
        raise HTTPException(
            status_code=503,
            detail="No LLM API key configured. Add keys to backend/.env or set DEMO_MODE=true.",
        )

    try:
        result = await run_eval(body.repo_url)
        result["demo"] = False
        result["llm_provider"] = get_active_provider()
        return result
    except GitAgentParseError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


# Vercel serverless entrypoint
try:
    from mangum import Mangum

    handler = Mangum(app, lifespan="off")
except ImportError:
    pass
