# AgentEval — Demo Video Script

**Target length:** 2:30–3:30  
**Tone:** Confident, technical but clear — builder talking to judges  
**Record:** Screen + voiceover (Loom, OBS, or QuickTime). Optional face cam in corner for intro/outro.

---

## Pre-recording checklist

- [ ] Backend live: [agenteval-api.vercel.app/health](https://agenteval-api.vercel.app/health) returns OK  
- [ ] Frontend live: [agenteval-rho.vercel.app](https://agenteval-rho.vercel.app) loads  
- [ ] Browser zoom ~100%, dark mode if it matches the UI  
- [ ] Close unrelated tabs; hide bookmarks bar  
- [ ] Have these URLs in a notes doc (copy-paste ready):
  - `https://github.com/open-gitagent/gitagent`
  - `https://github.com/iprincegautam/AgentEval`
- [ ] Optional: architecture diagram or GitHub README open in a second tab for B-roll

---

## SCENE 1 — Hook (0:00–0:20)

**ON SCREEN:** Black screen → fade to AgentEval homepage ([agenteval-rho.vercel.app](https://agenteval-rho.vercel.app))

**VO:**

> GitAgent tells you if your agent files are *valid*.  
> But valid isn’t the same as *good*.  
>  
> **AgentEval** is the missing quality layer — paste any GitAgent repo, and in seconds you get a scored report: pass or fail, A through F, and a failure taxonomy your team can actually act on.

**ON SCREEN:** Slow pan on title **AgentEval ↯** and subtitle *“Paste a GitAgent repo…”*

---

## SCENE 2 — The problem (0:20–0:45)

**ON SCREEN:** Split or quick cuts:
1. Generic “agent.yaml + SOUL.md + RULES.md” file icons (or GitAgent spec README)
2. A vague RULES.md example (blur if needed): “be helpful”, “be safe”

**VO:**

> The GitAgent standard is the right move — agents as code in the repo.  
> `gapman validate` checks structure: did you ship the files? Does the YAML parse?  
>  
> What it doesn’t tell you is: Will this agent refuse a jailbreak? Are your rules testable? Does SOUL.md match the manifest — or is it generic boilerplate?  
>  
> That’s a **quality** problem. And that’s what we built.

**ON SCREEN:** Text overlay (optional):  
`Structure ✓  →  Quality ?  →  AgentEval`

---

## SCENE 3 — What AgentEval does (0:45–1:10)

**ON SCREEN:** Simple architecture graphic (draw or use README mental model):

```text
Repo URL → Parse agent.yaml / SOUL.md / RULES.md
         → Rules Agent  ┐
         → Probe Agent  ├─ parallel
         → Identity Agent ┘
         → Orchestrator → Report (grade, taxonomy, probes)
```

**VO:**

> AgentEval is meta — we’re not just *using* GitAgent, we’re **evaluating** GitAgent agents.  
>  
> You paste a GitHub URL. We fetch the definition files, then run **three specialized agents in parallel**:  
> - **Rules** — are constraints specific and non-contradictory?  
> - **Probe** — what adversarial prompts would break this agent?  
> - **Identity** — is SOUL.md coherent and aligned with agent.yaml?  
>  
> An orchestrator synthesizes everything into one executive report — score, grade, top issues, strengths, and a **failure taxonomy**.

**ON SCREEN:** Highlight each agent name as you say it.

---

## SCENE 4 — Live demo #1: reference repo (1:10–2:00)

**ON SCREEN:** [agenteval-rho.vercel.app](https://agenteval-rho.vercel.app) — full width

**VO:**

> Here’s the live demo. I’ll start with the open GitAgent reference repo.

**ON SCREEN:** Paste into input:

```text
https://github.com/open-gitagent/gitagent
```

Click **Run Eval →**

**VO (while loading — skeleton visible, input pulse):**

> While it runs, we’re pulling files from GitHub and executing the three-agent pipeline. You’ll see the loading skeleton — same layout as the final report.

**ON SCREEN:** Report appears. Scroll slowly through:

1. **Header** — grade, verdict, overall score  
2. **Failure taxonomy** — counts by category  
3. **Three agent cards** — Rules, Identity, Probe (pause on Probe top risk)  
4. **Top issues / Strengths**  
5. **Files parsed** chips: `agent.yaml`, `SOUL.md`, `RULES.md`

**VO:**

> And here’s the report. Grade, verdict, executive summary.  
> Failure taxonomy — not just pass/fail, but *what kind* of failure: rules violations, identity drift, probe failures.  
>  
> The Probe agent is the differentiator — it doesn’t just lint your markdown. It asks: *what would a bad actor try*, and does your definition actually defend against it?  
>  
> For gitagent, you can see strengths around identity alignment, and specific issues where rules could be more testable.

**ON SCREEN (optional):** Click **{ } Copy JSON** — flash “Copied!” to show API-friendly output.

**VO:**

> One click — full JSON for CI or downstream tooling. RawEval-style quality infra, on top of GitAgent.

---

## SCENE 5 — Live demo #2: dogfood (2:00–2:35)

**ON SCREEN:** Clear input or new tab → same app

**VO:**

> This repo is a GitAgent too — we dogfood our own standard.

**ON SCREEN:** Paste:

```text
https://github.com/iprincegautam/AgentEval
```

Run eval → show report (grade + 1–2 callouts)

**VO:**

> AgentEval evaluating AgentEval. Same pipeline: our own `agent.yaml`, `SOUL.md`, and `RULES.md` at the repo root.  
> That’s the product story — we’re part of the ecosystem, not a side tool.

**ON SCREEN:** Quick flash of GitHub repo root showing `agent.yaml`, `SOUL.md`, `RULES.md` files.

---

## SCENE 6 — API / agentic angle (2:35–2:55)

**ON SCREEN:** Terminal with curl (pre-typed, hit Enter):

```bash
curl -X POST https://agenteval-api.vercel.app/evaluate \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/open-gitagent/gitagent"}'
```

**VO:**

> Everything you see in the UI is one POST to `/evaluate`. Drop this into CI, a judging pipeline, or another agent’s toolchain — structured JSON out, no UI required.

**ON SCREEN:** Scroll JSON briefly — `final_report.grade`, `failure_taxonomy`, `rules_eval` (don’t read every field).

---

## SCENE 7 — Stack & close (2:55–3:20)

**ON SCREEN:** README “Stack” section or simple end card:

| Layer | Tech |
|-------|------|
| UI | Next.js 14 |
| API | FastAPI |
| Agents | Multi-agent eval (Rules / Probe / Identity + Orchestrator) |
| LLM | OpenAI / OpenRouter fallback |
| Standard | GitAgent |

**VO:**

> Stack: Next.js frontend, FastAPI backend, four LLM-powered agents with provider fallback, deployed on Vercel. Open source on GitHub.  
>  
> **AgentEval** — structure checks if you’re valid; we check if you’re *ready*.  
>  
> Try it: **agenteval-rho.vercel.app**  
> Repo: **github.com/iprincegautam/AgentEval**  
>  
> Built for the Lyzr GitAgent challenge. I’m Prince Gautam — thanks for watching.

**ON SCREEN:** End card (3–5 seconds):

```text
AgentEval ↯
agenteval-rho.vercel.app
github.com/iprincegautam/AgentEval
```

---

## Optional 30-second “short cut” version

Use only Scenes 1, 4, and 7 — hook → one live eval on `open-gitagent/gitagent` → URL + thank you.

---

## Lines to avoid (judges hear these too often)

- “Revolutionary AI platform” — be specific: *quality layer for GitAgent*  
- Long Claude/API worship — one line on multi-provider is enough  
- Reading the entire report aloud — *show* taxonomy and probes, don’t narrate every bullet  

---

## Lines that land well

- “Valid isn’t the same as good.”  
- “We’re evaluating GitAgent agents — that’s meta.”  
- “`gapman` checks structure; AgentEval checks survival.”  
- “Probe agent asks what a bad actor would try.”  
- “Dogfood: this repo has its own agent.yaml.”  

---

## Recording tips

1. **Pace:** Pause 2 seconds after the report loads so viewers can read the grade.  
2. **Mouse:** Move deliberately; circle grade and Probe card with cursor.  
3. **Audio:** Record VO in a quiet room; normalize to -16 LUFS if you edit.  
4. **Export:** 1080p, 30fps; H.264 for LinkedIn/Twitter/YouTube.  
5. **Thumbnail text:** `AgentEval ↯` + `GitAgent Quality Report` + grade badge mockup.

---

## Submission caption (copy-paste)

```text
AgentEval ↯ — the quality layer for @GitAgent repos.

Paste a GitHub URL → 3 parallel eval agents (Rules, Probe, Identity) → scored report + failure taxonomy.

gapman checks structure. We check if your agent would survive real users and attackers.

🔴 Live: agenteval-rho.vercel.app
📦 github.com/iprincegautam/AgentEval

#LyzrChallenge #GitAgent #AIAgents #RawEval
```
