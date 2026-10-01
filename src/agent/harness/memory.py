"""Agent memory middleware and compact event analysis tools.

deepagents' `MemoryMiddleware` loads `/memory/` once per request but re-injects
the whole block into the system prompt on every model turn, so the mounted
corpus is a fixed per-turn token cost with no before-agent-only mode to switch
to. `BudgetedMemoryMiddleware` bounds that cost; `check_memory_corpus` reports
growth past the budget at startup.
"""

import asyncio
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
import re
from typing import Any

from deepagents.backends.context_hub import ContextHubBackend
from deepagents.middleware.memory import MemoryMiddleware
from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.config import get_config

from agent.harness.context import MEMORY_REPO
from agent.harness.hub import hub_result_content, hub_result_value
from agent.harness.pii import redact

logger = logging.getLogger(__name__)

MEMORY_EVENTS_FILE = "hot-path-events.jsonl"
MEMORY_EVENTS_PATH = f"/memory/{MEMORY_EVENTS_FILE}"
MEMORY_EVENTS_MAX_LINES = 500
COLD_MEMORY_PATH = "/memory/cold-path-memory.md"
MEMORY_WRITE_TOOLS = frozenset({"write_file", "edit_file"})
HARNESS_MEMORY_PATHS = frozenset({MEMORY_EVENTS_PATH, COLD_MEMORY_PATH})
_HEADING_PATTERN = re.compile(r"^##+ \S.*$", re.M)
MEMORY_TRUNCATION_NOTICE = (
    "[MEMORY TRUNCATED: {elided} of {total} characters of {path} were elided to "
    "stay within the {budget}-character memory budget, so what you see above is "
    "incomplete. Do not assume the omitted content does not exist — use the "
    "`grep` and `read_file` tools against `{path}` to retrieve anything you need "
    "from the part that is not shown.]"
)
_PREFERENCE_PATTERNS = [
    re.compile(r"\bremember that (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)", re.I),
    re.compile(r"\bi prefer (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)", re.I),
    re.compile(
        r"\bplease (?:use|prefer) (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)",
        re.I,
    ),
    re.compile(r"\bmy preference is (?P<preference>[^\n]+?)(?:[.!?](?:\s|$)|$)", re.I),
]


@dataclass
class _FailedHubCall:
    """Stand-in result for a Hub call that raised instead of returning one."""

    error: str
    file_data: None = None


