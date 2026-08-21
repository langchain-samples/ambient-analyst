"""Regex PII/PHI redaction middleware.

Scrubs personal health information (SSNs, emails, phones, etc.) out of every
message the model sees — user input *and* tool results (fetched pages, search
hits) alike. Redacting at the model boundary means the model can't reason over
or echo raw identifiers, and can't copy them into the memory/scorecard it
writes back.

Deliberately simple: a fixed set of regexes. Not a compliance-grade
de-identifier — it catches common structured identifiers, not free-text names
or addresses.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from langchain.agents.middleware.types import AgentMiddleware

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from langchain.agents.middleware.types import ModelRequest, ModelResponse
    from langchain_core.messages import BaseMessage

# label -> pattern. Order doesn't matter; each runs independently.
_PATTERNS = {
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "PHONE": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "MRN": re.compile(r"\b(?:MRN|Medical Record(?:\s*(?:No|Number|#))?)[:\s#]*\d{4,}\b", re.I),
}


def redact(text: str) -> str:
    """Replace every matched identifier with a `[REDACTED_<LABEL>]` marker."""
    for label, pattern in _PATTERNS.items():
        text = pattern.sub(f"[REDACTED_{label}]", text)
    return text


def _redact_content(content: str | list) -> str | list:
    """Redact a message's content, handling plain-string and content-block forms."""
    if isinstance(content, str):
        return redact(content)
    if isinstance(content, list):
        out = []
        for block in content:
            if isinstance(block, str):
                out.append(redact(block))
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                out.append({**block, "text": redact(block["text"])})
            else:
                out.append(block)
        return out
    return content


def _redact_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    return [m.model_copy(update={"content": _redact_content(m.content)}) for m in messages]


class PIIRedactionMiddleware(AgentMiddleware):
    """Redact PII/PHI from every message before it reaches the model."""

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        return handler(request.override(messages=_redact_messages(request.messages)))

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        return await handler(request.override(messages=_redact_messages(request.messages)))


if __name__ == "__main__":
    from langchain_core.messages import AIMessage, HumanMessage

    dirty = (
        "Patient SSN 123-45-6789, email jane.doe@example.com, "
        "call (555) 123-4567. MRN: 00982211. Card 4111 1111 1111 1111."
    )
    clean = redact(dirty)
    for needle in ("123-45-6789", "jane.doe@example.com", "555", "4111", "00982211"):
        assert needle not in clean, needle
    assert clean.count("[REDACTED_") == 5, clean
    assert redact("no identifiers here") == "no identifiers here"

    # message-level: string content and content-block lists both scrubbed
    msgs = _redact_messages([
        HumanMessage(content="my ssn is 111-22-3333"),
        AIMessage(content=[{"type": "text", "text": "email me at x@y.com"}]),
    ])
    assert "111-22-3333" not in msgs[0].content
    assert "x@y.com" not in msgs[1].content[0]["text"]
    print("ok:", clean)
