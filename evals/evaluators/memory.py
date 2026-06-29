"""Continuous-learning check (code, not an LLM judge): did the run persist a
memory/scorecard update? 1 = it wrote to /memory this run.

This is the OFFLINE counterpart of evals/online_memory_eval.py — same idea, but
that one is a self-contained server-side artifact (stdlib only, dict-shaped
traces) and can't share this module.
"""

NAME = "memory_updated"


def build():
    def memory_updated(outputs: dict) -> dict:
        writes = outputs.get("memory_writes") or []
        return {
            "key": NAME,
            "score": 1 if writes else 0,
            "comment": f"Wrote to {', '.join(sorted(set(writes)))}" if writes else "No /memory writes this run",
        }

    return memory_updated
