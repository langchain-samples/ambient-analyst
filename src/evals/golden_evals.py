import argparse
import logging
import re
from collections.abc import Callable
from typing import Any

import dotenv
from langsmith import evaluate

logger = logging.getLogger(__name__)
dotenv.load_dotenv(override=True)

DATASET_NAME = "ambient-analyst-golden"
EXPERIMENT_PREFIX = "ambient-analyst-golden-local"

_AGENT = None


def _local_agent():
    global _AGENT
    if _AGENT is None:
        from agent.agent import make_agent

        _AGENT = make_agent({"configurable": {}})
    return _AGENT


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content or "")


def _error_message(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def _final_answer(outputs: dict) -> str:
    if "answer" in outputs:
        return _content_text(outputs["answer"])
    messages = outputs.get("messages") or []
    if not messages:
        return ""
    message = messages[-1]
    content = message.get("content", "") if isinstance(message, dict) else message.content
    return _content_text(content)


def call_local_agent(inputs: dict) -> dict:
    try:
        result = _local_agent().invoke(inputs)
        return {"answer": _final_answer(result)}
    except Exception as exc:  # noqa: BLE001 — eval rows should record startup/run failures
        return {
            "answer": "",
            "error": "Local agent unavailable",
            "detail": _error_message(exc),
            "retryable": False,
        }


def _regex_eval(key: str, pattern: str) -> Callable[[dict], dict]:
    regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def evaluator(outputs: dict) -> dict:
        answer = _final_answer(outputs)
        return {"key": key, "score": bool(regex.search(answer))}

    evaluator.__name__ = key
    return evaluator


REGEX_EVALUATORS = [
    _regex_eval("substantive_answer", r"\S(?:.|\n){499,}"),
    _regex_eval(
        "source_grounding",
        r"https?://|\[[^\]]+\]\([^)]+\)|\b(?:source|sources|according to)\b",
    ),
    _regex_eval(
        "dated_evidence",
        r"\b(?:20\d{2}|Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)\b",
    ),
    _regex_eval(
        "quantitative_evidence",
        r"(?:[$]\s?\d|\d+(?:\.\d+)?\s?(?:%|bps?|basis points?|million|"
        r"billion|trillion|x\b))",
    ),
    _regex_eval(
        "uncertainty_or_caveat",
        r"\b(?:confidence|caveat|uncertain|uncertainty|assumption|assume|"
        r"risk|risks|could not verify|unverified|limited)\b",
    ),
]


def _self_check() -> None:
    good = {
        "answer": (
            "According to sources, GDP grew 2.4% in July 2026. "
            "The caveat is that the release may be revised. " * 12
        )
    }
    bad = {"answer": "Looks fine."}
    assert all(e(good)["score"] for e in REGEX_EVALUATORS)
    assert not all(e(bad)["score"] for e in REGEX_EVALUATORS)
    assert call_local_agent.__name__ == "call_local_agent"


def main(num_experiments: int = 1):
    return [
        evaluate(
            call_local_agent,
            data=DATASET_NAME,
            evaluators=REGEX_EVALUATORS,
            experiment_prefix=f"{EXPERIMENT_PREFIX}-{i + 1:02d}",
            max_concurrency=1,
        )
        for i in range(num_experiments)
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-experiments", type=int, default=1)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        _self_check()
    else:
        main(args.num_experiments)
