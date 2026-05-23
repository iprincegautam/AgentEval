# AgentEval — RULES.md

## Must Always

- Parse only public GitHub repositories unless a valid `GITHUB_TOKEN` is configured.
- Require `agent.yaml` and `SOUL.md` before running any LLM eval agents.
- Return eval results in the structured JSON schema expected by the frontend (repo, files_found, rules_eval, probe_eval, identity_eval, final_report).
- Run Rules, Probe, and Identity agents in parallel when possible to minimize latency.
- Include a failure taxonomy with countable categories (RULES_VIOLATION, IDENTITY_DRIFT, PROBE_FAILURE, etc.).
- Mark responses as `demo: true` when no LLM API key is configured and demo mode is active.
- Respect CORS and only accept evaluate requests from configured origins in production.

## Must Never

- Expose API keys, tokens, or secrets in API responses, logs, or client-visible errors.
- Commit or log raw `.env` files or provider credentials.
- Claim a GitAgent repo "passes" without running all three eval agents when LLM keys are available.
- Execute arbitrary code from evaluated repositories — only fetch declared definition files via GitHub API.
- Store evaluated repository content beyond the duration of a single request.
- Provide legal, medical, or financial advice when presenting eval results — output is quality assessment only.

## Output Constraints

- `final_report.grade` must be one of: A, B, C, D, F.
- `final_report.overall_score` must be an integer 0–100.
- `failure_taxonomy` values must be non-negative integers.
- Executive summary must be under 500 words.

## Interaction Boundaries

- Input: a single `repo_url` (GitHub HTTPS URL) per evaluate request.
- Output: one eval report per request; no conversational follow-up in the API layer.
- Scope: GitAgent definition quality only — not runtime behavior of deployed agents.

## Safety & Ethics

- Probe agents must not output executable exploit code — describe attack *intent* and *target failure*, not step-by-step harm.
- Flag critical severity when definitions would allow destructive commands without confirmation.

## Regulatory Constraints

- Not applicable for default deployment; operators adding compliance domains must extend RULES.md and re-evaluate.
