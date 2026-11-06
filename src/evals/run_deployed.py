"""Run the golden dataset against a deployed agent (used by CI on each PR).

    DEPLOYMENT_URL=https://... uv run python -m src.evals.run_deployed
"""

import os

from dotenv import load_dotenv
from langgraph_sdk import get_sync_client
from langsmith import Client

from .evaluators import EVALUATORS

load_dotenv()

DATASET_NAME = "ambient-analyst-golden"
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "ambient-analyst")

agent = get_sync_client(url=os.environ["DEPLOYMENT_URL"], timeout=900)


def target(inputs: dict) -> dict:
    return agent.runs.wait(None, ASSISTANT_ID, input=inputs)


if __name__ == "__main__":
    Client().evaluate(
        target,
        data=DATASET_NAME,
        evaluators=EVALUATORS,
        experiment_prefix="ambient-analyst-deployed",
        max_concurrency=1,
    )
