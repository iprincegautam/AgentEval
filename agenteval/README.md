# AgentEval — GitAgent Quality Evaluator

**One line:** Give it any GitAgent repo URL → it parses `agent.yaml`, `SOUL.md`, `RULES.md` → runs 3 specialized agents against the definition → returns a structured pass/fail eval report with a failure taxonomy.

You're not just using GitAgent — you're **evaluating** GitAgent agents. Meta quality infrastructure for agent definitions.

## Architecture

```
Next.js UI  →  POST /evaluate  →  FastAPI
                                      ↓
                              gitagent_parser (GitHub)
                                      ↓
                    ┌─────────────────────────────────┐
                    │  Orchestrator                    │
                    │    ├── Rules Agent (RULES.md)    │
                    │    ├── Identity Agent (SOUL.md)  │
                    │    └── Probe Agent (adversarial) │
                    └─────────────────────────────────┘
                                      ↓
                         Eval report JSON → UI
```

All eval agents call **Claude** (`claude-sonnet-4` by default).

## Quick start

### 1. Environment

```bash
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY (required) and GITHUB_TOKEN (recommended)
```

Load env for the backend (from `agenteval/`):

```bash
export $(grep -v '^#' .env | xargs)
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000), paste a GitHub URL with a GitAgent layout (e.g. `https://github.com/open-gitagent/gitagent`), and run evaluation.

## API

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/open-gitagent/gitagent"}'
```

Response includes `overall_status`, `overall_score`, per-check results (`rules`, `identity`, `probes`), and `failure_taxonomy` codes such as `RULES_VIOLATION`, `IDENTITY_DRIFT`, `PROBE_FAILURE`, `SCHEMA_INVALID`, `MISSING_REQUIRED_FILE`.

## Failure taxonomy

| Code | Meaning |
|------|---------|
| `RULES_VIOLATION` | Weak, missing, or untestable constraints |
| `IDENTITY_DRIFT` | Vague or contradictory SOUL.md |
| `PROBE_FAILURE` | Adversarial prompt likely bypasses definition |
| `INCONSISTENCY` | Mismatch between yaml / soul / rules |
| `SCHEMA_INVALID` | Invalid or incomplete agent.yaml |
| `MISSING_REQUIRED_FILE` | Required GitAgent file not found |

## Project layout

```
agenteval/
├── backend/          # FastAPI + multi-agent pipeline
├── frontend/         # Next.js UI + /api/evaluate proxy
├── .env.example
└── README.md
```

## License

MIT
