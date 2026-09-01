"""Agent memory middleware and compact event analysis tools."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import datetime, timezone
import json
import re
from typing import Any

from deepagents.backends.context_hub import ContextHubBackend
from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from agent.harness.context import MEMORY_REPO
from agent.harness.pii import redact

MEMORY_EVENTS_FILE = "hot-path-events.jsonl"
MEMORY_EVENTS_PATH = f"/memory/{MEMORY_EVENTS_FILE}"
COLD_MEMORY_PATH = "/memory/cold-path-memory.md"
MEMORY_WRITE_TOOLS = frozenset({"write_file", "edit_file"})
# Harness-owned paths: not injected into context, but read back by name (the
# hot-path log and the memory-consolidator's cold-path file), so writes to them
# are not silently lost the way an ad-hoc new file under /memory/ would be.
HARNESS_MEMORY_PATHS = frozenset({MEMORY_EVENTS_PATH, COLD_MEMORY_PATH})
_PREFERENCE_PATTERNS = [
    re.compile(r"\bremember that (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)", re.I),
    re.compile(r"\bi prefer (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)", re.I),
    re.compile(
        r"\bplease (?:use|prefer) (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)",
        re.I,
    ),
    re.compile(r"\bmy preference is (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)", re.I),
]


def _append_memory_event(event: dict[str, Any]) -> str | None:
    backend = ContextHubBackend(MEMORY_REPO)
    previous = backend.read(MEMORY_EVENTS_FILE)
    content = "" if previous.error or previous.file_data is None else previous.file_data.content
    # ponytail: full-file rewrite is fine for demos; use DB append for concurrent writers.
    result = backend.write(
        MEMORY_EVENTS_FILE,
        content + json.dumps(event, sort_keys=True) + "\n",
    )
    return result.error


def _latest_human_text(state: Any) -> str:
    messages = state.get("messages", []) if isinstance(state, dict) else []
    for message in reversed(messages):
        if not isinstance(message, HumanMessage):
            continue
        if isinstance(message.content, str):
            return message.content
    return ""


def _extract_preferences(text: str) -> list[str]:
    return [
        redact(match.group("preference").strip())
        for pattern in _PREFERENCE_PATTERNS
        for match in pattern.finditer(text)
        if match.group("preference").strip()
    ]


def _parse_events(payload: str) -> list[dict]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return [
            item
            for line in payload.splitlines()
            if line.strip()
            for item in [json.loads(line)]
            if isinstance(item, dict)
        ]
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def _event_summary(events: list[dict]) -> dict:
    return {
        "event_count": len(events),
        "topics": Counter(str(e.get("topic", "unknown")) for e in events).most_common(10),
        "event_kinds": Counter(
            str(e.get("event_kind") or e.get("kind") or "memory_event") for e in events
        ).most_common(10),
        "confidence": Counter(
            str(e.get("confidence", "unspecified")) for e in events
        ).most_common(),
        "sources": Counter(str(e.get("source", "unspecified")) for e in events).most_common(
            10
        ),
        "samples": events[:5],
    }


@tool
def run_context_interpreter(events_json: str) -> str:
    """Summarize memory/event JSON with exact counts before LLM judgment."""
    return json.dumps(_event_summary(_parse_events(events_json)), indent=2, sort_keys=True)


class HotPathMemoryMiddleware(AgentMiddleware):
    """Deterministically append selected completed tool calls to memory."""

    def __init__(self, tool_names: set[str]) -> None:
        self.tool_names = tool_names

    def _record(self, request: Any, result: Any) -> None:
        name = request.tool_call.get("name")
        if name not in self.tool_names:
            return
        _append_memory_event(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event_kind": "tool_call_completed",
                "topic": name,
                "fact": f"{name} completed on the hot path",
                "evidence": json.dumps(request.tool_call.get("args", {}), sort_keys=True),
                "source": "HotPathMemoryMiddleware",
                "confidence": "high",
                "status": getattr(result, "status", "success"),
            }
        )

    def wrap_tool_call(self, request: Any, handler: Any) -> Any:
        result = handler(request)
        self._record(request, result)
        return result

    async def awrap_tool_call(self, request: Any, handler: Any) -> Any:
        result = await handler(request)
        self._record(request, result)
        return result


class MemoryWriteGuardMiddleware(AgentMiddleware):
    """Reject durable writes to /memory/ paths that are never loaded back into context."""

    def __init__(self, injected_paths: Iterable[str]) -> None:
        self.allowed_paths = set(injected_paths) | HARNESS_MEMORY_PATHS

    def _rejection(self, request: Any) -> str | None:
        tool_call = getattr(request, "tool_call", None) or {}
        if tool_call.get("name") not in MEMORY_WRITE_TOOLS:
            return None
        path = (tool_call.get("args") or {}).get("file_path")
        if not isinstance(path, str) or not path.startswith("/memory/"):
            return None
        if path in self.allowed_paths:
            return None
        return (
            f"Rejected: {path} is not loaded into context. Durable findings must be "
            "written to /memory/AGENTS.md (or /memory/scorecard.md for LLM scorecard "
            "rows)."
        )

    def wrap_tool_call(self, request: Any, handler: Any) -> Any:
        rejection = self._rejection(request)
        return rejection if rejection is not None else handler(request)

    async def awrap_tool_call(self, request: Any, handler: Any) -> Any:
        rejection = self._rejection(request)
        return rejection if rejection is not None else await handler(request)


class SemanticPreferenceMiddleware(AgentMiddleware):
    """Extract explicit user preferences with regex before the model runs."""

    def before_agent(self, state: Any, runtime: Any) -> None:
        self._record_preferences(_latest_human_text(state))

    async def abefore_agent(self, state: Any, runtime: Any) -> None:
        self._record_preferences(_latest_human_text(state))

    def _record_preferences(self, text: str) -> None:
        for preference in _extract_preferences(text):
            _append_memory_event(
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "event_kind": "preference_extracted",
                    "topic": "user_preference",
                    "fact": preference,
                    "evidence": preference,
                    "source": "SemanticPreferenceMiddleware",
                    "confidence": "high",
                }
            )


if __name__ == "__main__":
    from types import SimpleNamespace

    events = _parse_events(
        '{"topic":"rates","event_kind":"preference"}\n{"topic":"rates"}'
    )
    summary = _event_summary(events)
    assert summary["event_count"] == 2
    assert summary["topics"][0] == ("rates", 2)
    assert dict(summary["event_kinds"])["memory_event"] == 1
    assert _event_summary([{"topic": "tavily_search"}])["event_count"] == 1
    assert _extract_preferences("I prefer concise answers.") == ["concise answers"]
    assert "[REDACTED_EMAIL]" in _extract_preferences(
        "Remember that my email is me@example.com."
    )[0]

    guard = MemoryWriteGuardMiddleware(["/memory/AGENTS.md", "/memory/scorecard.md"])
    handled = object()

    def _write(path: str) -> SimpleNamespace:
        return SimpleNamespace(
            tool_call={"name": "write_file", "args": {"file_path": path}}
        )

    assert guard.wrap_tool_call(_write("/memory/AGENTS.md"), lambda r: handled) is handled
    assert guard.wrap_tool_call(_write("/analysis/foo.csv"), lambda r: handled) is handled
    assert guard.wrap_tool_call(_write(COLD_MEMORY_PATH), lambda r: handled) is handled
    orphan = guard.wrap_tool_call(
        _write("/memory/frontier-market-growth-2026.md"), lambda r: handled
    )
    assert "is not loaded into context" in orphan, orphan
    assert "/memory/AGENTS.md" in orphan, orphan
    print("ok")
