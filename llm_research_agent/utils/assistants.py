"""Per-assistant configuration, resolved from the run config at construction.

Both deployed graphs are **graph factories**: the LangSmith deployment calls
them per run with the assistant's `config`, and they build the agent from the
`configurable` fields — `system_prompt` (blank -> the Hub default) and `tools`
(a subset of `TOOLS` names; omitted -> all). Configuration drives construction,
so the prompt is the agent's real system prompt and the tools are what's bound;
there is no runtime plumbing.

Create assistants via the deployments API with, e.g.,
`config={"configurable": {"system_prompt": "...", "tools": ["web_search"]}}`.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from langsmith import Client

from llm_research_agent.utils.tools import fetch_page, web_search

if TYPE_CHECKING:
    from langchain_core.runnables import RunnableConfig
    from langchain_core.tools import BaseTool

# Research tools an assistant may mix, by name.
TOOLS = {"web_search": web_search, "fetch_page": fetch_page}

# Default prompt: the Prompt Hub `llm-research-prompt` (same env var agent.py used).
_prompt = Client().pull_prompt(os.environ.get("LLM_RESEARCH_PROMPT_NAME", "llm-research-prompt"))
DEFAULT_SYSTEM_PROMPT = _prompt.messages[0].prompt.template


def assistant_settings(config: RunnableConfig | None) -> tuple[str, list[BaseTool]]:
    """Resolve (system_prompt, tools) from the run's `configurable` fields."""
    cfg = (config or {}).get("configurable") or {}
    names = cfg.get("tools")
    tools = [TOOLS[n] for n in names if n in TOOLS] if names is not None else list(TOOLS.values())
    return cfg.get("system_prompt") or DEFAULT_SYSTEM_PROMPT, tools
