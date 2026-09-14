import json
from collections import Counter

from langchain_core.tools import tool


@tool
def run_context_interpreter(events_json: str) -> str:
    """Summarize memory event JSON with exact counts before LLM judgment."""
    try:
        events = json.loads(events_json)
    except json.JSONDecodeError:
        events = [json.loads(line) for line in events_json.splitlines() if line.strip()]
    if isinstance(events, dict):
        events = [events]
    if not isinstance(events, list):
        events = []
    return json.dumps(
        {
            "event_count": len(events),
            "topics": Counter(str(event.get("topic", "unknown")) for event in events if isinstance(event, dict)).most_common(10),
            "event_kinds": Counter(str(event.get("event_kind", "memory_event")) for event in events if isinstance(event, dict)).most_common(10),
        },
        indent=2,
        sort_keys=True,
    )
