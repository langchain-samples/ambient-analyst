# ambient-analyst-managed

A Managed Deep Agent built with [`managed-deepagents`](https://github.com/langchain-ai/managed-deepagents-sdk).

## Project structure

```text
ambient-analyst-managed/
  agent.py             # define_deep_agent(...) — required `name` is the deploy id
  instructions.md      # always-loaded system prompt
  pyproject.toml       # project dependencies
  .env                 # API keys (LangSmith only); never commit
  identity.py          # managed authentication and private per-user state
  memory.py            # durable memory (`agent` scope)
  sandbox/__init__.py  # managed LangSmith sandbox (delete `sandbox/` to opt out)
  tools/               # optional custom tools
  middleware/          # optional middleware
  skills/              # optional skills synced to Context Hub
  connectors/          # optional MCP server declaration
```

## Install

```bash
uv sync
```

## Evaluate

Managed Deep Agent evals are Harbor evals. Author full Harbor tasks directly under
`evals/tasks/<task>/`. To start from a minimal task, run:

```bash
mda evals init my-task
```

This creates the optional scaffold `evals/scaffold/my-task/` with an `instruction.md` and a language
verifier. Run the same command with another name to add more scaffolds. At compile
time MDA copies selected scaffolds to `evals/tasks/` and preserves
every other task. Compile the managed agent, then run Harbor yourself:

```bash
mda evals compile ./ambient-analyst-managed                  # all tasks
mda evals compile ./ambient-analyst-managed --task my-task   # only my-task
# follow the printed `harbor run` command
```

## Develop

Edit `agent.py` to configure your model, tools, and middleware, and edit
`instructions.md` to shape the system prompt.

Run the compiled app on the local LangGraph dev server:

```bash
mda dev .
```

For Python projects, `mda dev` requires `uv` on `PATH`, but it resolves the local LangGraph dev server automatically; you do not need to install a global `langgraph` command.

## Model

`agent.py` runs on [LangSmith Gateway](https://docs.langchain.com/langsmith/gateway),
billed to your workspace's Gateway Credits, so the agent needs no model
provider key of its own. It authenticates with a LangSmith API key read from
`LANGSMITH_GATEWAY_API_KEY` — `LANGSMITH_API_KEY` is reserved by the platform
and never reaches a deployment, so the key is set under both names in `.env`.

Only the models LangSmith hosts are covered by credits. Naming a
`<provider>/<model>` route instead bills that provider against your
workspace's own secret for it.

## Identity

`identity.py` enables managed authentication: threads and downstream
credentials are per-caller. Set `auth` to one or more `auth.*` entries if
browsers call the deployment directly. Durable memory is declared
separately.

## Memory

`memory.py` mounts one deployment-shared memory tree at
`/memories/agent/` (read/write). `/memories/agent/AGENTS.md` is hot memory,
loaded into every run; other files under that path are read on demand. The
content lives in Context Hub, so deploys never overwrite what earlier runs
learned. Every caller shares it — keep procedural knowledge there, never
per-person facts or credentials.

The memory file holds only what the agent wrote. How to use memory — the
paths, which tools reach them, that the tree is shared — is stated in the
system prompt at runtime whenever a slice is mounted, so there is nothing to
maintain in the file and nothing to repeat in `instructions.md`.

## Sandbox

`sandbox/__init__.py` declares a managed LangSmith sandbox. MDA only enables the
sandbox when this declaration is present — remove the `sandbox/` directory to
opt out (for example for chat-only agents). If `sandbox/setup.sh` exists, MDA
embeds it and runs it once when the sandbox is first provisioned.

## Optional Runtime Pieces

Add `connectors/mcp.py` to attach MCP servers. The file must export a named
`connector` declaration.

## Deploy

Compile and deploy the project to LangSmith:

```bash
mda deploy .
```

This copies your files verbatim, generates a managed entry module, and writes a
deployable build (including `langgraph.json`) to `.mda/build`. The CLI uploads
that build to LangSmith to run your agent on the managed runtime.

Common options:

```bash
mda deploy . --name ambient-analyst-managed-dev --deployment-type dev
mda deploy . --workspace-id "$LANGSMITH_WORKSPACE_ID"
mda deploy . --no-wait
```

Deploy prints both the Agent Server URL to call and the LangSmith dashboard URL
to inspect.

## Logs

Read the deployed agent's server logs:

```bash
mda logs .
mda logs . --lines 200 --level error
```

In a terminal this streams new output until you press Ctrl-C. When the output is
piped or redirected it prints the most recent lines (1000 by default) and exits.

## Delete

Remove the deployment and the LangSmith resources it created:

```bash
mda delete .
```

This deletes the deployment, the tracing project created alongside it, the
Context Hub repo holding this agent's context and memory, and the managed
sandboxes this agent created. It asks first; pass `--yes` to skip the prompt.
Agent memory and thread history are not recoverable afterwards.

## Environment

`mda deploy` loads `.env`, uses `LANGSMITH_API_KEY` for LangSmith, and forwards
model provider keys such as `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` as deployment
secrets. Set `LANGSMITH_WORKSPACE_ID` or pass `--workspace-id` if your LangSmith
API key requires a workspace selection.
