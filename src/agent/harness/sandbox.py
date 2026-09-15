"""Sandbox path helpers and the lazily mounted /analysis/ route."""

from __future__ import annotations

import logging
import posixpath
from typing import Any, Callable

from deepagents.backends.protocol import (
    DeleteResult,
    EditResult,
    GlobResult,
    GrepResult,
    LsResult,
    ReadResult,
    WriteResult,
)

logger = logging.getLogger(__name__)

SANDBOX_UNAVAILABLE_ERROR = (
    "Error: the analysis sandbox is unavailable, so /analysis/ cannot be read or "
    "written. Do not publish an artifact; answer the user in text instead."
)


def analysis_path(path: str) -> str:
    raw = path.strip()
    if not raw:
        return "/analysis"
    if not raw.startswith("/"):
        raw = f"/analysis/{raw}"
    normalized = posixpath.normpath("/" + raw.lstrip("/"))
    if normalized != "/analysis" and not normalized.startswith("/analysis/"):
        raise ValueError("Data modeling artifacts must live under /analysis/")
    return normalized


class AnalysisSandbox:
    """Mounts the analysis sandbox on first use and retries until the mount works."""

    def __init__(
        self,
        mount: Callable[[], Any],
        backend_factory: Callable[[Any], Any],
    ) -> None:
        self._mount = mount
        self._backend_factory = backend_factory
        self._sandbox: Any = None
        self._backend: Any = None

    def sandbox(self) -> Any:
        """Return the mounted sandbox, re-attempting the mount while it is down."""
        if self._sandbox is None:
            try:
                self._sandbox = self._mount()
            except Exception as exc:  # noqa: BLE001 — a sandbox outage must not end the run
                logger.warning(
                    "Analysis sandbox unavailable (%s); /analysis/ is degraded and "
                    "the mount will be retried on the next use.",
                    exc,
                )
                return None
            self._backend = self._backend_factory(self._sandbox)
        return self._sandbox

    @property
    def available(self) -> bool:
        return self.sandbox() is not None

    def _routed(self) -> Any:
        self.sandbox()
        return self._backend

    # File operations. This backend stays registered on the /analysis/ route even
    # while the mount is down, so writes surface the outage instead of falling
    # through to the composite default and reporting a success that published
    # nothing. Searches stay empty rather than erroring: grep/glob fan out across
    # every route, and one unmounted route must not fail searches of the others.
    def ls(self, path: str) -> LsResult:
        backend = self._routed()
        if backend is None:
            return LsResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return backend.ls(path)

    async def als(self, path: str) -> LsResult:
        backend = self._routed()
        if backend is None:
            return LsResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return await backend.als(path)

    def read(self, file_path: str, offset: int = 0, limit: int = 2000) -> ReadResult:
        backend = self._routed()
        if backend is None:
            return ReadResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return backend.read(file_path, offset, limit)

    async def aread(self, file_path: str, offset: int = 0, limit: int = 2000) -> ReadResult:
        backend = self._routed()
        if backend is None:
            return ReadResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return await backend.aread(file_path, offset, limit)

    def write(self, file_path: str, content: str) -> WriteResult:
        backend = self._routed()
        if backend is None:
            return WriteResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return backend.write(file_path, content)

    async def awrite(self, file_path: str, content: str) -> WriteResult:
        backend = self._routed()
        if backend is None:
            return WriteResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return await backend.awrite(file_path, content)

    def edit(
        self, file_path: str, old_string: str, new_string: str, replace_all: bool = False
    ) -> EditResult:
        backend = self._routed()
        if backend is None:
            return EditResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return backend.edit(file_path, old_string, new_string, replace_all=replace_all)

    async def aedit(
        self, file_path: str, old_string: str, new_string: str, replace_all: bool = False
    ) -> EditResult:
        backend = self._routed()
        if backend is None:
            return EditResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return await backend.aedit(file_path, old_string, new_string, replace_all=replace_all)

    def delete(self, file_path: str) -> DeleteResult:
        backend = self._routed()
        if backend is None:
            return DeleteResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return backend.delete(file_path)

    async def adelete(self, file_path: str) -> DeleteResult:
        backend = self._routed()
        if backend is None:
            return DeleteResult(error=SANDBOX_UNAVAILABLE_ERROR)
        return await backend.adelete(file_path)

    def grep(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
        *,
        max_count: int | None = None,
    ) -> GrepResult:
        backend = self._routed()
        if backend is None:
            return GrepResult(matches=[])
        return backend.grep(pattern, path, glob, max_count=max_count)

    async def agrep(
        self,
        pattern: str,
        path: str | None = None,
        glob: str | None = None,
        *,
        max_count: int | None = None,
    ) -> GrepResult:
        backend = self._routed()
        if backend is None:
            return GrepResult(matches=[])
        return await backend.agrep(pattern, path, glob, max_count=max_count)

    def glob(self, pattern: str, path: str | None = None) -> GlobResult:
        backend = self._routed()
        if backend is None:
            return GlobResult(matches=[])
        return backend.glob(pattern, path)

    async def aglob(self, pattern: str, path: str | None = None) -> GlobResult:
        backend = self._routed()
        if backend is None:
            return GlobResult(matches=[])
        return await backend.aglob(pattern, path)
