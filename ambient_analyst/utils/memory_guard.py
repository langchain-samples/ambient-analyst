"""Append/patch-only guard for the Context Hub memory route.

`write_file` submits a whole-file body, so it can only be safe when the model
holds the complete current file. Memory (`/memory/AGENTS.md`,
`/memory/scorecard.md`) is a growing corpus that the agent reads in bounded
windows (`read_file` with an `offset`/`limit`, or `grep`), so a body
regenerated from context silently drops everything the model never read — we
observed a 60k-character memory file about to be replaced by a ~50k-character
rewrite after a 120-line read. Appending a durable note is an `edit_file`
operation: anchor on a unique string and patch in place.

This backend keeps the memory route readable and editable but refuses the
whole-file write, returning guidance that steers the model to `edit_file`.
"""

from __future__ import annotations

from deepagents.backends.context_hub import ContextHubBackend
from deepagents.backends.protocol import WriteResult
from langsmith.utils import LangSmithError

# Even when full writes are enabled, refuse a body that loses more than this
# fraction of the stored file.
MAX_SHRINK_FRACTION = 0.02

_WRITE_DISABLED = (
    "Error: write_file is disabled for {mount}. Use edit_file with a unique "
    "old_string anchor to append or patch {path} instead — write_file replaces "
    "the whole file and silently deletes anything not in the submitted body."
)

_WRITE_SHRINKS = (
    "Error: refusing write_file on {path}: the submitted body is {delta} bytes "
    "shorter than the stored {stored} bytes, so it would delete memory that was "
    "never read. Use edit_file with a unique old_string anchor to append or "
    "patch this file."
)


class AppendOnlyContextHubBackend(ContextHubBackend):
    """Context Hub backend that refuses destructive whole-file writes."""

    def __init__(
        self,
        identifier: str,
        *,
        mount: str = "/memory/",
        allow_full_write: bool = False,
        **kwargs,
    ) -> None:
        """Wrap `ContextHubBackend`, blocking `write` on the given mount."""
        super().__init__(identifier, **kwargs)
        self._mount = mount
        self._allow_full_write = allow_full_write

    def write(self, file_path: str, content: str) -> WriteResult:
        """Refuse whole-file writes; the agent must patch memory with `edit`."""
        # CompositeBackend strips the route prefix before delegating, so
        # re-attach the mount to name the path the model actually asked for.
        path = f"{self._mount}{file_path.lstrip('/')}"
        if not self._allow_full_write:
            return WriteResult(error=_WRITE_DISABLED.format(mount=self._mount, path=path))

        try:
            stored = self._ensure_cache().get(self._strip_prefix(file_path))
        except LangSmithError as exc:
            return WriteResult(error=f"Hub unavailable: {exc}")
        if stored is not None:
            delta = len(stored) - len(content)
            if delta > MAX_SHRINK_FRACTION * len(stored):
                return WriteResult(
                    error=_WRITE_SHRINKS.format(path=path, delta=delta, stored=len(stored))
                )
        return super().write(file_path, content)


if __name__ == "__main__":
    import uuid

    from langsmith.schemas import AgentContext, FileEntry

    STORED = "# Ambient Analyst Memory\n" + "".join(f"- note {i}\n" for i in range(500))

    class FakeClient:
        def __init__(self) -> None:
            self.files = {"AGENTS.md": STORED}
            self.pushes = 0

        def pull_agent(self, identifier: str) -> AgentContext:
            return AgentContext(
                commit_id=uuid.uuid4(),
                commit_hash="abcd1234",
                files={path: FileEntry(type="file", content=text) for path, text in self.files.items()},
            )

        def push_agent(self, identifier: str, *, files, parent_commit=None) -> str:
            self.pushes += 1
            for path, entry in files.items():
                if entry is None:
                    self.files.pop(path, None)
                else:
                    self.files[path] = entry.content
            return "https://smith.langchain.com/context/ambient-analyst-memory/beef1234"

    # write_file is refused with edit_file guidance, and nothing is committed.
    client = FakeClient()
    backend = AppendOnlyContextHubBackend("-/ambient-analyst-memory", client=client)
    result = backend.write("/AGENTS.md", "# Ambient Analyst Memory\n- only what I remembered\n")
    assert result.error is not None, result
    assert "write_file is disabled for /memory/" in result.error, result.error
    assert "edit_file" in result.error, result.error
    assert client.pushes == 0
    assert client.files["AGENTS.md"] == STORED

    # edit_file still appends normally.
    edit = backend.edit("/AGENTS.md", "- note 499\n", "- note 499\n- durable learning\n")
    assert edit.error is None, edit.error
    assert edit.occurrences == 1, edit
    assert "- durable learning\n" in client.files["AGENTS.md"]
    assert client.files["AGENTS.md"].startswith(STORED[: len(STORED) - len("- note 499\n")])

    # Defense in depth: an allowed full write still refuses a shrinking body.
    permissive = AppendOnlyContextHubBackend(
        "-/ambient-analyst-memory", client=FakeClient(), allow_full_write=True
    )
    shrunk = permissive.write("/AGENTS.md", STORED[: int(len(STORED) * 0.9)])
    assert shrunk.error is not None and "shorter than the stored" in shrunk.error, shrunk
    grown = permissive.write("/AGENTS.md", STORED + "- durable learning\n")
    assert grown.error is None, grown.error

    print("ok")
