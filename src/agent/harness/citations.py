"""Citation grounding guard.

The Hub system prompt requires every inline citation to come from a tool result
retrieved in the same session. That rule is prompt-only, and the model violates
it by emitting plausible-looking URLs on real domains — often a one-word mutation
of a URL it actually retrieved — attached to a hard figure. This middleware
enforces the rule deterministically: it accumulates every URL observed in tool
results during the run and relabels any URL in the final answer that was never
retrieved. It also labels figures placed next to a retrieved citation when that
source's retrieved text does not contain them, since a real URL does not verify
a number its content never stated.
"""

from __future__ import annotations

import json
import re
from decimal import ROUND_HALF_UP, Decimal
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
_UNVERIFIED_FIGURE = "(from background knowledge, unverified this session)"
_PARAGRAPH_RE = re.compile(r"(\n[ \t]*\n)")
_GROUP_SEP = ",\u00a0\u202f\u2009"
# The second lookbehind skips version-like tokens such as "GPT-4.1".
_FIGURE_RE = re.compile(
    r"(?<![\w.])(?<![A-Za-z]-)"
    r"(?P<cur>(?:[$€£¥]|\b(?:usd|eur|gbp|us\$))\s?)?"
    rf"(?P<num>\d{{1,3}}(?:[{_GROUP_SEP}]\d{{3}})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    rf"(?![{_GROUP_SEP}.]?\d)"
    r"(?P<pct>\s?(?:%|percent\b|per cent\b))?"
    r"(?P<scale>\s?(?:thousand|million|billion|trillion|bn|mn|tn)\b)?",
    re.IGNORECASE,
)
_EVIDENCE_NUMBER_RE = re.compile(
    rf"(?<![\d.])\d{{1,3}}(?:[{_GROUP_SEP}]\d{{3}})+(?:\.\d+)?(?!\d)"
    rf"|(?<![\d.{_GROUP_SEP}])\d+(?:\.\d+)?(?!\.?\d)"
)
_SCALE_EXP = {"thousand": 3, "million": 6, "mn": 6, "billion": 9, "bn": 9, "trillion": 12, "tn": 12}


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


def _figures(text: str) -> list[re.Match[str]]:
    """Return matches for specific numeric figures in `text`, skipping years and bare integers."""
    found = []
    for match in _FIGURE_RE.finditer(text):
        num = match.group("num")
        if re.fullmatch(r"19\d\d|20\d\d|2100", num) and not (match.group("cur") or match.group("pct")):
            continue
        if match.group("cur") or match.group("pct") or match.group("scale"):
            found.append(match)
            continue
        if not re.search(rf"[.{_GROUP_SEP}]", num):
            continue
        # Unmarked numbers after a capitalized word are usually names ("Llama 3.1", "Section 2.3").
        if re.search(r"\b[A-Z]\w* $", text[max(0, match.start() - 40) : match.start()]):
            continue
        found.append(match)
    return found


def _figure_in(fig: str, text: str) -> bool:
    """True if `fig` appears in `text`, tolerating thousands separators, $/% markers and unit scaling."""
    match = _FIGURE_RE.search(fig)
    if not match:
        return True
    whole, _, frac = re.sub(rf"[{_GROUP_SEP}]", "", match.group("num")).partition(".")
    groups = [whole[max(0, i - 3) : i] for i in range(len(whole), 0, -3)][::-1]
    literal = rf"[ {_GROUP_SEP}]?".join(groups) + (rf"\.{frac}" if frac else "")
    if re.search(rf"(?<![\d.])(?<!\d,){literal}(?![{_GROUP_SEP}]?\d)(?!\.\d)", text):
        return True
    scale = (match.group("scale") or "").strip().lower()
    if not scale:
        return False
    value = Decimal(f"{whole}.{frac}" if frac else whole)
    quantum = Decimal(1).scaleb(-len(frac))
    exp = _SCALE_EXP[scale]
    for found in _EVIDENCE_NUMBER_RE.finditer(text):
        raw = re.sub(rf"[{_GROUP_SEP}]", "", found.group(0))
        if len(raw) > 15:
            continue
        number = Decimal(raw)
        for unit in (0, 3, 6, 9, 12):
            if unit != exp and number.scaleb(unit - exp).quantize(quantum, ROUND_HALF_UP) == value:
                return True
    return False


