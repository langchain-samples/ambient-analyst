"""Code evaluators shared by every eval runner.

Each evaluator is a plain function: LangSmith passes it the target's `outputs`
and records the returned bool as a score keyed by the function name.
"""

import re
from typing import Any


def final_answer(outputs: dict) -> str:
    """Return the agent's final answer text from either runner's output shape."""
    if "answer" in outputs:
        return _text(outputs["answer"])
    messages = outputs.get("messages") or []
    if not messages:
        return ""
    last = messages[-1]
    return _text(last.get("content") if isinstance(last, dict) else last.content)


def _text(content: Any) -> str:
    if isinstance(content, list):
        return "\n".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
    return str(content or "")


def _regex_evaluator(name: str, pattern: str):
    regex = re.compile(pattern, re.IGNORECASE | re.DOTALL)

    def evaluator(outputs: dict) -> bool:
        return bool(regex.search(final_answer(outputs)))

    evaluator.__name__ = name
    return evaluator


MONTH = r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"

EVALUATORS = [
    _regex_evaluator("substantive_answer", r"\S.{499,}"),
    _regex_evaluator("source_grounding", r"https?://|\[[^\]]+\]\([^)]+\)|\b(?:sources?|according to)\b"),
    _regex_evaluator("dated_evidence", rf"\b(?:20\d{{2}}|{MONTH})\b"),
    _regex_evaluator("quantitative_evidence", r"\$\s?\d|\d+(?:\.\d+)?\s?(?:%|bps?|basis points?|million|billion|trillion|x\b)"),
    _regex_evaluator("uncertainty_or_caveat", r"\b(?:confidence|caveat|uncertain(?:ty)?|assum(?:e|ption)|risks?|could not verify|unverified|limited)\b"),
]


if __name__ == "__main__":
    good = {"answer": "According to sources, GDP grew 2.4% in July 2026. The caveat is that it may be revised. " * 8}
    bad = {"answer": "Looks fine."}
    assert all(e(good) for e in EVALUATORS)
    assert not any(e(bad) for e in EVALUATORS)
    print("evaluators ok")
