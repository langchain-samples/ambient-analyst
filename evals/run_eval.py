"""Custom SDK eval for the LLM research agent — results show up in LangSmith.

Three evaluators over the `llm-research-golden` dataset (all on a 0.0-1.0
continuous scale — LangSmith's default feedback range, and what the `correctness`
key's tenant feedback config enforces; sending 0-100 here 400s the ingest):
- hallucination_free  (LLM judge)  0.0-1.0, higher = fewer/no unsupported specifics
- correctness         (LLM judge)  0.0-1.0, higher = closer to the reference answer
- memory_updated      (code)       1.0 if the run wrote to /memory else 0.0 (continuous learning)

The agent's real output is the full graph state (`{messages: [...]}`), so the
target flattens it to a plain `answer` string + the list of /memory writes — which
is exactly what made the UI's default variable-mapping unreliable.

The judge runs through the SAME LangSmith gateway as the agent — here the
ANTHROPIC_API_KEY is a gateway key (a direct api.anthropic.com call 401s).
IMPORTANT: the gateway's PII-redaction policy strips locations like "US"/"China";
disable that policy (or point EVAL_JUDGE_BASE_URL / EVAL_JUDGE_MODEL at a direct
provider key) so the judge actually sees the answer and scores are meaningful.

Run:  uv run --env-file .env python evals/run_eval.py
"""

import os
import pathlib
import sys
import dotenv

dotenv.load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from langchain.chat_models import init_chat_model
from langsmith import evaluate
from pydantic import BaseModel, Field

from llm_research_agent.agent import agent

DATASET = os.environ.get("EVAL_DATASET", "llm-research-golden")


# --- helpers ---------------------------------------------------------------
def _final_text(messages) -> str:
    """Text of the last AI message (handles str or content-block list, obj or dict)."""
    for m in reversed(messages or []):
        typ = getattr(m, "type", None) or (m.get("type") if isinstance(m, dict) else None)
        if typ == "ai":
            content = getattr(m, "content", None) if not isinstance(m, dict) else m.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _question(inputs: dict) -> str:
    msgs = inputs.get("messages") or []
    if not msgs:
        return ""
    m = msgs[-1]
    content = m.get("content") if isinstance(m, dict) else getattr(m, "content", "")
    return content if isinstance(content, str) else ""


def _memory_writes(messages) -> list[str]:
    return [
        str((tc.get("args") or {}).get("file_path", ""))
        for m in (messages or [])
        for tc in (getattr(m, "tool_calls", None) or [])
        if tc.get("name") in ("write_file", "edit_file")
        and str((tc.get("args") or {}).get("file_path", "")).startswith("/memory")
    ]


# --- target ----------------------------------------------------------------
def run_agent(inputs: dict) -> dict:
    result = agent.invoke({"messages": inputs["messages"]})
    msgs = result["messages"]
    return {"answer": _final_text(msgs), "memory_writes": _memory_writes(msgs)}


# --- LLM judges ------------------------------------------------------------
class Grade(BaseModel):
    score: float = Field(ge=0, le=1, description="Quality score from 0.0 (worst) to 1.0 (best) for this criterion.")
    comment: str = Field(description="One-sentence justification that supports the score.")


_judge = init_chat_model(
    os.environ.get("EVAL_JUDGE_MODEL", "claude-sonnet-4-6"),
    model_provider="anthropic",
    base_url=os.environ.get("EVAL_JUDGE_BASE_URL", "https://gateway.smith.langchain.com/anthropic"),
    temperature=0,
).with_structured_output(Grade)

_RUBRICS = {
    "hallucination_free": (
        "Grade the AI answer for HALLUCINATIONS: invented or unsupported specifics "
        "(fake model names, made-up benchmark numbers, dates, prices, or sources), or "
        "claims that contradict the reference. Score 0.0-1.0: 1.0 = no hallucinations, "
        "every specific is plausible/supported and uncertainty is flagged; ~0.5 = a few "
        "minor unsupported details; 0.0 = major fabrications or contradicts the reference."
    ),
    "correctness": (
        "Grade the AI answer for CORRECTNESS against the reference answer. Score 0.0-1.0: "
        "1.0 = fully consistent with the reference and covers the question's key points; "
        "~0.5 = partially correct or missing key points; 0.0 = wrong or contradicts the reference."
    ),
}


def _llm_eval(key: str):
    def fn(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        prompt = (
            f"{_RUBRICS[key]}\n\n"
            f"<question>\n{_question(inputs)}\n</question>\n\n"
            f"<reference_answer>\n{_final_text((reference_outputs or {}).get('messages'))}\n</reference_answer>\n\n"
            f"<ai_answer>\n{outputs.get('answer', '')}\n</ai_answer>"
        )
        g: Grade = _judge.invoke(prompt)
        return {"key": key, "score": g.score, "comment": g.comment}

    fn.__name__ = key
    return fn


# --- code eval -------------------------------------------------------------
def memory_updated(outputs: dict) -> dict:
    writes = outputs.get("memory_writes") or []
    return {
        "key": "memory_updated",
        "score": 1 if writes else 0,
        "comment": f"Wrote to {', '.join(sorted(set(writes)))}" if writes else "No /memory writes this run",
    }


def main() -> None:
    results = evaluate(
        run_agent,
        data=DATASET,
        evaluators=[_llm_eval("hallucination_free"), _llm_eval("correctness"), memory_updated],
        experiment_prefix="llm-research-sdk-eval",
        # Serial: all agent runs share one module-level Context Hub memory backend,
        # so concurrent runs writing /memory would race the parent commit -> 409.
        max_concurrency=1,
    )
    print(getattr(results, "experiment_name", results))


if __name__ == "__main__":
    main()
