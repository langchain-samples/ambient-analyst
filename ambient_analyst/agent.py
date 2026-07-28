"""Ambient Analyst: a macroeconomic and business analysis agent.

Ambient Analyst is built on the LangChain DeepAgents framework. It investigates
economic conditions, industries, companies, competitive dynamics, and emerging
technologies. LLM landscape research is one specialist capability.

Storage in LangSmith (workspace-scoped API key resolves its own tenant — no
`LANGSMITH_WORKSPACE_ID` needed):
- **System prompt**: Prompt Hub prompt `ambient-analyst-prompt`, pulled at
  construction. Its system message is used as the agent's system prompt.
- **Skills**: separate Context Hub *skill repos* (one per skill), pulled at
  construction and staged under `/skills/<name>/SKILL.md` so the SkillsMiddleware
  discovers them with progressive disclosure.
- **Memory**: Context Hub *agent repo* `ambient-analyst-memory` (`AGENTS.md` +
  `scorecard.md`), mounted at `/memory/` and written back at runtime — the
  ambient-analyst-continuous-learning loop.
- **Analysis sandbox**: a LangSmith sandbox mounted at `/analysis/` for data
  analysis, calculations, charts, and intermediate artifacts.
- A `CompositeBackend` keeps scratch files ephemeral (`StateBackend`).
"""

import logging
import os
import pathlib
import tempfile

from deepagents import create_deep_agent, DeepAgentState
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

from ambient_analyst.utils.assistants import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_TOOLS,
    assistant_settings,
)
from ambient_analyst.utils.budget import RecursionFloorMiddleware, StepBudgetMiddleware
from ambient_analyst.utils.pii import PIIRedactionMiddleware
from ambient_analyst.utils.retry import rate_limit_retry_middleware

import dotenv

dotenv.load_dotenv(override=True)


logger = logging.getLogger(__name__)

# LangSmith resources (override via env to target staging vs production).
MEMORY_REPO = os.environ.get("AMBIENT_ANALYST_MEMORY_REPO", "ambient-analyst-memory")
# Each skill is its own Context Hub skill repo; handle == skill (and directory) name.
SKILL_HANDLES = [
    h.strip()
    for h in os.environ.get(
        "AMBIENT_ANALYST_SKILLS",
        "ambient-analyst-model-evaluation,ambient-analyst-benchmark-analysis,ambient-analyst-landscape-mapping,"
        "ambient-analyst-scorecard-maintenance,ambient-analyst-continuous-learning",
    ).split(",")
    if h.strip()
]

# Stable sandbox for analysis artifacts.
SANDBOX_NAME = os.environ.get(
    "AMBIENT_ANALYST_SANDBOX", "ambient-analyst-sandbox"
)

# Memory files loaded into context every run.
MEMORY_SOURCES = ["/memory/AGENTS.md", "/memory/scorecard.md"]

# Bounded research: hard step backstop + graceful final-answer turn budget.
RECURSION_LIMIT = 75
MAX_MODEL_TURNS = 25

client = Client()

# The system prompt and tool selection come from the assistant's config (see
# utils/assistants.py); `build_agent` takes them as arguments and the `make_agent`
# factory resolves them per run. Defaults reproduce the pre-configuration agent.

# Skills: deepagents has no native "mount N skill repos" backend, so we pull each
# repo's SKILL.md into a temp dir as <name>/SKILL.md and root a FilesystemBackend
# there. virtual_mode=True keeps paths relative to root_dir (required for
# CompositeBackend routing) and blocks ../absolute escapes. Skills refresh on
# restart — they're curated, stable config; the evolving state is memory.
skills_root = pathlib.Path(tempfile.mkdtemp(prefix="ambient_analyst_skills_"))
for handle in SKILL_HANDLES:
    skill_md = skills_root / handle / "SKILL.md"
    skill_md.parent.mkdir(parents=True)
    skill_md.write_text(client.pull_skill(handle).files["SKILL.md"].content)
