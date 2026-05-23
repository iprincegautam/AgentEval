"""AgentEval FastAPI backend."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from evaluator import evaluate_repo

load_dotenv()
load_dotenv("../.env")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not set — /evaluate will fail at runtime")
    yield


app = FastAPI(
    title="AgentEval API",
    description="GitAgent quality evaluator — multi-agent eval pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluateRequest(BaseModel):
    repo_url: str = Field(..., examples=["https://github.com/open-gitagent/gitagent"])


class EvaluateResponse(BaseModel):
    repo_url: str
    overall_status: str
    overall_score: float | None = None
    report: dict


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agenteval"}


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(body: EvaluateRequest):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not configured")

    report = await evaluate_repo(body.repo_url)
    return EvaluateResponse(
        repo_url=body.repo_url,
        overall_status=report.get("overall_status", "fail"),
        overall_score=report.get("overall_score"),
        report=report,
    )
