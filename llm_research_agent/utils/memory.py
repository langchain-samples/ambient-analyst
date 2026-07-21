"""Optimistic-lock retry for the Context Hub memory backend.

The `/memory/` route is a shared Context Hub agent repo, so concurrent runs
committing to the same `AGENTS.md` race on the parent commit. When a write loses
that race the hub rejects it with an HTTP 409 ("parent commit does not match
latest"), which `ContextHubBackend` surfaces as an error result. Without a retry
the write is silently dropped and the agent may misreport a memory save as
successful.

`ConflictRetryBackend` wraps `ContextHubBackend` and, on a 409 conflict, re-reads
the latest commit and reapplies the edit against the fresh content (bounded
retries with small backoff). Non-conflict errors are surfaced unchanged. The
underlying backend re-reads the tree on the next call because it drops its cache
after a failed commit, so retrying simply re-invokes the operation against fresh
content and a fresh parent commit.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from deepagents.backends.protocol import (
    BackendProtocol,
    EditResult,
    WriteResult,
)

if TYPE_CHECKING:
    from deepagents.backends.context_hub import ContextHubBackend
    from deepagents.backends.protocol import (
        FileDownloadResponse,
        FileUploadResponse,
        GlobResult,
        GrepResult,
        LsResult,
        ReadResult,
    )

# Substrings that identify an optimistic-lock conflict (HTTP 409) as opposed to
# any other hub failure, which must be surfaced rather than retried.
_CONFLICT_MARKERS = (
    "parent commit does not match latest",
    "conflict",
    "409",
)


def _is_conflict(error: str | None) -> bool:
    """Return True if `error` describes a 409 optimistic-lock conflict."""
    if not error:
        return False
    lowered = error.lower()
    return any(marker in lowered for marker in _CONFLICT_MARKERS)


class ConflictRetryBackend(BackendProtocol):
    """Wraps a `ContextHubBackend`, retrying writes on 409 optimistic-lock conflicts.

    Only `write`/`edit` add retry behavior; every other operation delegates
    unchanged to the wrapped backend. Async variants inherit from
    `BackendProtocol`, which dispatches them onto these sync methods.
    """

    def __init__(
        self,
        inner: ContextHubBackend,
        *,
        max_retries: int = 3,
        backoff: float = 0.1,
    ) -> None:
        """Wrap `inner`, retrying conflicting commits up to `max_retries` times."""
        self._inner = inner
        self._max_retries = max_retries
        self._backoff = backoff

    def write(self, file_path: str, content: str) -> WriteResult:
        """Commit `content`, retrying on 409 conflicts against fresh content."""
        result = self._inner.write(file_path, content)
        for attempt in range(1, self._max_retries):
            if not _is_conflict(result.error):
                return result
            time.sleep(self._backoff * attempt)
            result = self._inner.write(file_path, content)
        return result

    def edit(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,  # noqa: FBT001, FBT002
    ) -> EditResult:
        """Apply an edit, retrying on 409 conflicts against fresh content."""
        result = self._inner.edit(file_path, old_string, new_string, replace_all)
        for attempt in range(1, self._max_retries):
            if not _is_conflict(result.error):
                return result
            time.sleep(self._backoff * attempt)
            result = self._inner.edit(file_path, old_string, new_string, replace_all)
        return result

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> ReadResult:
        """Delegate to the wrapped backend."""
        return self._inner.read(file_path, offset=offset, limit=limit)

    def ls(self, path: str = "/") -> LsResult:
        """Delegate to the wrapped backend."""
        return self._inner.ls(path)

    def grep(self, pattern: str, path: str | None = None, glob: str | None = None) -> GrepResult:
        """Delegate to the wrapped backend."""
        return self._inner.grep(pattern, path, glob)

    def glob(self, pattern: str, path: str | None = None) -> GlobResult:
        """Delegate to the wrapped backend."""
        return self._inner.glob(pattern, path)

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """Delegate to the wrapped backend."""
        return self._inner.upload_files(files)

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """Delegate to the wrapped backend."""
        return self._inner.download_files(paths)
