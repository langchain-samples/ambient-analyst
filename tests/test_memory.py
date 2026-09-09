"""Tests for Context Hub retry behavior."""

from __future__ import annotations

from deepagents.backends.protocol import EditResult, WriteResult

from agent.harness import hub
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
    assert not hub._is_retryable_result(EditResult(error="Error: File not found"))
    assert not hub._is_retryable_result(EditResult())
