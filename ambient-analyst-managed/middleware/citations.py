"""Citation grounding guard.

The Hub system prompt requires every inline citation to come from a tool result
retrieved in the same session. That rule is prompt-only, and the model violates
it by emitting plausible-looking URLs on real domains — often a one-word mutation
of a URL it actually retrieved — attached to a hard figure. This middleware
enforces the rule deterministically: it accumulates every URL observed in tool
results during the run and relabels any URL in the final answer that was never
retrieved.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from urllib.parse import unquote

from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from langchain.agents.middleware.types import ModelRequest, ModelResponse

_URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`\\|]+")
_UNVERIFIED = "(source not retrieved this session)"
# PIIRedactionMiddleware turns digit runs inside URLs into [REDACTED_*] markers;
# those URLs can no longer be matched against the retrieved set, so leave them be.
_REDACTED_RE = re.compile(r"\[redacted_", re.I)
# Shortest trailing path segment distinctive enough to match against raw evidence.
_MIN_SLUG_LEN = 15


def _normalize(url: str) -> str:
    """Scheme/host/query-insensitive form used for retrieved-vs-cited matching."""
    text = unquote(url).strip().lower()
    text = re.sub(r"^https?://", "", text)
    text = re.sub(r"^www\.", "", text)
    text = text.split("#", 1)[0].split("?", 1)[0]
    return text.rstrip("/.,;:!)]}\"'")


def _text(content: str | list) -> str:
    """Flatten a message's content, handling plain-string and content-block forms."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "\n".join(parts)
    return ""


def _grounded(cited: str, retrieved: set[str], evidence: str) -> bool:
    """True if `cited` matches a retrieved URL, or its distinctive slug is in the evidence."""
    normalized = _normalize(cited)
    if any(
        normalized == r or r.startswith(normalized) or normalized.startswith(r)
        for r in retrieved
    ):
        return True
    slug = normalized.rsplit("/", 1)[-1]
    return len(slug) >= _MIN_SLUG_LEN and slug in evidence


def _scrub_text(text: str, retrieved: set[str], evidence: str) -> str:
    """Replace every ungrounded URL in `text` with the unverified marker."""

    def replace(match: re.Match[str]) -> str:
        url = match.group(0)
        if _REDACTED_RE.search(url) or _grounded(url, retrieved, evidence):
            return url
        return _UNVERIFIED

    return _URL_RE.sub(replace, text)


def _scrub_content(content: str | list, retrieved: set[str], evidence: str) -> str | list:
    """Scrub a message's content, handling plain-string and content-block forms."""
    if isinstance(content, str):
        return _scrub_text(content, retrieved, evidence)
    if isinstance(content, list):
        out = []
        for block in content:
            if isinstance(block, str):
                out.append(_scrub_text(block, retrieved, evidence))
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                out.append({**block, "text": _scrub_text(block["text"], retrieved, evidence)})
            else:
                out.append(block)
        return out
    return content


def _citation_evidence(messages: list[BaseMessage]) -> tuple[set[str], str]:
    """Return the URLs and raw tool evidence visible in this model request."""
    evidence: list[str] = []
    retrieved: set[str] = set()
    for message in messages:
        if isinstance(message, ToolMessage):
            body = _text(message.content)
            evidence.append(unquote(body).lower())
            retrieved.update(_normalize(u) for u in _URL_RE.findall(body))
    return retrieved, "\n".join(evidence)


class CitationGuardMiddleware(AgentMiddleware):
    """Relabel final-answer citations whose URLs were never retrieved this session."""

    def _scrub(
        self, response: ModelResponse, retrieved: set[str], evidence: str
    ) -> ModelResponse:
        """Rewrite ungrounded URLs in the final (tool-call-free) AI message."""
        messages = getattr(response, "result", None) or []
        if not messages or not isinstance(messages[-1], AIMessage):
            return response
        final = messages[-1]
        if final.tool_calls:
            return response
        scrubbed = _scrub_content(final.content, retrieved, evidence)
        if scrubbed == final.content:
            return response
        messages[-1] = final.model_copy(update={"content": scrubbed})
        return response

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        retrieved, evidence = _citation_evidence(request.messages)
        return self._scrub(handler(request), retrieved, evidence)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        retrieved, evidence = _citation_evidence(request.messages)
        return self._scrub(await handler(request), retrieved, evidence)


if __name__ == "__main__":
    from types import SimpleNamespace

    real = "https://www.example.org/reports/trends-international-trade-2025"
    fake = "https://www.example.org/reports/trends-in-international-trade-2025"
    redacted = "https://data.example.gov/series/[REDACTED_PHONE]"

    guard = CitationGuardMiddleware()
    retrieved, evidence = _citation_evidence(
        [
            ToolMessage(content=f"Search hit: {real} — trade grew 3.1%.", tool_call_id="1"),
            ToolMessage(
                content=[{"type": "text", "text": f"Series page {redacted}"}],
                tool_call_id="2",
            ),
        ]
    )
    answer = f"Trade grew 3.1% ([source]({real})) and tariffs fell ([source]({fake})). Series: {redacted}"
    response = SimpleNamespace(result=[AIMessage(content=answer)])
    guard._scrub(response, retrieved, evidence)
    out = response.result[-1].content

    assert real in out, out
    assert fake not in out, out
    assert _UNVERIFIED in out, out
    assert redacted in out, out

    # A tool-calling turn is not the final answer and must be left alone.
    mid = AIMessage(
        content=f"Checking {fake}",
        tool_calls=[{"name": "search", "args": {"q": "trade"}, "id": "3"}],
    )
    midresponse = SimpleNamespace(result=[mid])
    guard._scrub(midresponse, retrieved, evidence)
    assert midresponse.result[-1].content == f"Checking {fake}"

    def _answer(_request):
        return SimpleNamespace(result=[AIMessage(content=f"Leaked? {real}")])

    clean = guard.wrap_model_call(SimpleNamespace(messages=[]), _answer)
    assert real not in clean.result[-1].content, clean.result[-1].content

    print("citation guard self-test passed")
