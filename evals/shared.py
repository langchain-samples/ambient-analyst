"""Shared building blocks for the eval suite.

Used by `evals/run.py` and every module under `evals/evaluators/`. Holds the bits
that are common across evaluators so each evaluator module stays a thin,
single-metric definition (see evals/evaluators/__init__.py for the convention).

The judges run through the SAME LangSmith gateway as the agent: the repo's
ANTHROPIC_API_KEY is a gateway key (a direct api.anthropic.com call 401s), so
each openevals judge is built with a gateway-routed chat model passed as `judge=`
— NOT a `model="provider:name"` string. IMPORTANT: the gateway's PII-redaction
policy can strip locations like "US"/"China"; disable it (or point
EVAL_JUDGE_BASE_URL / EVAL_JUDGE_MODEL at a direct key) so scores are meaningful.
"""

import os

from langchain.chat_models import init_chat_model
from openevals.llm import create_llm_as_judge

DATASET = os.environ.get("EVAL_DATASET", "llm-research-golden")
# Serial: every agent run shares one module-level Context Hub /memory backend, so
# concurrent runs writing /memory race the parent commit -> 409.
MAX_CONCURRENCY = 1


# --- message-state helpers -------------------------------------------------
def final_text(messages) -> str:
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


def question(inputs: dict) -> str:
    msgs = (inputs or {}).get("messages") or []
    if not msgs:
        return ""
    m = msgs[-1]
    content = m.get("content") if isinstance(m, dict) else getattr(m, "content", "")
    return content if isinstance(content, str) else ""


def memory_writes(messages) -> list[str]:
    return [
        str((tc.get("args") or {}).get("file_path", ""))
        for m in (messages or [])
        for tc in (getattr(m, "tool_calls", None) or [])
        if tc.get("name") in ("write_file", "edit_file")
        and str((tc.get("args") or {}).get("file_path", "")).startswith("/memory")
    ]


# --- target ----------------------------------------------------------------
def make_target(agent):
    """Wrap an agent into a LangSmith eval target (flattens graph state to a plain
    `answer` string + the list of /memory writes)."""

    def target(inputs: dict) -> dict:
        result = agent.invoke({"messages": inputs["messages"]})
        msgs = result["messages"]
        return {"answer": final_text(msgs), "memory_writes": memory_writes(msgs)}

    return target


# --- judge factory ---------------------------------------------------------
def _gateway_judge():
    return init_chat_model(
        os.environ.get("EVAL_JUDGE_MODEL", "claude-sonnet-4-6"),
        model_provider="anthropic",
        base_url=os.environ.get("EVAL_JUDGE_BASE_URL", "https://gateway.smith.langchain.com/anthropic"),
        temperature=0,
    )


def make_judge(prompt, feedback_key: str):
    """An openevals LLM-as-judge wired to the gateway. continuous=False -> binary
    0/1 (what the `correctness` key's tenant feedback config enforces)."""
    return create_llm_as_judge(prompt=prompt, feedback_key=feedback_key, judge=_gateway_judge())


# --- self-check (no network) -----------------------------------------------
if __name__ == "__main__":
    from types import SimpleNamespace as NS  # mimics AIMessage's .tool_calls attr

    assert question({"messages": [{"role": "user", "content": "hi"}]}) == "hi"
    assert question({}) == ""
    assert final_text([{"type": "ai", "content": "answer"}]) == "answer"
    assert final_text([{"type": "ai", "content": [{"type": "text", "text": "blk"}]}]) == "blk"
    assert final_text([{"type": "human", "content": "q"}]) == ""
    # Real runs return message objects, so tool_calls is an attribute, not a key.
    msgs = [NS(tool_calls=[{"name": "write_file", "args": {"file_path": "/memory/scorecard.md"}}])]
    assert memory_writes(msgs) == ["/memory/scorecard.md"]
    assert memory_writes([NS(tool_calls=[{"name": "write_file", "args": {"file_path": "/scratch/x"}}])]) == []
    print("shared.py self-check OK")
