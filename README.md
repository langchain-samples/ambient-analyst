# Ambient Analyst

Ambient Analyst is a macroeconomic and business analyst built on the
[LangChain **DeepAgents**](https://docs.langchain.com/oss/python/deepagents/overview)
framework and packaged as a
[LangGraph application](https://docs.langchain.com/oss/python/langgraph/application-structure)
(`langgraph.json`) so it runs in LangGraph Studio and deploys on LangSmith.

Ask it things like:

- "What macro forces will shape enterprise software spending this year?"
- "Compare the growth drivers and risks for these three companies."
- "How could rates, inflation, and regulation change this industry's outlook?"
- "Which LLM is best for this workload, and can I trust the benchmarks?"

It produces **sourced, dated** analysis, separates evidence from inference,
tests scenarios and counterarguments, and states confidence and decision
implications. LLM research and model evaluation remain a specialist capability.

## How it works

- **Tools** — `tavily_search` for current web research and `tavily_extract` for
  source extraction, both from `langchain-tavily` and configurable per assistant.
- **Skills** — specialist LLM research playbooks loaded on demand via progressive
  disclosure, each stored as its own **LangSmith Context Hub skill repo**
  (`pull_skill`), pulled at startup:
  - `ambient-analyst-model-evaluation` — how to research and compare current models.
  - `ambient-analyst-benchmark-analysis` — the major benchmarks and how to judge their validity
    (contamination, saturation, self-reported vs independent, construct validity).
  - `ambient-analyst-landscape-mapping` — the major labs/model families and tracking releases.
  - `ambient-analyst-scorecard-maintenance` — the scorecard schema and how to update it safely.
  - `ambient-analyst-continuous-learning` — what to capture after each task so the agent improves.
- **Long-term memory** — `AGENTS.md` (standing context + learnings) and
  `scorecard.md` (ranked best-models-per-category, with scores, sources, dates,
  and caveats), in the Context Hub agent repo `ambient-analyst-memory`. Loaded into
  context every run.
- **Hot-path memory** — `hot_path_record_memory` appends cheap, auditable events
  to `/memory/hot-path-events.jsonl` during the current run: explicit user
  preferences, detector hits, evidence links, and other high-confidence facts.
- **Cold-path memory** — `memory-consolidator` reviews repeated hot-path events
  later and promotes durable patterns into `/memory/cold-path-memory.md` rather
  than rewriting broad memory summaries on every request.
- **System prompt** — pulled from the **LangSmith Prompt Hub** prompt
  `ambient-analyst-prompt` at startup (its system message), not hard-coded.
- **Continuous learning** — the agent updates memory and the scorecard with its
  own `write_file`/`edit_file` tools, which commit straight back to the Context
  Hub. Knowledge compounds across sessions instead of restarting each time.
- **Bounded research** — the prompt sets a search budget and stopping criteria,
  and a `StepBudgetMiddleware` forces a clean, tool-free final answer once the
  model-turn budget is nearly spent. A `recursion_limit` (`agent.py`) is the hard
  backstop. Together these prevent the agent from looping on hard-to-verify,
  fast-moving figures — the user always gets a finished, caveated answer rather
  than a `GraphRecursionError`.

### Architecture: state lives in LangSmith

This repo holds **only the agent code** — skills, memory, and the system prompt
all live in LangSmith (the single source of truth), so there are no local copies
to drift out of date. At construction the agent pulls the **Prompt Hub** prompt
`ambient-analyst-prompt` (system message) and each **skill repo** (`pull_skill`),
staging the skills locally so a `CompositeBackend` can serve them:

```
/skills/   -> FilesystemBackend(temp dir, virtual_mode=True)  # skill repos pulled at startup (progressive disclosure)
/memory/   -> ContextHubBackend("ambient-analyst-memory")     # AGENTS.md, scorecard, hot/cold memory files
/analysis/ -> LangSmithSandbox                                # datasets, calculations, charts, artifacts
everything else -> StateBackend()                             # ephemeral scratch (todos, working notes)
```

Skills and the prompt are pulled at startup (curated, stable — edit them in
LangSmith and restart/redeploy). Memory is the evolving state, written back to the
Context Hub at runtime. The key must be **scoped to the workspace** these repos
live in (then it resolves its own tenant — no `LANGSMITH_WORKSPACE_ID` needed).

## Deep agent capabilities

The agent exercises the full DeepAgents toolkit — these are what
the [frontend visualizer](#frontend-capability-visualizer) is built to show off:

- **Context-engineered memory paths** — short-term scratch lives in graph state,
  durable memory lives under `/memory/`, cheap events are captured on the hot
  path, and repeated patterns are consolidated on the cold path by a narrow
  subagent.
- **Interpreters as context compressors** — `run_context_interpreter` uses code to
  count and summarize event JSON before the LLM judges what should become memory.
  `CodeInterpreterMiddleware` remains available for workflow-style fan-out and
  analysis code.
- **Dynamic subagents** — with `CodeInterpreterMiddleware` (`langchain-quickjs`),
  phrasing a request as a **"workflow"** lets the agent dispatch subagents from
  interpreter code (loops, parallel fan-out) rather than one tool call at a time.
  `macro-analysis-worker` can analyze sources, companies, industries, countries,
  indicators, or scenarios in parallel. `memory-consolidator` handles cold-path
  memory reflection in an isolated context.
- **Middleware** — a custom stack (PII redaction, a recursion floor, and a step
  budget that forces a clean final answer near the turn limit) plus the built-in
  planning (todos) and code-interpreter middleware.
- **Sandbox** — a LangSmith managed sandbox mounted at `/analysis/` (via
  `CompositeBackend`) for calculations, datasets, charts, and artifacts.

Dynamic subagents are enabled on the served graph (`make_agent`).

## Project layout

```
ambient-analyst/
├── ambient_analyst/
│   ├── agent.py              # deep agent: subagents, sandbox, middleware; pulls the prompt from the Hub
│   ├── simple_agent.py       # a plain ReAct comparison graph
│   └── utils/
│       ├── assistants.py     # prompt + Tavily tool registry for assistant configs
│       ├── pii.py            # PII redaction middleware
│       └── budget.py         # recursion-floor + step-budget middleware
├── frontend/                 # Next.js capability visualizer (see below)
├── langgraph.json
├── pyproject.toml
└── .env.example
```

The Context Hub repos (skills, memory, prompt) are created/maintained in the Hub,
not from this repo. See **Editing content** below.

## 1. Install

```bash
uv sync
```

## 2. Configure keys

```bash
cp .env.example .env   # then fill in your keys
```

You need `TAVILY_API_KEY`, `LC_GATEWAY_KEY` and `LANGSMITH_API_KEY`. Leaving
`LANGSMITH_TRACING=true` sends traces to LangSmith. **Use a `LANGSMITH_API_KEY`
scoped to the workspace** that holds the prompt/skill/memory repos — it then
resolves its own tenant and needs no `LANGSMITH_WORKSPACE_ID`. (An
org/multi-workspace key resolves no tenant and 404s on the repos; set
`LANGSMITH_WORKSPACE_ID` for those.) Resource names are overridable via
`AMBIENT_ANALYST_PROMPT_NAME`, `AMBIENT_ANALYST_MEMORY_REPO`, and `AMBIENT_ANALYST_SKILLS`.

## 3. Run

```bash
uv run langgraph dev
```

This serves the `ambient-analyst` graph from `langgraph.json` in LangGraph
Studio. The system prompt, skills, and memory are read directly from LangSmith —
no per-invocation seeding needed.

## Frontend: capability visualizer

`frontend/` is a Next.js app that connects to the agent server and makes the
[capabilities above](#deep-agent-capabilities) visible — one panel each: a chat
with live tool calls, a **Plan** panel (todos), live **Subagent** cards, an
**Artifacts** panel (files the agent and sandbox produce), a **Middleware**
panel. Capability chips in
the header light up as each feature activates. Built on
[`@langchain/react`](https://docs.langchain.com/oss/python/deepagents/frontend/overview)'s
`useStream`.

The browser talks to the agent server through a same-origin proxy
(`app/api/lg`) that injects the LangSmith key server-side, so the key never
reaches the browser.

```bash
# 1. Start the agent server (from the repo root)
uv run langgraph dev                 # http://127.0.0.1:2024

# 2. Start the UI (in a second terminal)
cd frontend
cp .env.example .env.local           # local default proxies to :2024, no key needed
pnpm install
pnpm dev                             # http://localhost:3000
```

Demo prompts are one-click buttons (**Macro outlook**, **Run a workflow**,
**Analyze data**); Tavily tool calls show up in the live tool-call UI.

To point at the **LangSmith deployment** instead of the local server, set in
`frontend/.env.local`:

```bash
LANGGRAPH_DEPLOYMENT_URL=https://<your-deployment>.us.langgraph.app
LANGSMITH_API_KEY=lsv2_...
```

The UI deploys **separately** from the agent server (e.g. Vercel, root directory
`frontend`, pointed at the deployment URL) — a LangSmith Deployment hosts the
agent, not the frontend.

## Editing content

All of the agent's editable content lives in LangSmith (the source of truth —
there are no local copies in this repo):

- **System prompt** — Prompt Hub prompt `ambient-analyst-prompt` (its system
  message): edit in the LangSmith UI; pulled fresh each time the graph is built.
- **Skills** — one Context Hub **skill repo** per skill (`ambient-analyst-model-evaluation`,
  `ambient-analyst-benchmark-analysis`, `ambient-analyst-landscape-mapping`, `ambient-analyst-scorecard-maintenance`,
  `ambient-analyst-continuous-learning`), each with a `SKILL.md`: edit in the UI to refine a
  playbook; pulled at startup.
- **Memory + scorecard** — Context Hub agent repo `ambient-analyst-memory`
  (`AGENTS.md` + `scorecard.md`): primarily owned by the agent — it writes back
  as it learns. Editable in the UI to correct or reset.

> Note: because content lives in LangSmith, it isn't version-controlled in git.
> Use each repo's own commit history (each write is a commit) to track/revert.
