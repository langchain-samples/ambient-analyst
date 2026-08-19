"""Newline-delimited rendering for bulky tool results.

The deepagents harness spills oversized tool results to
`/large_tool_results/<tool_call_id>` and tells the agent to page through the
artifact with `read_file`'s `offset`/`limit`, which are **line** based. A raw
Tavily payload serializes to a single enormous line, so every `offset > 0` read
fails with `Line offset N exceeds file length (1 lines)` and `offset=0` returns
the whole payload — re-inflating the context the offload was meant to protect.
Rendering results as newline-delimited, width-bounded text before they reach the
offload path keeps that pagination contract honest.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from langchain_core.tools import StructuredTool

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

# Wide enough to keep records readable, narrow enough that a 100-line page is a
# bounded amount of context.
MAX_LINE_CHARS = 200


def line_delimited(payload: Any) -> str:
    """Render a tool payload as newline-delimited text with bounded line length."""
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2, ensure_ascii=False)
    lines: list[str] = []
    for line in text.splitlines():
        if not line:
            lines.append("")
            continue
        for start in range(0, len(line), MAX_LINE_CHARS):
            lines.append(line[start : start + MAX_LINE_CHARS])
    return "\n".join(lines)


def line_delimited_tool(tool: BaseTool) -> BaseTool:
    """Wrap `tool` so its result is newline-delimited and line-paginatable."""

    def run(**kwargs: Any) -> str:
        return line_delimited(tool.invoke(kwargs))

    async def arun(**kwargs: Any) -> str:
        return line_delimited(await tool.ainvoke(kwargs))

    return StructuredTool.from_function(
        func=run,
        coroutine=arun,
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
    )
