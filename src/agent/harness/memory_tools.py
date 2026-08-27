"""Agent memory tools for capture and compact event analysis."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json

from deepagents.backends.context_hub import ContextHubBackend
from langchain_core.tools import tool

from agent.harness.context import MEMORY_REPO

MEMORY_EVENTS_FILE = "hot-path-events.jsonl"
MEMORY_EVENTS_PATH = f"/memory/{MEMORY_EVENTS_FILE}"
COLD_MEMORY_PATH = "/memory/cold-path-memory.md"


def _parse_events(payload: str) -> list[dict]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return [
            item
            for line in payload.splitlines()
            if line.strip()
            for item in [json.loads(line)]
            if isinstance(item, dict)
        ]
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def _event_summary(events: list[dict]) -> dict:
    return {
        "event_count": len(events),
        "topics": Counter(str(e.get("topic", "unknown")) for e in events).most_common(10),
        "event_kinds": Counter(
            str(e.get("event_kind") or e.get("kind") or "memory_event") for e in events
        ).most_common(10),
        "confidence": Counter(
            str(e.get("confidence", "unspecified")) for e in events
        ).most_common(),
        "sources": Counter(str(e.get("source", "unspecified")) for e in events).most_common(
            10
        ),
        "samples": events[:5],
    }


@tool
def run_context_interpreter(events_json: str) -> str:
    """Summarize memory/event JSON with exact counts before LLM judgment."""
    return json.dumps(_event_summary(_parse_events(events_json)), indent=2, sort_keys=True)


@tool
def hot_path_record_memory(
    topic: str,
    fact: str,
    evidence: str,
    source: str = "conversation",
    event_kind: str = "memory_event",
    confidence: str = "medium",
) -> str:
    """Append a cheap, auditable memory event to long-term Context Hub memory."""
    backend = ContextHubBackend(MEMORY_REPO)
    previous = backend.read(MEMORY_EVENTS_FILE)
    content = "" if previous.error or previous.file_data is None else previous.file_data.content
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_kind": event_kind,
        "topic": topic,
        "fact": fact,
        "evidence": evidence,
        "source": source,
        "confidence": confidence,
    }
    # ponytail: full-file rewrite is fine for demos; use DB append for concurrent writers.
    result = backend.write(
        MEMORY_EVENTS_FILE,
        content + json.dumps(event, sort_keys=True) + "\n",
    )
    if result.error:
        return f"failed to record memory event: {result.error}"
    return json.dumps(
        {
            "recorded": True,
            "events_path": MEMORY_EVENTS_PATH,
            "cold_memory_path": COLD_MEMORY_PATH,
            "next_tool": "task(memory-consolidator) when patterns repeat",
        },
        sort_keys=True,
    )


if __name__ == "__main__":
    events = _parse_events(
        '{"topic":"rates","event_kind":"preference"}\n{"topic":"rates"}'
    )
    summary = _event_summary(events)
    assert summary["event_count"] == 2
    assert summary["topics"][0] == ("rates", 2)
    assert dict(summary["event_kinds"])["memory_event"] == 1
    print("ok")
