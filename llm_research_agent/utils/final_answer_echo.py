"""Final-answer echo middleware: rescue the buried answer when the terminal AI
message is empty or a memory-persistence stub.

The agent's continuous-learning loop can cause it to write its substantive
answer as `content` on an AI message that also calls `edit_file` against
`/memory/*`. After the tool returns, the next model turn often produces an
empty AIMessage (or a one-line "Persisted to /memory/..." acknowledgment),
which becomes `messages[-1]` for the caller — so the user sees nothing useful.

This middleware runs in `after_agent` / `aafter_agent`: if the final AIMessage
looks empty or like a persistence stub, it walks backward to the most recent
AIMessage with substantial content and appends a fresh AIMessage carrying that
content (with no tool_calls), so `messages[-1].content` is the real answer.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import AIMessage

if TYPE_CHECKING:
    from langgraph.runtime import Runtime

_STUB_RE = re.compile(
    r"^\s*(\*\*)?(persisted|saved|memory updated|scorecard updated|"
    r"memory persisted|persisting|updated memory|updated scorecard)",
    re.IGNORECASE,
)
_STUB_MAX_LEN = 200
_SUBSTANTIVE_MIN_LEN = 400


def _message_text(msg: Any) -> str:
    """Render an AIMessage's content to a flat string, handling list-of-parts shapes."""
    content = getattr(msg, "content", "") or ""
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict) and p.get("type") == "text":
                parts.append(p.get("text", ""))
        content = "".join(parts)
    return str(content).strip()


def _is_empty_or_stub(msg: Any) -> bool:
    """True when `msg` is an AIMessage with no tool_calls whose text is empty or a persistence stub."""
    if not isinstance(msg, AIMessage):
        return False
    if getattr(msg, "tool_calls", None):
        return False
    text = _message_text(msg)
    if not text:
        return True
    return len(text) < _STUB_MAX_LEN and bool(_STUB_RE.match(text))


def _find_buried_answer(messages: list[Any]) -> str | None:
    """Find the most recent AIMessage in `messages[:-1]` whose text is substantive."""
    # Walk backward, skipping the terminal stub itself. The buried answer
    # typically rode along with an edit_file tool_call, so we don't require
    # tool_calls to be empty here.
    for msg in reversed(messages[:-1]):
        if not isinstance(msg, AIMessage):
            continue
        text = _message_text(msg)
        if len(text) >= _SUBSTANTIVE_MIN_LEN:
            return text
    return None


class FinalAnswerEchoMiddleware(AgentMiddleware):
    """Echo a buried substantive answer forward when the terminal message is empty/stub."""

    def _maybe_echo(self, state: Any) -> dict[str, Any] | None:
        """Return a state update appending the buried answer, or None for no-op."""
        messages = (
            state.get("messages") if isinstance(state, dict) else getattr(state, "messages", None)
        )
        if not messages:
            return None
        if not _is_empty_or_stub(messages[-1]):
            return None
        buried = _find_buried_answer(messages)
        if buried is None:
            return None
        return {"messages": [AIMessage(content=buried)]}

    def after_agent(self, state: Any, runtime: Runtime) -> dict[str, Any] | None:
        """Rescue a buried answer when the terminal AI message is empty or a stub."""
        return self._maybe_echo(state)

    async def aafter_agent(self, state: Any, runtime: Runtime) -> dict[str, Any] | None:
        """Async variant of `after_agent`."""
        return self._maybe_echo(state)
