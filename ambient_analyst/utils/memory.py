"""Budgeted memory: keep the always-on memory preamble from growing without bound.

The `/memory/` Context Hub repo is written back at runtime by the
continuous-learning loop, so `AGENTS.md` and `scorecard.md` grow every session.
deepagents' `MemoryMiddleware` loads those files once per request (in
`before_agent`) but re-serializes the whole loaded block into the system prompt
on *every* model turn (`wrap_model_call`) — the system prompt has to be resent
with each call, so there is no before-agent-only injection mode to switch to.
That makes the corpus size a fixed per-turn tax: at ~261KB mounted (~65K tokens)
a single request paid a ~83K-token floor and multiplied it by 4-14 turns, which
is what the traces on this issue show.

`BudgetedMemoryMiddleware` bounds that tax. It caps the loaded corpus at a
character budget, trimming at line boundaries and preferring the head of the
first source (`AGENTS.md`, the durable instructions) over the tail of the
append-only logs that follow it. Whatever is elided is replaced by an explicit
marker telling the agent that memory was truncated and that `grep`/`read_file`
over `/memory/` will retrieve the rest — the content stays reachable on demand
instead of being silently dropped.

`check_memory_corpus` is the startup guard: it reports the mounted size and
complains (or raises, under `strict`) when the corpus outgrows the budget, so
unbounded growth surfaces in CI rather than in production token spend.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from deepagents.middleware.memory import MemoryMiddleware

if TYPE_CHECKING:
    from collections.abc import Sequence

    from deepagents.backends.protocol import BackendProtocol
    from langchain_core.runnables import RunnableConfig
    from langgraph.runtime import Runtime

logger = logging.getLogger(__name__)

_TRUNCATION_NOTICE = (
    "[MEMORY TRUNCATED: {elided} of {total} characters of {path} were elided to "
    "stay within the {budget}-character memory budget, so what you see above is "
    "incomplete. Do not assume the omitted content does not exist — use the "
    "`grep` and `read_file` tools against `{path}` to retrieve anything you need "
    "from the part that is not shown.]"
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
    contents: dict[str, str],
    sources: Sequence[str],
    budget: int,
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
            _TRUNCATION_NOTICE.format(
                elided=len(raw), total=len(raw), path=path, budget=budget
            )
        )
        kept = _keep_lines(raw, allowance - reserve - 1, from_end=from_end)
        notice = _TRUNCATION_NOTICE.format(
            elided=len(raw) - len(kept), total=len(raw), path=path, budget=budget
        )
        compacted[path] = f"{notice}\n{kept}" if from_end else f"{kept}\n{notice}"
        logger.warning(
            "Memory source %s truncated from %d to %d characters "
            "(%d-character budget); agent must grep/read_file for the rest.",
            path,
            len(raw),
            len(kept),
            budget,
        )
    return compacted


def check_memory_corpus(
    backend: BackendProtocol,
    sources: Sequence[str],
    budget: int,
    *,
    strict: bool = False,
) -> int:
    """Log the mounted memory size and flag (or raise on) a corpus over `budget`."""
    sizes: dict[str, int] = {}
    try:
        responses = backend.download_files(list(sources))
    except Exception as exc:  # noqa: BLE001 — never block startup on the check itself
        logger.warning(
            "Could not measure memory corpus (%s); skipping budget check.", exc
        )
        return 0
    for path, response in zip(sources, responses, strict=True):
        if response.content is not None:
            sizes[path] = len(response.content.decode("utf-8"))
    total = sum(sizes.values())
    if total > budget:
        message = (
            f"Memory corpus is {total} characters, over the {budget}-character budget "
            f"({sizes}); it will be truncated into the prompt every model turn. "
            "Compact /memory/ (summarize and prune scorecard.md, trim AGENTS.md to "
            "durable instructions) or raise AMBIENT_ANALYST_MEMORY_CHAR_BUDGET."
        )
        if strict:
            raise MemoryBudgetExceededError(message)
        logger.error(message)
    else:
        logger.info("Memory corpus is %d/%d characters (%s).", total, budget, sizes)
    return total


class BudgetedMemoryMiddleware(MemoryMiddleware):
    """`MemoryMiddleware` that caps the injected memory block at `char_budget` characters."""

    def __init__(self, *, char_budget: int, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.char_budget = char_budget

    def before_agent(
        self, state: Any, runtime: Runtime, config: RunnableConfig
    ) -> dict[str, Any] | None:
        """Load memory, then compact it to the budget before it reaches the prompt."""
        update = super().before_agent(state, runtime, config)
        return self._compact_update(update)

    async def abefore_agent(
        self, state: Any, runtime: Runtime, config: RunnableConfig
    ) -> dict[str, Any] | None:
        """Async variant of `before_agent`."""
        update = await super().abefore_agent(state, runtime, config)
        return self._compact_update(update)

    def _compact_update(self, update: dict[str, Any] | None) -> dict[str, Any] | None:
        if not update or "memory_contents" not in update:
            return update
        return {
            **update,
            "memory_contents": compact_memory_contents(
                update["memory_contents"], self.sources, self.char_budget
            ),
        }
