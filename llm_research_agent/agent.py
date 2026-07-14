"""LLM research agent.

A research analyst for the large language model landscape, built on the
LangChain DeepAgents framework. It investigates which models lead, how the major
benchmarks work and whether they're trustworthy, and who the major labs are —
and it maintains a long-term **scorecard** of the best models that improves over
time.

Storage in LangSmith (workspace-scoped API key resolves its own tenant — no
`LANGSMITH_WORKSPACE_ID` needed):
- **System prompt**: Prompt Hub prompt `llm-research-prompt`, pulled at
  construction. Its system message is used as the agent's system prompt.
- **Skills**: separate Context Hub *skill repos* (one per skill), pulled at
  construction and staged under `/skills/<name>/SKILL.md` so the SkillsMiddleware
  discovers them with progressive disclosure.
- **Memory**: Context Hub *agent repo* `llm-research-memory` (`AGENTS.md` +
  `scorecard.md`), mounted at `/memory/` and written back at runtime — the
  continuous-learning loop.
- **Shared workspace**: a directory mounted at `/shared/` that the `coder`
  subagent also writes to, so this agent can read what the coder produced for
  simple file handoffs (best-effort mount). The agent just sees a shared
  directory; it's backed by a shared LangSmith sandbox. See the
  `shared-workspace` skill.
- A `CompositeBackend` keeps scratch files ephemeral (`StateBackend`).
"""

import logging
import os
import pathlib
import tempfile
from typing import Annotated

from deepagents import create_deep_agent, AsyncSubAgent, DeepAgentState
from deepagents.backends import StateBackend
from deepagents.backends.composite import CompositeBackend
from deepagents.backends.context_hub import ContextHubBackend
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.langsmith import LangSmithSandbox
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage
from langchain_quickjs import CodeInterpreterMiddleware
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langsmith import Client
from langsmith.sandbox import SandboxClient

from llm_research_agent.utils.assistants import DEFAULT_SYSTEM_PROMPT, assistant_settings
from llm_research_agent.utils.budget import RecursionFloorMiddleware, StepBudgetMiddleware
from llm_research_agent.utils.pii import PIIRedactionMiddleware
from llm_research_agent.utils.tools import fetch_page, web_search

import dotenv
import os

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

# LangSmith resources (override via env to target staging vs production).
MEMORY_REPO = os.environ.get("LLM_RESEARCH_MEMORY_REPO", "llm-research-memory")
# Each skill is its own Context Hub skill repo; handle == skill (and directory) name.
SKILL_HANDLES = [
    h.strip()
    for h in os.environ.get(
        "LLM_RESEARCH_SKILLS",
        "model-evaluation,benchmark-analysis,landscape-mapping,"
        "scorecard-maintenance,continuous-learning,code-generation,"
        "codegen-shared-workspace",
    ).split(",")
    if h.strip()
]

# The shared workspace at /shared/ is backed by a LangSmith sandbox the `coder`
# subagent also writes to; we attach by the same name to read those files for
# handoffs (see the `shared-workspace` skill).
SANDBOX_NAME = os.environ.get("LLM_RESEARCH_SANDBOX", "code-gen-agent-sandbox")

# Memory files loaded into context every run.
MEMORY_SOURCES = ["/memory/AGENTS.md", "/memory/scorecard.md"]

# Bounded research: hard step backstop + graceful final-answer turn budget.
RECURSION_LIMIT = 75
MAX_MODEL_TURNS = 25

client = Client()


# deepagents' DeepAgentState swaps the `messages` reducer to a DeltaChannel
# (checkpoint-size optimization). That custom channel stops LangSmith Studio from
# recognizing the graph as a chat/MessagesState graph, so it drops the prefilled
# message input and forces raw JSON entry. Restore the standard `add_messages`
# channel so Studio renders the message box like the simple agent.
# ponytail: reverts the O(N²)→O(N) checkpoint optimization on messages; fine for
# a demo, drop this subclass if checkpoint growth ever bites.
class StudioState(DeepAgentState):
    messages: Annotated[list[AnyMessage], add_messages]

# The system prompt and tool selection come from the assistant's config (see
# utils/assistants.py); `build_agent` takes them as arguments and the `make_agent`
# factory resolves them per run. Defaults reproduce the pre-configuration agent.

# Skills: deepagents has no native "mount N skill repos" backend, so we pull each
# repo's SKILL.md into a temp dir as <name>/SKILL.md and root a FilesystemBackend
# there. virtual_mode=True keeps paths relative to root_dir (required for
# CompositeBackend routing) and blocks ../absolute escapes. Skills refresh on
# restart — they're curated, stable config; the evolving state is memory.
skills_root = pathlib.Path(tempfile.mkdtemp(prefix="llm_research_skills_"))
for handle in SKILL_HANDLES:
    skill_md = skills_root / handle / "SKILL.md"
    skill_md.parent.mkdir(parents=True)
    skill_md.write_text(client.pull_skill(handle).files["SKILL.md"].content)
