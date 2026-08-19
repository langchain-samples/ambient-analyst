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
from typing import TYPE_CHECKING

from langchain_tavily import TavilyExtract, TavilySearch
from langsmith import Client

from ambient_analyst.utils.tool_results import line_delimited_tool

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langchain_core.tools import BaseTool

# Search/extract payloads are the results that overflow the context window and get
# offloaded to `/large_tool_results/`; the wrapper makes them newline-delimited so
# the harness' line-based `offset`/`limit` pagination advice actually works.
tavily_search = line_delimited_tool(TavilySearch(max_results=5))
tavily_extract = line_delimited_tool(
    TavilyExtract(extract_depth="advanced", format="markdown")
)

TOOLS = {
    "tavily_search": tavily_search,
    "tavily_extract": tavily_extract,
}
DEFAULT_TOOLS = [tavily_search, tavily_extract]

PROMPT_NAME = os.environ.get(
    "AMBIENT_ANALYST_PROMPT_NAME", "ambient-analyst-prompt"
)
DEFAULT_SYSTEM_PROMPT = Client().pull_prompt(PROMPT_NAME).messages[0].prompt.template


def assistant_settings(config: RunnableConfig | None) -> tuple[str, list[BaseTool]]:
    """Resolve (system_prompt, tools) from the run's `configurable` fields."""
    cfg = (config or {}).get("configurable") or {}
    names = cfg.get("tools")
    tools = [TOOLS[n] for n in names if n in TOOLS] if names is not None else DEFAULT_TOOLS
    return cfg.get("system_prompt") or DEFAULT_SYSTEM_PROMPT, tools
