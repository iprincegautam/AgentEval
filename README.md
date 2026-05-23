# AgentEval ↯

> The missing quality layer for GitAgent — paste any GitAgent repo, get a structured pass/fail eval report in seconds.

## What it does

GitAgent's `gapman validate` checks structure. AgentEval checks **quality**.

Three specialized agents run in parallel:

- **Rules Agent** — is RULES.md specific, non-contradictory, safe?
- **Probe Agent** — generates adversarial prompts that would break this agent
- **Identity Agent** — is SOUL.md specific enough to be implemented consistently?

An orchestrator synthesizes all three into a scored report (0–100, A–F grade) with failure taxonomy.

## GitAgent definition

This repo includes a first-class GitAgent bundle at the repository root:

- [`agent.yaml`](./agent.yaml) — manifest
- [`SOUL.md`](./SOUL.md) — identity
- [`RULES.md`](./RULES.md) — constraints

You can evaluate this repo with AgentEval itself:

```bash
curl -X POST https://agenteval-api.vercel.app/evaluate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/iprincegautam/AgentEval"}'
```

## Stack

- Next.js 14 (TypeScript) — frontend
- FastAPI (Python) — backend
- Claude / OpenAI / OpenRouter (auto-fallback) — all 4 agents
- GitAgent — the standard being evaluated

## Live demo

- **App:** [agenteval-rho.vercel.app](https://agenteval-rho.vercel.app)
- **API:** [agenteval-api.vercel.app](https://agenteval-api.vercel.app)

## Run locally

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY or ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deploy

### Backend (Railway)

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Root directory: **`/backend`**
3. Environment: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, plus optional `CORS_ORIGINS=https://your-app.vercel.app`
4. Start command (auto via `Procfile`): `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. [vercel.com](https://vercel.com) → Import repo
2. Root directory: **`/frontend`**
3. Environment: `NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app`

## API

```bash
curl -X POST https://YOUR_RAILWAY_URL/evaluate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/open-gitagent/gitagent"}'
```

## Built for

Lyzr Builder Challenge — GitAgent Hiring Challenge (May 2026)

Built by Prince Gautam