skills_backend = FilesystemBackend(root_dir=str(skills_root), virtual_mode=True)

# Default agent model — exported so the eval suite can record it in experiment
# metadata (single source of truth for the "what model ran" tag).
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-5.5-2026-04-23"

model = init_chat_model(
    model=DEFAULT_MODEL,
    model_provider=DEFAULT_PROVIDER,
    base_url="https://gateway.smith.langchain.com/openai",
    api_key=os.getenv('LANGSMITH_API_KEY_GATEWAY')
)

# Mount the shared workspace at /shared/, backed by the sandbox the `coder`
# subagent also writes to. Per the `shared-workspace` skill: connect by name with
# get_sandbox() (NOT the auto-deleting `client.sandbox()` context manager), start
# it if it was idled, and never delete it — the coder agent owns its lifecycle.
# Best-effort: the backing sandbox may not exist yet when this agent starts, so a
# failure just disables the /shared/ route rather than breaking the agent.
shared_routes = {}
try:
    sandbox_client = SandboxClient()
    sandbox = sandbox_client.get_sandbox(SANDBOX_NAME)
    if sandbox.status != "ready":
        sandbox = sandbox_client.start_sandbox(SANDBOX_NAME)
    shared_routes["/shared/"] = LangSmithSandbox(sandbox)
except Exception as exc:  # noqa: BLE001 — shared workspace is optional at startup
    logger.warning(
        "Shared workspace %r unavailable (%s); /shared/ route disabled.",
        SANDBOX_NAME,
        exc,
    )

# Scratch files stay ephemeral in state; /skills serves the pulled skill repos;
# /memory persists to the LangSmith Context Hub; /shared/ (when available) is
# the directory shared with the coder subagent.
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/skills/": skills_backend,
        "/memory/": ContextHubBackend(MEMORY_REPO),
        **shared_routes,
    },
)

async_subagents = [
    AsyncSubAgent(
        name="code-gen-agent",
        description=(
            "Use PROACTIVELY for any task whose deliverable is runnable code — "
            "writing/generating scripts, programs, data visualizations, or "
            "notebooks, and reviewing or refactoring code. Prefer this over "
            "writing code inline with the file tools. Pass a complete, "
            "self-contained spec (it cannot see the conversation): the goal, the "
            "data/values to embed, expected inputs/outputs, output file path, and "
            "the language/libraries to use. See the `code-generation` skill."
        ),
        graph_id="code_gen_agent",
        url="https://code-gen-agent-deployed-682e04b101d656aba3008a1dbef1884e.us.langgraph.app"
    ),
]

# Regular (dict-form) subagents. With CodeInterpreterMiddleware, the agent can
# dispatch these from interpreter code via task() — dynamic fan-out — when a
# request is phrased as a "workflow" (e.g. "run a workflow that analyzes each of
# these sources"). Without that phrasing they still work as ordinary subagents.
DYNAMIC_SUBAGENTS = [
    {
        "name": "source-analyst",
        "description": (
            "Analyzes a single source or URL and returns its key claims with "
            "citations. Dispatch one per source to analyze many sources in "
            "parallel."
        ),
        "system_prompt": (
            "You analyze one source and extract its key claims, each with a "
            "direct citation (quote + URL). Be terse and factual."
        ),
    },
]

# Tools gated behind human approval on the *served* graph (HITL demo). Passed via
# make_agent only — build_agent()'s default leaves it off so the offline eval,
# which has no checkpointer, never blocks on an interrupt.
INTERRUPT_ON = {"fetch_page": True}


def build_agent(chat_model=None, system_prompt=None, tools=None, interrupt_on=None):
    """Build the research agent.

    `chat_model`/`system_prompt`/`tools` default to the standard model, the Hub
    prompt, and both research tools — reproducing the pre-configuration agent
    (used by the offline eval and the A/B model eval, which only swaps the model).
    Skills, memory, and subagents are shared module state.
    """
    return create_deep_agent(
        model=chat_model or model,
        tools=[web_search, fetch_page] if tools is None else tools,
        system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        state_schema=StudioState,
        backend=backend,
        skills=["/skills/"],
        memory=MEMORY_SOURCES,
        subagents=async_subagents + DYNAMIC_SUBAGENTS,
        interrupt_on=interrupt_on,
        middleware=[
            PIIRedactionMiddleware(),
            RecursionFloorMiddleware(minimum=25),
            StepBudgetMiddleware(max_model_turns=MAX_MODEL_TURNS),
            CodeInterpreterMiddleware(),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})


def make_agent(config: RunnableConfig):
    """Graph factory: build the agent from the assistant's config (prompt + tools).

    Enables HITL (`interrupt_on`) on the served graph — the LangGraph server
    provides the checkpointer that persists interrupts.
    """
    system_prompt, tools = assistant_settings(config)
    return build_agent(system_prompt=system_prompt, tools=tools, interrupt_on=INTERRUPT_ON)


# Default compiled instance — imported by the offline eval. `make_agent` is what
# langgraph.json deploys (rebuilt per run from each assistant's config).
agent = build_agent()
