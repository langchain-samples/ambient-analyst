"""Tests for Context Hub retry behavior."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from deepagents.backends.protocol import EditResult, WriteResult

from agent.harness import hub
from agent.harness import memory
from agent.harness.hub import ResilientHubBackend

_CONFLICT_ERROR = (
    "Hub unavailable: Conflict (parent commit does not match latest)"
)


class _FakeHubBackend:
    """Minimal stand-in that fails the first N edit/write calls with a 409."""

    def __init__(self, fail_times: int) -> None:
        self._fail_times = fail_times
        self.edit_calls = 0
        self.write_calls = 0

    def edit(self, file_path, old_string, new_string, replace_all=False):
        self.edit_calls += 1
        if self.edit_calls <= self._fail_times:
            return EditResult(error=_CONFLICT_ERROR)
        return EditResult(path=file_path, occurrences=1)

    def write(self, file_path, content):
        self.write_calls += 1
        if self.write_calls <= self._fail_times:
            return WriteResult(error=_CONFLICT_ERROR)
        return WriteResult(path=file_path)


class _DictHubBackend:
    def __init__(self, fail_times: int) -> None:
        self._fail_times = fail_times
        self.read_calls = 0
        self.edit_calls = 0
        self.write_calls = 0

    def read(self, file_path, offset=0, limit=2000):
        self.read_calls += 1
        if self.read_calls <= self._fail_times:
            return {"error": "HTTP 503"}
        return {"error": None, "file_data": {"content": b"ok"}}

    def edit(self, file_path, old_string, new_string, replace_all=False):
        self.edit_calls += 1
        if self.edit_calls <= self._fail_times:
            return {"error": _CONFLICT_ERROR}
        return {"error": None, "path": file_path, "occurrences": 1}

    def write(self, file_path, content):
        self.write_calls += 1
        if self.write_calls <= self._fail_times:
            return {"error": "HTTP 409"}
        return {"error": None, "path": file_path}


def test_edit_retries_on_conflict_then_succeeds(monkeypatch):
    monkeypatch.setattr(hub, "BACKOFF_SECONDS", 0)
    inner = _FakeHubBackend(fail_times=1)
    backend = ResilientHubBackend(inner, max_retries=3)

    result = backend.edit("/memory/AGENTS.md", "old", "new")

    assert result.error is None
    assert result.path == "/memory/AGENTS.md"
    assert inner.edit_calls == 2


def test_write_retries_on_conflict_then_succeeds(monkeypatch):
    monkeypatch.setattr(hub, "BACKOFF_SECONDS", 0)
    inner = _FakeHubBackend(fail_times=1)
    backend = ResilientHubBackend(inner, max_retries=3)

    result = backend.write("/memory/AGENTS.md", "content")

    assert result.error is None
    assert inner.write_calls == 2


def test_dict_results_retry_like_protocol_objects(monkeypatch):
    monkeypatch.setattr(hub, "BACKOFF_SECONDS", 0)
    inner = _DictHubBackend(fail_times=1)
    backend = ResilientHubBackend(inner, max_retries=3)

    file_data = backend.read("/memory/AGENTS.md").get("file_data")
    assert hub.hub_result_content(file_data) == "ok"
    assert backend.edit("/memory/AGENTS.md", "old", "new")["error"] is None
    assert backend.write("/memory/AGENTS.md", "content")["error"] is None
    assert inner.read_calls == 2
    assert inner.edit_calls == 2
    assert inner.write_calls == 2


def test_edit_gives_up_after_max_retries(monkeypatch):
    monkeypatch.setattr(hub, "BACKOFF_SECONDS", 0)
    inner = _FakeHubBackend(fail_times=99)
    backend = ResilientHubBackend(inner, max_retries=3)

    result = backend.edit("/memory/AGENTS.md", "old", "new")

    assert result.error == _CONFLICT_ERROR
    assert inner.edit_calls == 3


def test_non_conflict_error_is_not_retried():
    class _AlwaysMissing:
        def __init__(self):
            self.edit_calls = 0

        def edit(self, *args, **kwargs):
            self.edit_calls += 1
            return EditResult(error="Error: File '/memory/AGENTS.md' not found")

    inner = _AlwaysMissing()
    backend = ResilientHubBackend(inner, max_retries=3)

    result = backend.edit("/memory/AGENTS.md", "old", "new")

    assert "not found" in result.error
    assert inner.edit_calls == 1


def test_retryable_result_markers():
    assert hub._is_retryable_result(EditResult(error=_CONFLICT_ERROR))
    assert hub._is_retryable_result(WriteResult(error="HTTP 409"))
    assert hub._is_retryable_result({"error": "HTTP 503"})
    assert not hub._is_retryable_result(EditResult(error="Error: File not found"))
    assert not hub._is_retryable_result(EditResult())
    assert not hub._is_retryable_result({"error": None})


def test_hot_path_async_memory_append_runs_off_event_loop(monkeypatch):
    thread_has_loop = None

    def _capture(_event):
        nonlocal thread_has_loop
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            thread_has_loop = False
        else:
            thread_has_loop = True

    async def _handler(_request):
        return SimpleNamespace(status="success")

    monkeypatch.setattr(memory, "_append_memory_event", _capture)
    request = SimpleNamespace(tool_call={"name": "tavily_search", "args": {"q": "cpi"}})
    middleware = memory.HotPathMemoryMiddleware({"tavily_search"})

    result = asyncio.run(middleware.awrap_tool_call(request, _handler))

    assert result.status == "success"
    assert thread_has_loop is False


def test_append_memory_event_reads_dict_file_data(monkeypatch):
    captured = []

    class _Hub:
        def __init__(self, _identifier):
            pass

        def read(self, _path):
            return {"error": None, "file_data": {"content": '{"i": "old"}\n'}}

        def write(self, _path, content):
            captured.append(content)
            return {"error": None}

    monkeypatch.setattr(memory, "ContextHubBackend", _Hub)

    assert memory._append_memory_event({"i": "new"}) is None
    assert captured[-1].splitlines() == ['{"i": "old"}', '{"i": "new"}']


def _memory_edit_turn(tool_content, status="success"):
    from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

    return [
        HumanMessage(content="What would turn a refinancing problem into a default cycle?"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "edit_file",
                    "args": {"file_path": "/memory/AGENTS.md", "old_string": "a", "new_string": "b"},
                    "id": "edit-1",
                }
            ],
        ),
        ToolMessage(content=tool_content, tool_call_id="edit-1", name="edit_file", status=status),
    ]


def _guarded_final(messages, answer):
    from langchain_core.messages import AIMessage

    response = SimpleNamespace(result=[AIMessage(content=answer)])
    guard = memory.MemorySaveClaimGuardMiddleware()
    return guard.wrap_model_call(SimpleNamespace(messages=messages), lambda _r: response)


_SAVE_CLAIM = "**Memory:** I saved the default-cycle framework to `/memory/AGENTS.md`."


def test_save_claim_guard_flags_claim_when_memory_edit_errored():
    messages = _memory_edit_turn("Error: String not found in file: 'x'", status="error")

    out = _guarded_final(messages, _SAVE_CLAIM).result[-1].content

    assert out.startswith(_SAVE_CLAIM)
    assert memory.UNVERIFIED_SAVE_NOTICE in out


def test_save_claim_guard_flags_claim_when_turn_made_no_tool_calls():
    from langchain_core.messages import HumanMessage

    earlier = _memory_edit_turn("Successfully replaced 1 instance(s) of the string in '/memory/AGENTS.md'")
    messages = [*earlier, HumanMessage(content="How would you stress-test a portfolio?")]
    answer = "I saved the durable stress-testing framework in memory; no personal data was stored."

    out = _guarded_final(messages, answer).result[-1].content

    assert memory.UNVERIFIED_SAVE_NOTICE in out


def test_save_claim_guard_allows_claim_backed_by_successful_memory_write():
    messages = _memory_edit_turn("Successfully replaced 1 instance(s) of the string in '/memory/AGENTS.md'")

    out = _guarded_final(messages, _SAVE_CLAIM).result[-1].content

    assert out == _SAVE_CLAIM


def test_save_claim_guard_ignores_honest_and_unrelated_statements():
    assert not memory.claims_memory_save(
        "Nothing was saved; the attempted memory update did not match the file structure."
    )
    assert not memory.claims_memory_save("SK Hynix added share in memory as HBM demand rose.")
    assert memory.claims_memory_save("Memory update: AGENTS.md updated with the stagflation framework.")
