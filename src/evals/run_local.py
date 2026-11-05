"""Run the golden dataset against the agent in-process (no deployment needed).

    uv run python -m src.evals.run_local --repetitions 3
"""

import argparse
import asyncio
from functools import cache

from dotenv import load_dotenv
from langsmith import Client

from .evaluators import EVALUATORS, final_answer

load_dotenv(override=True)

DATASET_NAME = "ambient-analyst-golden"


@cache
def local_agent():
    from agent.agent import make_agent

    return asyncio.run(make_agent({"configurable": {}}))


def target(inputs: dict) -> dict:
    return {"answer": final_answer(local_agent().invoke(inputs))}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=1, help="runs per example, to measure variance")
    args = parser.parse_args()

    Client().evaluate(
        target,
        data=DATASET_NAME,
        evaluators=EVALUATORS,
        experiment_prefix="ambient-analyst-local",
        num_repetitions=args.repetitions,
        max_concurrency=1,
    )
