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
  ambient-analyst-continuous-learning loop. Injected under a character budget
  (see `harness/memory.py`) because memory is re-serialized into the prompt on
  every model turn.
- **Analysis sandbox**: a LangSmith sandbox mounted at `/analysis/` for data
  analysis, calculations, charts, and intermediate artifacts.
- A `CompositeBackend` keeps scratch files ephemeral (`StateBackend`).
"""

import logging
import os
import pathlib
import tempfile
import warnings
from typing import TYPE_CHECKING

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.composite import CompositeBackend
from deepagents.backends.context_hub import ContextHubBackend
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.langsmith import LangSmithSandbox
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, ToolMessage
from langchain.tools import ToolRuntime
from langchain_quickjs import CodeInterpreterMiddleware
from langchain_core._api import LangChainBetaWarning
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_tavily import TavilyExtract, TavilySearch
from langsmith import Client
from langsmith.sandbox import SandboxClient
from langgraph.types import Command

from agent.harness.budget import RecursionFloorMiddleware, StepBudgetMiddleware
from agent.harness.citations import CitationGuardMiddleware
from agent.harness.context import MEMORY_REPO, SKILL_HANDLES, prompt_identifier
from agent.harness.hub import ResilientHubBackend
from agent.harness.memory import (
    BudgetedMemoryMiddleware,
    COLD_MEMORY_PATH,
    HotPathMemoryMiddleware,
    MEMORY_EVENTS_PATH,
    MemorySaveClaimGuardMiddleware,
    MemoryWriteGuardMiddleware,
    SemanticPreferenceMiddleware,
    check_memory_corpus,
    run_context_interpreter,
)
from agent.harness.pii import PIIRedactionMiddleware
from agent.harness.retry import rate_limit_retry_middleware
from agent.harness.visualization import share_visualization

import dotenv

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

dotenv.load_dotenv(override=True)


logger = logging.getLogger(__name__)
warnings.filterwarnings(
    "ignore",
    category=LangChainBetaWarning,
    message=r"The class `CodeInterpreterMiddleware` is in beta\..*",
)

tavily_search = TavilySearch(max_results=5)
tavily_extract = TavilyExtract(extract_depth="advanced", format="markdown")

def _required(component: str, fn):
    try:
        return fn()
    except Exception as exc:
        raise RuntimeError(
            f"Failed to initialize {component}: {type(exc).__name__}: {exc}"
        ) from exc


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"missing {name}")
    return value


def _gateway_headers() -> dict[str, str]:
    return {"X-Tenant-ID": _required_env("LANGSMITH_WORKSPACE_ID")}


PROMPT_NAME = os.environ.get("AMBIENT_ANALYST_PROMPT_NAME", "ambient-analyst-prompt")

# Stable sandbox for analysis artifacts.
SANDBOX_NAME = os.environ.get(
    "AMBIENT_ANALYST_SANDBOX", "ambient-analyst-sandbox"
)

# Memory files loaded into context every run. Order matters: the durable
# instructions come first and are kept head-first when the budget bites, the
# append-only scorecard follows and is kept tail-first (see harness/memory.py).
MEMORY_SOURCES = ["/memory/AGENTS.md", "/memory/scorecard.md"]

# Memory is re-serialized into the system prompt on every model turn, so the
# mounted corpus is a fixed per-turn token cost. Cap what can reach the prompt;
# anything over the cap stays reachable through grep/read_file on /memory/.
MEMORY_CHAR_BUDGET = int(
    os.environ.get("AMBIENT_ANALYST_MEMORY_CHAR_BUDGET", "40000")
)
# Set to 1 (e.g. in CI) to make an over-budget memory corpus a hard failure.
MEMORY_BUDGET_STRICT = os.environ.get("AMBIENT_ANALYST_MEMORY_STRICT", "") == "1"

# Bounded research: hard step backstop + graceful final-answer turn budget.
RECURSION_LIMIT = 75
MAX_MODEL_TURNS = 25

client = Client()
DEFAULT_SYSTEM_PROMPT = _required(
    "prompt",
    lambda: client.pull_prompt(
        prompt_identifier(client),
        dangerously_pull_public_prompt=True,
    ).messages[0].prompt.template,
)

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
    skill_md.write_text(
        _required(
            f"skill {handle}",
            lambda handle=handle: client.pull_skill(handle).files["SKILL.md"].content,
        )
    )
skills_backend = FilesystemBackend(root_dir=str(skills_root), virtual_mode=True)

# Default agent model — exported so the eval suite can record it in experiment
# metadata (single source of truth for the "what model ran" tag).
DEFAULT_PROVIDER = "openai"
DEFAULT_MODEL = "gpt-5.6-luna"

model = _required(
    "model",
    lambda: init_chat_model(
        model=DEFAULT_MODEL,
        model_provider=DEFAULT_PROVIDER,
        base_url="https://gateway.smith.langchain.com/openai",
        api_key=_required_env("LC_GATEWAY_KEY"),
        default_headers=_gateway_headers(),
        reasoning_effort="none",
    ),
)

# Mount a persistent analysis environment. Create it on first startup and reuse
# it across runs so generated datasets and artifacts remain available.
sandbox_routes = {}
sandbox = None
try:
    sandbox_client = SandboxClient()
    sandbox = next(
        (
            item
            for item in sandbox_client.list_sandboxes()
            if getattr(item, "name", None) == SANDBOX_NAME
        ),
        None,
    )
    if sandbox is None:
        try:
            sandbox = sandbox_client.create_sandbox(name=SANDBOX_NAME)
        except Exception as exc:
            if "already exists" not in str(exc) and "409" not in str(exc):
                raise
            sandbox = sandbox_client.start_sandbox(SANDBOX_NAME)
    if sandbox.status != "ready":
        sandbox = sandbox_client.start_sandbox(SANDBOX_NAME)
    sandbox_routes["/analysis/"] = LangSmithSandbox(sandbox)
except Exception as exc:  # noqa: BLE001 — sandbox is optional at startup
    logger.warning(
        "Analysis sandbox %r unavailable (%s); /analysis/ route disabled.",
        SANDBOX_NAME,
        exc,
    )
ANALYSIS_SANDBOX_MOUNTED = "/analysis/" in sandbox_routes


@tool(return_direct=True)
def share_visualization_link(path: str, runtime: ToolRuntime) -> Command:
    """Publish HTML under /analysis/ as the final user-facing response."""
    if not ANALYSIS_SANDBOX_MOUNTED:
        raise RuntimeError("the analysis sandbox is unavailable")
    link = share_visualization(sandbox, path)
    response = f"[Open visualization]({link.download_url})\n\nExpires in one hour."
    return Command(
        update={
            "messages": [
                ToolMessage(content="Visualization published.", tool_call_id=runtime.tool_call_id),
                AIMessage(content=response),
            ]
        }
    )


TOOLS = {
    "tavily_search": tavily_search,
    "tavily_extract": tavily_extract,
    "run_context_interpreter": run_context_interpreter,
    "share_visualization_link": share_visualization_link,
}
DEFAULT_TOOLS = list(TOOLS.values())

VISUALIZATION_INSTRUCTIONS = """
When a visualization materially helps, write one self-contained static HTML file
under /analysis/ with inline CSS and SVG, then call share_visualization_link as
the final action. Its direct output is sent to the user unchanged. Do not use
JavaScript or external assets: the browser link renders in a sandbox. Do not
expose sensitive data.
If a user says a visualization link expired or is invalid, call
share_visualization_link again with the existing /analysis/ file path; do not
recreate the visualization.
"""

# Scratch files stay ephemeral in state; /skills serves the pulled skill repos;
# /memory persists to the LangSmith Context Hub; /analysis/ is the managed
# sandbox for calculations and artifacts.
backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/skills/": skills_backend,
        "/memory/": ResilientHubBackend(ContextHubBackend(MEMORY_REPO), max_retries=3),
        **sandbox_routes,
    },
)

# Catch unbounded memory growth at startup rather than in production token spend.
check_memory_corpus(
    backend, MEMORY_SOURCES, MEMORY_CHAR_BUDGET, strict=MEMORY_BUDGET_STRICT
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
    {
        "name": "memory-consolidator",
        "description": (
            "Cold-path worker. Consolidates repeated hot-path memory events into "
            "durable analyst preferences, standing filters, or summary updates."
        ),
        "system_prompt": (
            f"Read hot-path events from {MEMORY_EVENTS_PATH}. Use "
            "run_context_interpreter to count repeated topics and event kinds. "
            f"Update {COLD_MEMORY_PATH} only for durable patterns with clear "
            "evidence; do not rewrite broad memory summaries for one-off events."
        ),
        "tools": [run_context_interpreter],
    },
]


def assistant_settings(config: RunnableConfig | None) -> tuple[str, list["BaseTool"]]:
    cfg = (config or {}).get("configurable") or {}
    names = cfg.get("tools")
    tools = [TOOLS[n] for n in names if n in TOOLS] if names is not None else DEFAULT_TOOLS
    if share_visualization_link not in tools:
        tools.append(share_visualization_link)
    return cfg.get("system_prompt") or DEFAULT_SYSTEM_PROMPT, tools


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
        system_prompt=(system_prompt or DEFAULT_SYSTEM_PROMPT) + VISUALIZATION_INSTRUCTIONS,
        backend=backend,
        skills=["/skills/"],
        subagents=DYNAMIC_SUBAGENTS,
        middleware=[
            rate_limit_retry_middleware(),
            PIIRedactionMiddleware(),
            CitationGuardMiddleware(),
            # Passed here instead of via `memory=` so the block is size-capped.
            # deepagents' MemoryMiddleware loads the files once per request but
            # re-injects them into the system prompt on every model turn and
            # offers no before-agent-only mode — the system prompt is resent
            # with each call, so the budget, not the injection point, is what
            # bounds the cost. AnthropicPromptCachingMiddleware is inert here:
            # this agent runs an OpenAI model through the gateway.
            BudgetedMemoryMiddleware(
                backend=backend,
                sources=MEMORY_SOURCES,
                add_cache_control=True,
                char_budget=MEMORY_CHAR_BUDGET,
            ),
            SemanticPreferenceMiddleware(),
            MemoryWriteGuardMiddleware(MEMORY_SOURCES),
            MemorySaveClaimGuardMiddleware(),
            HotPathMemoryMiddleware({"tavily_search", "tavily_extract", "task"}),
            RecursionFloorMiddleware(),
            StepBudgetMiddleware(max_model_turns=MAX_MODEL_TURNS),
            CodeInterpreterMiddleware(),
        ],
    ).with_config({"recursion_limit": RECURSION_LIMIT})


def _chat_model_from_config(config: RunnableConfig):
    cfg = (config or {}).get("configurable") or {}
    configured = cfg.get("model")
    if not configured:
        return model

    if ":" in configured:
        provider, model_name = configured.split(":", 1)
    else:
        provider, model_name = DEFAULT_PROVIDER, configured
    return init_chat_model(
        model=model_name,
        model_provider=provider,
        base_url=f"https://gateway.smith.langchain.com/{provider}",
        api_key=_required_env("LC_GATEWAY_KEY"),
        default_headers=_gateway_headers(),
        reasoning_effort="none" if provider == "openai" else None,
    )


def make_agent(config: RunnableConfig):
    """Graph factory: build the agent from the assistant's config (prompt + tools).
    """
    system_prompt, tools = assistant_settings(config)
    return build_agent(
        chat_model=_chat_model_from_config(config),
        system_prompt=system_prompt,
        tools=tools,
    )


# Default compiled instance — imported by the offline eval. `make_agent` is what
# langgraph.json deploys (rebuilt per run from each assistant's config).
agent = build_agent()
