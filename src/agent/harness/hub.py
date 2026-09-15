"""Keep Context Hub transport failures inside the tool result."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
import logging
import time
from typing import Any

from deepagents.backends.protocol import EditResult, ReadResult, WriteResult

logger = logging.getLogger(__name__)

BACKOFF_SECONDS = 0.5

_RETRYABLE_MARKERS = (
    "conflict",
    "409",
    "500",
    "502",
    "503",
    "504",
    "expecting value",
    "timed out",
    "timeout",
    "connection",
)

# Only ever applied to reads of the mounted memory files: a full-file write from
# a concurrent session leaves the path briefly missing, so a not-found read there
# is a race to retry rather than a hard error. An edit anchor that is "not found"
# is a real failure and must stay immediate.
_NOT_FOUND_MARKERS = ("not found", "404")


def _is_not_found_text(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _NOT_FOUND_MARKERS)


def _memory_key(file_path: str) -> str:
    """Normalize a path so `/memory/AGENTS.md` and `/AGENTS.md` compare equal."""
    trimmed = file_path.lstrip("/")
    return trimmed[len("memory/") :] if trimmed.startswith("memory/") else trimmed


def _is_not_found(exc: BaseException) -> bool:
    while exc:
        if getattr(exc, "status_code", None) == 404:
            return True
        if _is_not_found_text(f"{type(exc).__name__}: {exc}"):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


def _is_not_found_result(result: Any) -> bool:
    error = hub_result_value(result, "error")
    return isinstance(error, str) and _is_not_found_text(error)


def _is_retryable(exc: BaseException) -> bool:
    while exc:
        if getattr(exc, "status_code", None) in {409, 500, 502, 503, 504}:
            return True
        text = f"{type(exc).__name__}: {exc}".lower()
        if any(marker in text for marker in _RETRYABLE_MARKERS):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


def _is_retryable_result(result: Any) -> bool:
    error = hub_result_value(result, "error")
    return isinstance(error, str) and any(
        marker in error.lower() for marker in _RETRYABLE_MARKERS
    )


def hub_result_value(result: Any, key: str) -> Any:
    return result.get(key) if isinstance(result, dict) else getattr(result, key, None)


def hub_result_content(result: Any) -> str:
    content = hub_result_value(result, "content")
    return content.decode("utf-8") if isinstance(content, bytes) else (content or "")


class ResilientHubBackend:
    """Wraps a Context Hub backend so failed pushes come back as result errors."""

    def __init__(
        self,
        backend: Any,
        max_retries: int = 3,
        retry_missing_paths: Iterable[str] = (),
    ) -> None:
        self.backend = backend
        self.max_retries = max(1, max_retries)
        self.retry_missing_paths = {_memory_key(path) for path in retry_missing_paths}

    def __getattr__(self, name: str) -> Any:
        return getattr(self.backend, name)

    def _failure(self, operation: str, message: str, result_type: type) -> Any:
        logger.warning(
            "Context Hub %s failed (%s); reporting it as a tool-level error.",
            operation,
            message,
        )
        return result_type(error=f"Context Hub {operation} failed: {message}")

    def _retry_missing(self, file_path: Any) -> bool:
        return (
            isinstance(file_path, str)
            and _memory_key(file_path) in self.retry_missing_paths
        )

    def _call(
        self,
        operation: str,
        result_type: type,
        *args: Any,
        retry_missing: bool = False,
        **kwargs: Any,
    ) -> Any:
        fn = getattr(self.backend, operation)
        message = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                result = fn(*args, **kwargs)
                if attempt >= self.max_retries or not (
                    _is_retryable_result(result)
                    or (retry_missing and _is_not_found_result(result))
                ):
                    return result
            except Exception as exc:  # noqa: BLE001 — a Hub outage must not end the run
                message = f"{type(exc).__name__}: {exc}"
                if attempt >= self.max_retries or not (
                    _is_retryable(exc) or (retry_missing and _is_not_found(exc))
                ):
                    break
            time.sleep(BACKOFF_SECONDS * attempt)
        return self._failure(operation, message, result_type)

    async def _acall(
        self,
        operation: str,
        result_type: type,
        *args: Any,
        retry_missing: bool = False,
        **kwargs: Any,
    ) -> Any:
        fn = getattr(self.backend, operation)
        message = ""
        for attempt in range(1, self.max_retries + 1):
            try:
                result = await fn(*args, **kwargs)
                if attempt >= self.max_retries or not (
                    _is_retryable_result(result)
                    or (retry_missing and _is_not_found_result(result))
                ):
                    return result
            except Exception as exc:  # noqa: BLE001 — a Hub outage must not end the run
                message = f"{type(exc).__name__}: {exc}"
                if attempt >= self.max_retries or not (
                    _is_retryable(exc) or (retry_missing and _is_not_found(exc))
                ):
                    break
            await asyncio.sleep(BACKOFF_SECONDS * attempt)
        return self._failure(operation, message, result_type)

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> ReadResult:
        return self._call(
            "read",
            ReadResult,
            file_path,
            offset,
            limit,
            retry_missing=self._retry_missing(file_path),
        )

    def write(self, file_path: str, content: str) -> WriteResult:
        return self._call("write", WriteResult, file_path, content)

    def edit(
        self, file_path: str, old_string: str, new_string: str, replace_all: bool = False
    ) -> EditResult:
        return self._call("edit", EditResult, file_path, old_string, new_string, replace_all)

    async def aread(self, file_path: str, offset: int = 0, limit: int = 2000) -> ReadResult:
        return await self._acall(
            "aread",
            ReadResult,
            file_path,
            offset,
            limit,
            retry_missing=self._retry_missing(file_path),
        )

    async def awrite(self, file_path: str, content: str) -> WriteResult:
        return await self._acall("awrite", WriteResult, file_path, content)

    async def aedit(
        self, file_path: str, old_string: str, new_string: str, replace_all: bool = False
    ) -> EditResult:
        return await self._acall("aedit", EditResult, file_path, old_string, new_string, replace_all)


if __name__ == "__main__":
    from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError

    class HubDown:
        calls = 0

        def _boom(self, *args, **kwargs):
            HubDown.calls += 1
            raise RequestsJSONDecodeError("Expecting value", "", 0)

        read = write = edit = _boom

        async def _aboom(self, *args, **kwargs):
            return self._boom()

        aread = awrite = aedit = _aboom

    class NotFound:
        def read(self, *args, **kwargs):
            raise ValueError("no such file")

    resilient = ResilientHubBackend(HubDown(), max_retries=2)
    assert resilient.read("hot-path-events.jsonl").error
    assert resilient.write("hot-path-events.jsonl", "{}\n").error
    assert resilient.edit("AGENTS.md", "old", "new").error
    assert asyncio.run(resilient.aread("AGENTS.md")).error
    assert asyncio.run(resilient.awrite("AGENTS.md", "x")).error
    assert asyncio.run(resilient.aedit("AGENTS.md", "old", "new")).error
    assert HubDown.calls == 12, HubDown.calls

    assert _is_retryable(RequestsJSONDecodeError("Expecting value", "", 0))
    assert _is_retryable_result({"error": "HTTP 409"})
    assert hub_result_value({"file_data": {"content": "x"}}, "file_data") == {
        "content": "x"
    }
    assert hub_result_content({"content": b"x"}) == "x"
    assert not _is_retryable(ValueError("old_string not found"))
    assert ResilientHubBackend(NotFound(), max_retries=3).read("AGENTS.md").error
    assert ResilientHubBackend(HubDown()).max_retries == 3

    class MissingThenPresent:
        calls = 0

        def read(self, *args, **kwargs):
            MissingThenPresent.calls += 1
            if MissingThenPresent.calls == 1:
                return ReadResult(error="Error: File '/AGENTS.md' not found")
            return {"error": None, "file_data": {"content": "recovered"}}

    BACKOFF_SECONDS = 0
    memory_backend = ResilientHubBackend(
        MissingThenPresent(), max_retries=3, retry_missing_paths=["/memory/AGENTS.md"]
    )
    assert hub_result_content(memory_backend.read("/AGENTS.md")["file_data"]) == "recovered"
    assert MissingThenPresent.calls == 2
    assert not _is_not_found_result(ReadResult(error="HTTP 409"))
    assert _memory_key("/memory/AGENTS.md") == _memory_key("/AGENTS.md") == "AGENTS.md"
    print("ok")