skills_backend = FilesystemBackend(root_dir=str(skills_root), virtual_mode=True)

# Default agent model — exported so the eval suite can record it in experiment
# metadata (single source of truth for the "what model ran" tag).
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-5.4-mini-2026-03-17"

model = init_chat_model(
    model=DEFAULT_MODEL,
    model_provider=DEFAULT_PROVIDER,
    base_url="https://gateway.smith.langchain.com/openai",
    api_key=os.getenv("LC_GATEWAY_KEY")
)

# Mount a persistent analysis environment. Create it on first startup and reuse
# it across runs so generated datasets and artifacts remain available.
sandbox_routes = {}
try:
    sandbox_client = SandboxClient()
    existing = [
        item
        for item in sandbox_client.list_sandboxes()
        if getattr(item, "name", None) == SANDBOX_NAME
    ]
    sandbox = (
        existing[0]
        if existing
        else sandbox_client.create_sandbox(name=SANDBOX_NAME)
    )
    if sandbox.status != "ready":
        sandbox = sandbox_client.start_sandbox(SANDBOX_NAME)
    sandbox_routes["/analysis/"] = LangSmithSandbox(sandbox)
except Exception as exc:  # noqa: BLE001 — sandbox is optional at startup
    logger.warning(
        "Analysis sandbox %r unavailable (%s); /analysis/ route disabled.",
        SANDBOX_NAME,
        exc,
    )

# Scratch files stay ephemeral in state; /skills serves the pulled skill repos;
# /memory persists to the LangSmith Context Hub; /analysis/ is the managed
# sandbox for calculations and artifacts.
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/skills/": skills_backend,
        "/memory/": ContextHubBackend(MEMORY_REPO),
        **sandbox_routes,
    },
)

# Regular (dict-form) subagents. With CodeInterpreterMiddleware, the agent can
# dispatch these from interpreter code via task() — dynamic fan-out — when a
# request is phrased as a "workflow" (e.g. "run a workflow that analyzes each of
# these sources"). Without that phrasing they still work as ordinary subagents.
DYNAMIC_SUBAGENTS = [
    {
        "name": "macro-analysis-worker",
        "description": (
            "Analyzes one source, company, industry, country, economic indicator, "
            "or scenario. Dispatch workers in parallel for comparative and "
            "multi-source macroeconomic or business analysis."
        ),
        "system_prompt": (
            "You are a macroeconomic and business analysis specialist. Evaluate "
            "the assigned unit, separate facts from inference, quantify material "
            "drivers where possible, identify risks and counterarguments, and "
            "cite dated primary sources. Return a concise analyst brief."
        ),
    },
]

def build_agent(chat_model=None, system_prompt=None, tools=None):
    """Build the Ambient Analyst agent.

    `chat_model`/`system_prompt`/`tools` default to the standard model, the Hub
    prompt, and the default tool set — reproducing the pre-configuration agent
    (used by the offline eval and the A/B model eval, which only swaps the model).
    Skills, memory, and subagents are shared module state.
    """
    return create_deep_agent(
        model=chat_model or model,
        tools=DEFAULT_TOOLS if tools is None else tools,
        system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        backend=backend,
        skills=["/skills/"],
        memory=MEMORY_SOURCES,
        subagents=DYNAMIC_SUBAGENTS,
        middleware=[
            rate_limit_retry_middleware(),
            PIIRedactionMiddleware(),
            RecursionFloorMiddleware(),
            StepBudgetMiddleware(max_model_turns=MAX_MODEL_TURNS),
            CodeInterpreterMiddleware(),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})


def make_agent(config: RunnableConfig):
    """Graph factory: build the agent from the assistant's config (prompt + tools).
    """
    system_prompt, tools = assistant_settings(config)
    return build_agent(system_prompt=system_prompt, tools=tools)


# Default compiled instance — imported by the offline eval. `make_agent` is what
# langgraph.json deploys (rebuilt per run from each assistant's config).
agent = build_agent()
