"""Pull the golden dataset from LangSmith (the source of truth) into a snapshot.

The dataset lives on LangSmith and is the canonical benchmark: its questions
(inputs) and reference answers (outputs) are maintained there, not hardcoded here.
Reference outputs are the agent's own vetted answers, so the eval suite
(evals/run.py) grades future changes against today's behavior.

This script reads the live examples and writes a git-trackable snapshot
(golden_snapshot.jsonl, one example per line, next to this file) so dataset drift
shows up in a diff.

Schema (matches what evals/shared.py reads):
- inputs            : {"messages": [{"role": "user", "content": <question>}]}
- reference outputs : {"messages": [{"type": "ai", "content": <reference answer>}]}

Run:  uv run --env-file .env python evals/datasets/sync.py
"""

import json
import pathlib
import sys

from langsmith import Client

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from evals.shared import DATASET  # single source of truth for the dataset name

SNAPSHOT = pathlib.Path(__file__).resolve().parent / "golden_snapshot.jsonl"


def _question(inputs: dict) -> str:
    msgs = (inputs or {}).get("messages") or [{}]
    return msgs[-1].get("content", "")


def _answer(outputs: dict) -> str:
    msgs = (outputs or {}).get("messages") or [{}]
    return msgs[-1].get("content", "")


def main() -> None:
    client = Client()
    ds = client.read_dataset(dataset_name=DATASET)

    examples = sorted(client.list_examples(dataset_id=ds.id), key=lambda e: str(e.id))
    snapshot = [
        {"id": str(e.id), "inputs": e.inputs, "outputs": e.outputs}
        for e in examples
    ]
    SNAPSHOT.write_text(
        "".join(json.dumps(rec, sort_keys=True, default=str) + "\n" for rec in snapshot)
    )

    print(f"Pulled {len(snapshot)} examples from '{DATASET}' ({ds.id}).")
    for e in examples:
        q, a = _question(e.inputs), _answer(e.outputs)
        print(f"  - {q[:70]!r} -> reference {len(a)} chars")
    print(f"\nSnapshot: {SNAPSHOT}")
    print(f"View: https://smith.langchain.com/datasets/{ds.id}")


if __name__ == "__main__":
    main()
