"""Reconcile claimed memory persistence against the run's actual tool calls.

The system prompt requires the agent to state what it persisted before the final
answer. The model can satisfy that instruction narratively — declaring it updated
`/memory/AGENTS.md` — without ever calling `write_file`/`edit_file`, so the
continuous-learning loop silently does nothing while the user is told their
context was saved.

This middleware makes the claim verifiable: after the agent finishes it looks for
a `write_file`/`edit_file` call against a `/memory/` path that actually returned
success, and if the final answer asserts a memory update anyway, it rewrites that
sentence to say plainly that nothing was persisted. Runs that genuinely wrote,
and runs that use the sanctioned "nothing durable was saved" phrasing, pass
through untouched.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import AIMessage, ToolMessage

if TYPE_CHECKING:
    from langgraph.runtime import Runtime

MEMORY_PREFIX = "/memory/"
MEMORY_WRITE_TOOLS = {"write_file", "edit_file"}

# A tool result counts as a write only when it isn't an error. Backend failures
# (e.g. a Context Hub 409 on a stale base commit) surface as error ToolMessages.
_ERROR_MARKERS = ("error", "failed", "exception", "traceback")

_MEMORY_TOKEN = r"(?:/memory/?|memor(?:y|ies)|AGENTS\.md|scorecard\.md)"
_WRITE_VERB = (
    r"(?:saved|persisted|stored|wrote|written|writing|added|appended|updated|"
    r"recorded|logged|captured|committed)"
)
_CLAIM_PATTERNS = (
    re.compile(rf"\b{_WRITE_VERB}\b[^.!?\n]{{0,160}}?{_MEMORY_TOKEN}", re.I),
    re.compile(rf"{_MEMORY_TOKEN}[^.!?\n]{{0,160}}?\b{_WRITE_VERB}\b", re.I),
)

# Explicit negative disclosures the prompt sanctions — never rewrite these.
_NEGATIVE_MARKERS = (
    "nothing durable",
    "nothing new",
    "nothing warranted",
    "nothing to persist",
    "nothing persisted",
    "nothing was persisted",
    "nothing saved",
    "no durable",
    "no memory update",
    "no update to memory",
    "no changes to memory",
    "not saved",
    "not persisted",
    "did not save",
    "didn't save",
    "no new memory",
)

_CORRECTION = (
    "Saved to memory: nothing was persisted this run — no successful write to "
    "/memory/ was made, so the findings above were not saved and will not carry "
    "over to future sessions."
)

# Sentence boundaries, minus the abbreviations that pepper analyst prose ("the
# U.S.", "e.g.") — splitting inside one would leave an ungrammatical remnant of a
# rewritten claim behind.
_SENTENCE_SPLIT = re.compile(
    r"(?<=[.!?])(?=\s)"
    r"(?<!\b[A-Z]\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bvs\.)(?<!\betc\.)(?<!\bcf\.)"
)


def _as_text(content: str | list | None) -> str:
    """Flatten message content (string or content-block list) to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "".join(parts)
    return ""


def _memory_write_call_ids(messages: list[Any]) -> set[str]:
    """Ids of `write_file`/`edit_file` calls whose arguments target a `/memory/` path."""
    ids = set()
    for message in messages:
        for call in getattr(message, "tool_calls", None) or []:
            if call.get("name") not in MEMORY_WRITE_TOOLS:
                continue
            args = call.get("args") or {}
            if any(
                isinstance(value, str) and value.startswith(MEMORY_PREFIX)
                for value in args.values()
            ):
                ids.add(call.get("id"))
    return ids


def _is_error_result(message: ToolMessage) -> bool:
    if getattr(message, "status", None) == "error":
        return True
    text = _as_text(message.content).strip().lower()
    return any(text.startswith(marker) for marker in _ERROR_MARKERS)


def has_successful_memory_write(messages: list[Any]) -> bool:
    """True when some `/memory/` write tool call returned a non-error result."""
    call_ids = _memory_write_call_ids(messages)
    if not call_ids:
        return False
    return any(
        isinstance(m, ToolMessage)
        and m.tool_call_id in call_ids
        and not _is_error_result(m)
        for m in messages
    )


def _is_affirmative_claim(sentence: str) -> bool:
    lowered = sentence.lower()
    if any(marker in lowered for marker in _NEGATIVE_MARKERS):
        return False
    return any(pattern.search(sentence) for pattern in _CLAIM_PATTERNS)


def rewrite_unbacked_claim(text: str) -> str:
    """Replace affirmative memory-persistence sentences with the no-write correction."""
    corrected = False
    lines = []
    for line in text.split("\n"):
        pieces = []
        changed = False
        for sentence in _SENTENCE_SPLIT.split(line):
            if not _is_affirmative_claim(sentence):
                pieces.append(sentence)
                continue
            changed = True
            leading = sentence[: len(sentence) - len(sentence.lstrip())]
            # Only the first claim carries the correction; later ones are dropped
            # so the disclosure isn't repeated across the answer.
            pieces.append(leading + _CORRECTION if not corrected else leading)
            corrected = True
        joined = "".join(pieces)
        lines.append(joined.rstrip() if changed else line)
    return "\n".join(lines)