def _safe_hub_call(fn: Any, *args: Any, **kwargs: Any) -> Any:
    """Run a Hub call, converting a raised transport error into a result object."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 — memory bookkeeping is never fatal
        return _FailedHubCall(error=f"{type(exc).__name__}: {exc}")


def _append_memory_event(event: dict[str, Any]) -> str | None:
    """Append one event to the bounded hot-path log, returning any error text."""
    backend = _safe_hub_call(ContextHubBackend, MEMORY_REPO)
    if isinstance(backend, _FailedHubCall):
        return backend.error
    previous = _safe_hub_call(backend.read, MEMORY_EVENTS_FILE)
    if isinstance(previous, _FailedHubCall):
        # Writing on an unreadable log would replace the whole history with one event.
        return previous.error
    file_data = hub_result_value(previous, "file_data")
    content = (
        ""
        if hub_result_value(previous, "error") or file_data is None
        else hub_result_content(file_data)
    )
    # Bounded-tail stopgap: the full-file rewrite pushes the entire log on every
    # call, so keep only the newest events. An append-only store (DB or a Hub
    # append API) is the real fix and also handles concurrent writers.
    lines = [line for line in content.splitlines() if line.strip()][
        -(MEMORY_EVENTS_MAX_LINES - 1) :
    ]
    lines.append(json.dumps(event, sort_keys=True))
    result = _safe_hub_call(backend.write, MEMORY_EVENTS_FILE, "\n".join(lines) + "\n")
    return hub_result_value(result, "error")


def _read_memory_file(path: str) -> str | None:
    """Read a mounted /memory/ file from the Hub, returning None when unreadable."""
    backend = _safe_hub_call(ContextHubBackend, MEMORY_REPO)
    if isinstance(backend, _FailedHubCall):
        return None
    result = _safe_hub_call(backend.read, path.removeprefix("/memory/"))
    if isinstance(result, _FailedHubCall) or hub_result_value(result, "error"):
        return None
    file_data = hub_result_value(result, "file_data")
    return None if file_data is None else hub_result_content(file_data)


def _headings(text: str) -> list[str]:
    return [match.group(0).strip() for match in _HEADING_PATTERN.finditer(text)]


def _duplicated_headings(
    current: str, old: str, new: str, *, whole_file: bool
) -> list[str]:
    """Return headings the proposed write would leave appearing twice in the file."""
    counts: Counter[str] = Counter()
    if not whole_file:
        counts = Counter(_headings(current)) - Counter(_headings(old))
    counts += Counter(_headings(new))
    return [heading for heading in dict.fromkeys(_headings(new)) if counts[heading] > 1]


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
        # Runs after the wrapped tool succeeded, so a failed append must not
        # discard that result.
        error = _append_memory_event(
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
        if error:
            logger.warning(
                "Hot-path memory append for %r failed (%s); keeping the tool result.",
                name,
                error,
            )

    def wrap_tool_call(self, request: Any, handler: Any) -> Any:
        result = handler(request)
        self._record(request, result)
        return result

    async def awrap_tool_call(self, request: Any, handler: Any) -> Any:
        result = await handler(request)
        await asyncio.to_thread(self._record, request, result)
        return result


class MemoryWriteGuardMiddleware(AgentMiddleware):
    """Reject durable writes to /memory/ paths that are never loaded back into context."""

    def __init__(self, injected_paths: Iterable[str]) -> None:
        self.allowed_paths = set(injected_paths) | HARNESS_MEMORY_PATHS

    def _rejection(self, request: Any) -> str | None:
        tool_call = getattr(request, "tool_call", None) or {}
        if tool_call.get("name") not in MEMORY_WRITE_TOOLS:
            return None
        args = tool_call.get("args") or {}
        path = args.get("file_path")
        if not isinstance(path, str) or not path.startswith("/memory/"):
            return None
        if path in self.allowed_paths:
            return self._duplicate_heading_rejection(path, args)
        return (
            f"Rejected: {path} is not loaded into context. Durable findings must be "
            "written to /memory/AGENTS.md (or /memory/scorecard.md for LLM scorecard "
            "rows)."
        )

    def _duplicate_heading_rejection(self, path: str, args: dict) -> str | None:
        if path in HARNESS_MEMORY_PATHS:
            return None
        whole_file = "content" in args
        proposed = args.get("content") if whole_file else args.get("new_string")
        if not isinstance(proposed, str) or not _headings(proposed):
            return None
        current = _read_memory_file(path)
        if current is None:
            # An unreadable corpus must not block a durable save.
            return None
        old = args.get("old_string")
        duplicated = _duplicated_headings(
            current, old if isinstance(old, str) else "", proposed, whole_file=whole_file
        )
        if not duplicated:
            return None
        return (
            f"Rejected: the heading {duplicated[0]!r} already exists in {path}, and "
            "every heading there is a unique anchor — re-emitting it would create a "
            "second section with the same title and leave neither usable as an "
            "anchor. Append inside the existing section instead: read the lines under "
            "that heading, then set old_string to its last bullet and new_string to "
            "that same bullet plus your new one."
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
        await asyncio.to_thread(self._record_preferences, _latest_human_text(state))

    def _record_preferences(self, text: str) -> None:
        for preference in _extract_preferences(text):
            error = _append_memory_event(
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
            if error:
                logger.warning(
                    "Preference memory append failed (%s); continuing the run.", error
                )


class MemoryBudgetExceededError(RuntimeError):
    """Raised by `check_memory_corpus` in strict mode when memory outgrows its budget."""


def _keep_lines(text: str, budget: int, *, from_end: bool) -> str:
    """Return as many whole lines of `text` as fit in `budget` characters."""
    if budget <= 0:
        return ""
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    used = 0
    for line in reversed(lines) if from_end else lines:
        if used + len(line) > budget:
            break
        kept.append(line)
        used += len(line)
    if from_end:
        kept.reverse()
    return "".join(kept)


def _allocate(sizes: dict[str, int], budget: int) -> dict[str, int]:
    """Split `budget` across sources, letting small sources release their slack."""
    allocation: dict[str, int] = {}
    pending = dict(sizes)
    remaining = budget
    while pending:
        share = remaining // len(pending)
        satisfied = [path for path, size in pending.items() if size <= share]
        if not satisfied:
            allocation.update({path: share for path in pending})
            break
        for path in satisfied:
            allocation[path] = pending.pop(path)
            remaining -= allocation[path]
    return allocation


def compact_memory_contents(
    contents: dict[str, str], sources: Sequence[str], budget: int
) -> dict[str, str]:
    """Trim loaded memory to `budget` characters total, marking what was elided."""
    present = [path for path in sources if contents.get(path) is not None]
    allocation = _allocate({path: len(contents[path]) for path in present}, budget)
    compacted: dict[str, str] = {}
    for index, path in enumerate(present):
        raw = contents[path]
        allowance = allocation[path]
        if len(raw) <= allowance:
            compacted[path] = raw
            continue
        # The first source holds the durable instructions, which lead the file;
        # later sources are append-only logs whose newest entries are at the end.
        from_end = index > 0
        reserve = len(
            MEMORY_TRUNCATION_NOTICE.format(
                elided=len(raw), total=len(raw), path=path, budget=budget
            )
        )
        kept = _keep_lines(raw, allowance - reserve - 1, from_end=from_end)
        notice = MEMORY_TRUNCATION_NOTICE.format(
            elided=len(raw) - len(kept), total=len(raw), path=path, budget=budget
        )
        compacted[path] = f"{notice}\n{kept}" if from_end else f"{kept}\n{notice}"
        logger.info(
            "Memory source %s truncated from %d to %d characters (%d-character "
            "budget); the agent must grep/read_file for the rest.",
            path,
            len(raw),
            len(kept),
            budget,
        )
    return compacted


def check_memory_corpus(
    backend: Any, sources: Sequence[str], budget: int, *, strict: bool = False
) -> int:
    """Log the mounted memory size and flag (or raise on) a corpus over `budget`."""
    responses = _safe_hub_call(backend.download_files, list(sources))
    if isinstance(responses, _FailedHubCall):
        logger.warning(
            "Could not measure the memory corpus (%s); skipping the budget check.",
            responses.error,
        )
        return 0
    sizes = {
        path: len(hub_result_content(response))
        for path, response in zip(sources, responses, strict=True)
        if hub_result_value(response, "content") is not None
    }
    total = sum(sizes.values())
    if total > budget:
        message = (
            f"Memory corpus is {total} characters, over the {budget}-character "
            f"budget ({sizes}); it is truncated into the prompt on every model "
            "turn. Compact /memory/ (summarize and prune scorecard.md, trim "
            "AGENTS.md to durable instructions) or raise "
            "AMBIENT_ANALYST_MEMORY_CHAR_BUDGET."
        )
        if strict:
            raise MemoryBudgetExceededError(message)
        logger.info(message)
    else:
        logger.info("Memory corpus is %d/%d characters (%s).", total, budget, sizes)
    return total


class BudgetedMemoryMiddleware(MemoryMiddleware):
    """`MemoryMiddleware` that caps the injected memory block at `char_budget` characters."""

    def __init__(self, *, char_budget: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.char_budget = char_budget

    def before_agent(
        self, state: Any, runtime: Any, config: RunnableConfig | None = None
    ) -> dict[str, Any] | None:
        """Load memory, then compact it to the budget before it can reach the prompt."""
        if config is None:
            config = get_config()
        return self._compact_update(super().before_agent(state, runtime, config))

    async def abefore_agent(
        self, state: Any, runtime: Any, config: RunnableConfig | None = None
    ) -> dict[str, Any] | None:
        """Async variant of `before_agent`."""
        if config is None:
            config = get_config()
        return self._compact_update(await super().abefore_agent(state, runtime, config))

    def _compact_update(self, update: dict[str, Any] | None) -> dict[str, Any] | None:
        if not update or "memory_contents" not in update:
            return update
        return {
            **update,
            "memory_contents": compact_memory_contents(
                update["memory_contents"], self.sources, self.char_budget
            ),
        }


if __name__ == "__main__":
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

    from types import SimpleNamespace

    seed = "".join(
        json.dumps({"i": i}, sort_keys=True) + "\n" for i in range(MEMORY_EVENTS_MAX_LINES + 50)
    )

    class HubDown:
        def __init__(self, identifier: str) -> None:
            self.identifier = identifier

        def read(self, *args, **kwargs):
            raise RuntimeError("Expecting value: line 1 column 1 (char 0)")

        def write(self, *args, **kwargs):
            raise RuntimeError("Expecting value: line 1 column 1 (char 0)")

    captured: list[str] = []

    class HubCapture:
        def __init__(self, identifier: str) -> None:
            self.identifier = identifier

        def read(self, *args, **kwargs):
            return SimpleNamespace(error=None, file_data=SimpleNamespace(content=seed))

        def write(self, file_path: str, content: str):
            captured.append(content)
            return SimpleNamespace(error=None)

    ContextHubBackend = HubCapture
    assert _append_memory_event({"i": "newest"}) is None
    written_lines = captured[-1].splitlines()
    assert len(written_lines) == MEMORY_EVENTS_MAX_LINES, len(written_lines)
    assert json.loads(written_lines[-1]) == {"i": "newest"}

    ContextHubBackend = HubDown
    assert "Expecting value" in (_append_memory_event({"i": "dropped"}) or "")
    hot_path = HotPathMemoryMiddleware({"tavily_search"})
    search_request = SimpleNamespace(tool_call={"name": "tavily_search", "args": {"q": "cpi"}})
    assert hot_path.wrap_tool_call(search_request, lambda _r: "search-result") == "search-result"
    SemanticPreferenceMiddleware()._record_preferences("I prefer concise answers.")

    budget = 4000
    sources = ["/memory/AGENTS.md", "/memory/scorecard.md"]
    corpus = {
        "/memory/AGENTS.md": "".join(f"instruction {i}\n" for i in range(1000)),
        "/memory/scorecard.md": "".join(f"| model {i} | score |\n" for i in range(1000)),
    }
    compacted = compact_memory_contents(corpus, sources, budget)
    assert sum(len(v) for v in compacted.values()) <= budget
    assert compacted["/memory/AGENTS.md"].startswith("instruction 0\n")
    assert compacted["/memory/scorecard.md"].rstrip().endswith("| model 999 | score |")
    assert all("MEMORY TRUNCATED" in value for value in compacted.values())
    assert all("`grep` and `read_file`" in value for value in compacted.values())
    small = {"/memory/AGENTS.md": "short\n", "/memory/scorecard.md": "also short\n"}
    assert compact_memory_contents(small, sources, budget) == small

    class Corpus:
        def download_files(self, paths):
            return [
                SimpleNamespace(content=corpus[path].encode("utf-8"), error=None)
                for path in paths
            ]

        async def adownload_files(self, paths):
            return self.download_files(paths)

    class CorpusDown:
        def download_files(self, paths):
            raise RuntimeError("Context Hub unavailable")

    assert check_memory_corpus(Corpus(), sources, budget) == sum(
        len(v) for v in corpus.values()
    )
    assert check_memory_corpus(Corpus(), sources, 10**9) > 0
    assert check_memory_corpus(CorpusDown(), sources, budget) == 0
    try:
        check_memory_corpus(Corpus(), sources, budget, strict=True)
    except MemoryBudgetExceededError:
        pass
    else:
        raise AssertionError("strict check_memory_corpus must raise when over budget")

    budgeted = BudgetedMemoryMiddleware(
        backend=Corpus(), sources=sources, char_budget=budget
    )
    update = budgeted._compact_update({"memory_contents": dict(corpus)})
    assert sum(len(v) for v in update["memory_contents"].values()) <= budget
    assert budgeted._compact_update(None) is None

    get_config = lambda: {}  # type: ignore[assignment]
    assert budgeted.before_agent({}, SimpleNamespace())["memory_contents"]

    import asyncio

    assert asyncio.run(budgeted.abefore_agent({}, SimpleNamespace()))["memory_contents"]

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

    class HubCorpus:
        def __init__(self, identifier: str) -> None:
            self.identifier = identifier

        def read(self, *args, **kwargs):
            return SimpleNamespace(
                error=None,
                file_data=SimpleNamespace(
                    content="# Memory\n\n## Learnings\n- old bullet\n\n"
                    "## Trusted sources\n- a source\n"
                ),
            )

    ContextHubBackend = HubCorpus

    def _edit(old: str, new: str) -> SimpleNamespace:
        return SimpleNamespace(
            tool_call={
                "name": "edit_file",
                "args": {
                    "file_path": "/memory/AGENTS.md",
                    "old_string": old,
                    "new_string": new,
                },
            }
        )

    duplicate = guard.wrap_tool_call(
        _edit("## Trusted sources\n", "## Learnings\n- new bullet\n"), lambda r: handled
    )
    assert "already exists" in duplicate, duplicate
    assert "## Learnings" in duplicate, duplicate
    assert (
        guard.wrap_tool_call(
            _edit("## Learnings\n", "## Learnings\n- new bullet\n"), lambda r: handled
        )
        is handled
    )
    assert (
        guard.wrap_tool_call(
            _edit("- old bullet", "- old bullet\n- new bullet"), lambda r: handled
        )
        is handled
    )
    cold_write = SimpleNamespace(
        tool_call={
            "name": "write_file",
            "args": {"file_path": COLD_MEMORY_PATH, "content": "## Learnings\n- x\n"},
        }
    )
    assert guard.wrap_tool_call(cold_write, lambda r: handled) is handled
    print("ok")
