"""Per-assistant configuration, resolved from the run config at construction.

Both deployed graphs are **graph factories**: the LangSmith deployment calls
them per run with the assistant's `config`, and they build the agent from the
`configurable` fields — `system_prompt` (blank -> the Hub default) and `tools`
(a subset of `TOOLS` names; omitted -> `DEFAULT_TOOLS`). Configuration drives construction,
so the prompt is the agent's real system prompt and the tools are what's bound;
there is no runtime plumbing.

Create assistants via the deployments API with, e.g.,
`config={"configurable": {"system_prompt": "...", "tools": ["tavily_search"]}}`.
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

from langchain_tavily import TavilyExtract, TavilySearch
from langsmith import Client

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langchain_core.tools import BaseTool

tavily_search = TavilySearch(max_results=5)
tavily_extract = TavilyExtract(extract_depth="advanced", format="markdown")

TOOLS = {
    "tavily_search": tavily_search,
    "tavily_extract": tavily_extract,
}
DEFAULT_TOOLS = [tavily_search, tavily_extract]

PROMPT_NAME = os.environ.get(
    "AMBIENT_ANALYST_PROMPT_NAME", "ambient-analyst-prompt"
)
DEFAULT_SYSTEM_PROMPT = Client().pull_prompt(PROMPT_NAME).messages[0].prompt.template

# Tools that can actually persist state across runs. Only the deepagents graph
# binds any of these; the Tavily tools cannot write anything.
PERSISTENCE_TOOL_NAMES = frozenset({"read_file", "write_file", "edit_file", "ls"})

NO_MEMORY_CLAUSE = (
    "You have no durable memory in this configuration. Never state or imply "
    "that you saved, persisted, or will persist anything."
)

# The Hub template is authored for the deepagents harness; these are the pieces
# that only hold when filesystem/memory tools are bound.
_TOOL_RENAMES = (("web_search", "tavily_search"), ("fetch_page", "tavily_extract"))
_DROPPED_LINES = (
    "- Filesystem tools:",
    "- /analysis/:",
    "- Do not rely on figures recalled from /memory/",
    "- What changed in memory,",
    "Memory",
    "/memory/AGENTS.md",
    "Only persist a figure",
)
_DROPPED_STEPS = ("Check /memory/", "Read relevant skills under /skills/")
_PERSIST_MANDATE = "Before the final answer, persist durable findings"
_STEP_NUMBER = re.compile(r"^\d+\. ")


def prompt_for_tools(
    prompt: str, tools: list[BaseTool], *, filesystem: bool = False
) -> str:
    """Strip the capabilities the bound toolset cannot actually deliver."""
    if filesystem or {tool.name for tool in tools} & PERSISTENCE_TOOL_NAMES:
        return prompt
    for old, new in _TOOL_RENAMES:
        prompt = prompt.replace(old, new)
    kept: list[str] = []
    step = 0
    for line in prompt.split("\n"):
        body = _STEP_NUMBER.sub("", line)
        if line.startswith(_DROPPED_LINES) or body.startswith(_DROPPED_STEPS):
            continue
        if line.startswith(_PERSIST_MANDATE):
            line = NO_MEMORY_CLAUSE
        elif body != line:
            step += 1
            line = f"{step}. {body}"
        if not line and (not kept or not kept[-1]):
            continue
        kept.append(line)
    return "\n".join(kept)


def assistant_settings(
    config: RunnableConfig | None, *, filesystem: bool = False
) -> tuple[str, list[BaseTool]]:
    """Resolve (system_prompt, tools) from the run's `configurable` fields."""
    cfg = (config or {}).get("configurable") or {}
    names = cfg.get("tools")
    tools = [TOOLS[n] for n in names if n in TOOLS] if names is not None else DEFAULT_TOOLS
    prompt = cfg.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
    return prompt_for_tools(prompt, tools, filesystem=filesystem), tools