def _source_text(url: str, sources: dict[str, str], evidence: str) -> str:
    """Return the retrieved text for `url`, or all evidence when none was captured for it."""
    normalized = _normalize(url)
    texts = [
        text
        for key, text in sources.items()
        if key == normalized or key.startswith(normalized) or normalized.startswith(key)
    ]
    return "\n".join(texts) or evidence


def _label_figures(paragraph: str, retrieved: set[str], evidence: str, sources: dict[str, str]) -> str:
    """Label figures in a cited paragraph that its grounded sources' retrieved text does not contain."""
    urls = [m.span() for m in _URL_RE.finditer(paragraph)]
    cited = dict.fromkeys(
        paragraph[s:e]
        for s, e in urls
        if not _REDACTED_RE.search(paragraph[s:e]) and _grounded(paragraph[s:e], retrieved, evidence)
    )
    if not cited:
        return paragraph
    source = "\n".join(_source_text(url, sources, evidence) for url in cited)
    figures = _figures(paragraph)
    unsupported = []
    for i, match in enumerate(figures):
        start, end = match.span()
        if any(s < end and start < e for s, e in urls):
            continue
        stop = figures[i + 1].start() if i + 1 < len(figures) else len(paragraph)
        if re.search(r"unverified|background knowledge", paragraph[end : min(end + 80, stop)], re.IGNORECASE):
            continue
        if not _figure_in(match.group(0), source):
            unsupported.append(end)
    for end in reversed(unsupported):
        paragraph = f"{paragraph[:end]} {_UNVERIFIED_FIGURE}{paragraph[end:]}"
    return paragraph


def _scrub_text(text: str, retrieved: set[str], evidence: str, sources: dict[str, str]) -> str:
    """Label unsupported figures in cited paragraphs, then replace every ungrounded URL with the unverified marker."""

    def replace(match: re.Match[str]) -> str:
        url = match.group(0)
        if _REDACTED_RE.search(url) or _grounded(url, retrieved, evidence):
            return url
        return _UNVERIFIED

    text = "".join(_label_figures(p, retrieved, evidence, sources) for p in _PARAGRAPH_RE.split(text))
    return _URL_RE.sub(replace, text)


def _scrub_content(
    content: str | list, retrieved: set[str], evidence: str, sources: dict[str, str]
) -> str | list:
    """Scrub a message's content, handling plain-string and content-block forms."""
    if isinstance(content, str):
        return _scrub_text(content, retrieved, evidence, sources)
    if isinstance(content, list):
        out = []
        for block in content:
            if isinstance(block, str):
                out.append(_scrub_text(block, retrieved, evidence, sources))
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                out.append({**block, "text": _scrub_text(block["text"], retrieved, evidence, sources)})
            else:
                out.append(block)
        return out
    return content


def _result_entries(body: str) -> dict[str, str]:
    """Map each result URL in a JSON tool result (e.g. Tavily) to that result's own text."""
    if not body.lstrip().startswith(("{", "[")):
        return {}
    try:
        stack = [json.loads(body)]
    except ValueError:
        return {}
    entries: dict[str, str] = {}
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            text = "\n".join(
                value for key in ("title", "content", "raw_content") if isinstance(value := node.get(key), str)
            )
            if isinstance(node.get("url"), str) and text.strip():
                key = _normalize(node["url"])
                entries[key] = f"{entries.get(key, '')}\n{text.lower()}"
            stack.extend(node.values())
    return entries


def _citation_evidence(messages: list[BaseMessage]) -> tuple[set[str], str, dict[str, str]]:
    """Return the URLs, raw tool evidence, and per-URL retrieved text visible in this model request."""
    evidence: list[str] = []
    retrieved: set[str] = set()
    sources: dict[str, str] = {}
    for message in messages:
        if isinstance(message, ToolMessage):
            body = _text(message.content)
            evidence.append(unquote(body).lower())
            urls = {_normalize(u) for u in _URL_RE.findall(body)}
            retrieved.update(urls)
            entries = _result_entries(body)
            for url in urls - entries.keys():
                entries[url] = body.lower()
            for url, text in entries.items():
                sources[url] = f"{sources.get(url, '')}\n{text}"
    return retrieved, "\n".join(evidence), sources


