# AgentEval ↯

> The missing quality layer for GitAgent — paste any GitAgent repo, get a structured pass/fail eval report in seconds.

**Live app:** [agenteval-rho.vercel.app](https://agenteval-rho.vercel.app) · **API:** [agenteval-api.vercel.app](https://agenteval-api.vercel.app)

---

## What it does

GitAgent's `gapman validate` checks structure. AgentEval checks **quality**.

Three specialized agents run in parallel:

- **Rules Agent** — is RULES.md specific, non-contradictory, safe?
- **Probe Agent** — generates adversarial prompts that would break this agent
- **Identity Agent** — is SOUL.md specific enough to be implemented consistently?

An orchestrator synthesizes all three into a scored report (0–100, A–F grade) with failure taxonomy.

**Pitch for judges:** *"`gapman` checks structure; AgentEval checks whether the agent would survive real users and attackers."*

---

## Getting started

Pick the path that matches you — no need to understand everything on day one.

### Path A — Try it now (no install)

Best for judges, demos, and first-time users.

1. Open **[agenteval-rho.vercel.app](https://agenteval-rho.vercel.app)**
2. Paste a GitHub URL that contains GitAgent files (`agent.yaml` + `SOUL.md`), for example:
   - `https://github.com/open-gitagent/gitagent`
   - `https://github.com/iprincegautam/AgentEval` (this repo — self-eval)
3. Click **Run Eval →**
4. Read the grade, per-agent scores, failure taxonomy, and adversarial probes.

### Path B — Run locally (development)

Best for hacking on the UI, agents, or prompts.

**You need (one-time):**

| Tool | What it is | Why AgentEval uses it |
|------|------------|------------------------|
| [Node.js](https://nodejs.org) | Runs JavaScript outside the browser | Powers the Next.js UI |
| **npm** | Node's package manager — installs libraries like React and Next | `npm install` in `frontend/` |
| Python 3.11+ | Runs the backend | FastAPI + eval pipeline |
| **pip** | Python's package manager | `pip install -r requirements.txt` |
| An LLM API key | OpenAI, OpenRouter, or Anthropic | Powers the four eval agents |

**Architecture:**

```text
Browser (:3000)  →  Next.js frontend  →  FastAPI (:8000)  →  LLM APIs
```

**Terminal 1 — backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # add OPENAI_API_KEY=sk-... (or OpenRouter, etc.)
uvicorn main:app --reload --port 8000
```

**Terminal 2 — frontend**

```bash
cd frontend
npm install                        # downloads dependencies (Next.js, React, …)
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                        # starts UI at http://localhost:3000
```

Open **[http://localhost:3000](http://localhost:3000)** — not port 8000 (that's the API).

### Path C — API / automation (agentic workflows)

Best for CI, scripts, or another agent calling AgentEval as a quality gate.

```bash
curl -X POST https://agenteval-api.vercel.app/evaluate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/iprincegautam/AgentEval"}'
```

Response fields include `final_report.grade`, `rules_eval`, `probe_eval`, `identity_eval`, and `failure_taxonomy`.

### Path D — Build your own GitAgent, then eval it

Best for the GitAgent challenge — dogfood the standard.

1. In your repo, add at minimum:
   - `agent.yaml` — name, version, description
   - `SOUL.md` — who the agent is (one paragraph minimum)
   - `RULES.md` — must-always / must-never (strongly recommended)
2. Push to GitHub.
3. Run AgentEval on your repo URL.
4. Fix `top_3_issues` from the report; re-run until score/grade improve.

This repository includes its own GitAgent bundle at the root — see below.

---

## Glossary (quick)

| Term | Meaning |
|------|---------|
| **GitAgent** | Open standard: agent = files in a repo (`agent.yaml`, `SOUL.md`, `RULES.md`) |
| **npm** | Installs JavaScript deps; run `npm install` once, then `npm run dev` |
| **pip** | Installs Python deps for the backend |
| **uvicorn** | Serves the FastAPI app |
| **`.env`** | Local secrets (API keys) — never commit |
| **Multi-agent pipeline** | Rules + Probe + Identity run in parallel; orchestrator merges results |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|--------|-----|
| `localhost:3000` connection refused | Frontend not running | `cd frontend && npm run dev` |
| 503 / no API key | Missing LLM key in `backend/.env` | Set `OPENAI_API_KEY` in `backend/.env`, restart uvicorn |
| `No agent.yaml found` | Repo isn't GitAgent-shaped | Add required files or use another URL |
| Browser on `:8000` shows JSON | That's the API, not the UI | Use `:3000` or the live Vercel app |
| Demo banner in UI | No key on server; demo mode on | Add keys to production env (Vercel project settings) |

---

## GitAgent definition (this repo)

First-class GitAgent bundle at the repository root:

- [`agent.yaml`](./agent.yaml) — manifest
- [`SOUL.md`](./SOUL.md) — identity
- [`RULES.md`](./RULES.md) — constraints

Self-eval:

```bash
curl -X POST https://agenteval-api.vercel.app/evaluate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/iprincegautam/AgentEval"}'
```

---

## Stack

- **Next.js 14** (TypeScript) — frontend
- **FastAPI** (Python) — backend
- **OpenAI / OpenRouter / Anthropic** (auto-fallback) — eval agents
- **GitAgent** — the standard being evaluated

---

## Deploy (production)

Currently hosted on **Vercel** (two projects):

| Piece | Vercel project | Root dir | Key env var |
|-------|----------------|----------|-------------|
| Frontend | `agenteval` | `frontend/` | `NEXT_PUBLIC_API_URL` → API URL |
| API | `agenteval-api` | `backend/` | `OPENAI_API_KEY` (or other LLM keys) |

**Alternative — Railway (backend) + Vercel (frontend):**

1. Railway → import repo → root **`backend`** → set `OPENAI_API_KEY` → deploy.
2. Vercel → import repo → root **`frontend`** → `NEXT_PUBLIC_API_URL=<railway-url>`.
3. Set `CORS_ORIGINS` on the backend to your Vercel domain.

See [`render.yaml`](./render.yaml) for a Render.com option.

---

## Project layout

```text
agenteval/
├── agent.yaml          # This project's GitAgent manifest
├── SOUL.md
├── RULES.md
├── backend/            # FastAPI + eval agents
├── frontend/           # Next.js UI
└── README.md
```

---

## Built for

Lyzr Builder Challenge — GitAgent Hiring Challenge (May 2026)

Built by [Prince Gautam](https://github.com/iprincegautam)