class MemoryAssertionMiddleware(AgentMiddleware):
    """Rewrite final-answer memory-persistence claims that no write tool call backs."""

    def _reconcile(self, state: Any) -> dict[str, Any] | None:
        messages = (state or {}).get("messages") or []
        if not messages:
            return None
        final = messages[-1]
        if not isinstance(final, AIMessage) or getattr(final, "tool_calls", None):
            return None
        if has_successful_memory_write(messages):
            return None
        text = _as_text(final.content)
        rewritten = rewrite_unbacked_claim(text)
        if rewritten == text:
            return None
        return {"messages": [final.model_copy(update={"content": rewritten})]}

    def after_agent(self, state: Any, runtime: Runtime) -> dict[str, Any] | None:
        """Reconcile the final answer's memory claim with the run's tool calls."""
        return self._reconcile(state)

    async def aafter_agent(self, state: Any, runtime: Runtime) -> dict[str, Any] | None:
        """Async variant of `after_agent`."""
        return self._reconcile(state)


if __name__ == "__main__":
    def _write_call(path: str, call_id: str) -> AIMessage:
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "write_file",
                    "args": {"file_path": path, "content": "note"},
                    "id": call_id,
                    "type": "tool_call",
                }
            ],
        )

    claim = (
        "Here is the analysis.\n\n"
        "What I saved to memory: I updated the regional-bank watchlist note in "
        "`/memory/AGENTS.md` to reflect the verified framing."
    )
    mw = MemoryAssertionMiddleware()

    # 1. Affirmative claim backed by a successful /memory/ write — unchanged.
    backed = [
        _write_call("/memory/AGENTS.md", "c1"),
        ToolMessage(content="Updated /memory/AGENTS.md", tool_call_id="c1"),
        AIMessage(content=claim, id="final"),
    ]
    assert mw.after_agent({"messages": backed}, None) is None

    # 2. Affirmative claim with no write tool call at all — claim is rewritten.
    unbacked = [
        AIMessage(
            content="",
            tool_calls=[
                {"name": "read_file", "args": {"file_path": "/memory/AGENTS.md"},
                 "id": "r1", "type": "tool_call"}
            ],
        ),
        ToolMessage(content="1 # Ambient Analyst Memory", tool_call_id="r1"),
        AIMessage(content=claim, id="final"),
    ]
    update = mw.after_agent({"messages": unbacked}, None)
    assert update is not None
    fixed = update["messages"][0]
    assert fixed.id == "final"
    assert "/memory/AGENTS.md` to reflect" not in fixed.content
    assert "no successful write to /memory/" in fixed.content
    assert fixed.content.startswith("Here is the analysis.")

    # Abbreviations inside the claim don't leave a remnant behind.
    abbrev = (
        "Ranking: Japan, then France.\n\n"
        "Saved to memory: I added a durable note that the main concerns are "
        "Japan, the U.S., and the U.K., per verified 2026 sources."
    )
    update = mw.after_agent({"messages": [AIMessage(content=abbrev, id="final")]}, None)
    assert update is not None
    assert update["messages"][0].content == (
        "Ranking: Japan, then France.\n\n" + _CORRECTION
    ), update["messages"][0].content

    # 3. The sanctioned negative disclosure passes through unchanged.
    disclosed = [
        AIMessage(
            content=(
                "Here is the analysis.\n\n"
                "Saved to memory: nothing durable — this run only restated "
                "already-recorded findings, so no memory update was made."
            ),
            id="final",
        ),
    ]
    assert mw.after_agent({"messages": disclosed}, None) is None

    # A failed write (e.g. Context Hub 409) does not count as persistence.
    failed = [
        _write_call("/memory/AGENTS.md", "c2"),
        ToolMessage(content="Error: 409 conflict", tool_call_id="c2", status="error"),
        AIMessage(content=claim, id="final"),
    ]
    assert mw.after_agent({"messages": failed}, None) is not None

    # A write outside /memory/ does not back a memory claim.
    elsewhere = [
        _write_call("/analysis/notes.md", "c3"),
        ToolMessage(content="wrote /analysis/notes.md", tool_call_id="c3"),
        AIMessage(content=claim, id="final"),
    ]
    assert mw.after_agent({"messages": elsewhere}, None) is not None

    # Answers that never claim persistence are untouched.
    quiet = [AIMessage(content="Rates are likely to stay elevated.", id="final")]
    assert mw.after_agent({"messages": quiet}, None) is None

    print("ok")