class CitationGuardMiddleware(AgentMiddleware):
    """Relabel final-answer citations that were never retrieved, and cited figures their source lacks."""

    def _scrub(
        self, response: ModelResponse, retrieved: set[str], evidence: str, sources: dict[str, str]
    ) -> ModelResponse:
        """Rewrite ungrounded URLs and unsupported cited figures in the final (tool-call-free) AI message."""
        messages = getattr(response, "result", None) or []
        if not messages or not isinstance(messages[-1], AIMessage):
            return response
        final = messages[-1]
        if final.tool_calls:
            return response
        scrubbed = _scrub_content(final.content, retrieved, evidence, sources)
        if scrubbed == final.content:
            return response
        messages[-1] = final.model_copy(update={"content": scrubbed})
        return response

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        retrieved, evidence, sources = _citation_evidence(request.messages)
        return self._scrub(handler(request), retrieved, evidence, sources)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        retrieved, evidence, sources = _citation_evidence(request.messages)
        return self._scrub(await handler(request), retrieved, evidence, sources)


if __name__ == "__main__":
    from types import SimpleNamespace

    real = "https://www.example.org/reports/trends-international-trade-2025"
    fake = "https://www.example.org/reports/trends-in-international-trade-2025"
    redacted = "https://data.example.gov/series/[REDACTED_PHONE]"

    guard = CitationGuardMiddleware()
    retrieved, evidence, sources = _citation_evidence(
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
    guard._scrub(response, retrieved, evidence, sources)
    out = response.result[-1].content

    assert real in out, out
    assert fake not in out, out
    assert _UNVERIFIED in out, out
    assert redacted in out, out
    assert _UNVERIFIED_FIGURE not in out, out

    # A tool-calling turn is not the final answer and must be left alone.
    mid = AIMessage(
        content=f"Checking {fake}",
        tool_calls=[{"name": "search", "args": {"q": "trade"}, "id": "3"}],
    )
    midresponse = SimpleNamespace(result=[mid])
    guard._scrub(midresponse, retrieved, evidence, sources)
    assert midresponse.result[-1].content == f"Checking {fake}"

    # Figures next to a retrieved citation must appear in that citation's own retrieved text.
    report = "https://www.example.com/files/annual_report_2025.pdf"
    other = "https://www.example.com/news/q1-results"
    tavily = json.dumps(
        {
            "results": [
                {"url": report, "title": "Annual Report", "content": "Total backlog $150.2 billion; revenue 37,869 million."},
                {"url": other, "title": "Q1", "content": "Services backlog of $69.7 billion at quarter end."},
            ]
        }
    )
    retrieved, evidence, sources = _citation_evidence(
        [
            ToolMessage(content=tavily, tool_call_id="4"),
            ToolMessage(content="https://stats.example.org/emissions output was 26 717 kt in 2024.", tool_call_id="5"),
        ]
    )

    def _final(text: str) -> str:
        result = SimpleNamespace(result=[AIMessage(content=text)])
        guard._scrub(result, retrieved, evidence, sources)
        return result.result[-1].content

    fabricated = f"Services backlog was **$69.7 billion** at year-end 2025.  \n[Annual report]({report})"
    assert _final(fabricated) == fabricated.replace("billion**", f"billion {_UNVERIFIED_FIGURE}**"), _final(fabricated)

    spaced = "Emissions were 26,717 kt in 2024 ([source](https://stats.example.org/emissions))."
    assert _final(spaced) == spaced, _final(spaced)

    verbatim = f"Backlog reached $150.2 billion and revenue $37.869 billion in 2025 ([report]({report}))."
    assert _final(verbatim) == verbatim, _final(verbatim)

    uncited = "Services backlog was $69.7 billion.\n\nSee the report for details."
    assert _final(uncited) == uncited, _final(uncited)

    labeled = f"Backlog was $12.5 billion (from background knowledge, unverified this session) ([report]({report}))."
    assert _final(labeled) == labeled, _final(labeled)

    def _answer(_request):
        return SimpleNamespace(result=[AIMessage(content=f"Leaked? {real}")])

    clean = guard.wrap_model_call(SimpleNamespace(messages=[]), _answer)
    assert real not in clean.result[-1].content, clean.result[-1].content

    print("citation guard self-test passed")
