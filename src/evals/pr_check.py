import os
import logging

import dotenv
import requests
from langsmith import evaluate

logger = logging.getLogger(__name__)
dotenv.load_dotenv()

DATASET_NAME = "ambient-analyst-relevant"
PREVIEW_BASE_URL = os.getenv("PREVIEW_BASE_URL")
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "ambient-analyst")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")


def call_preview_agent(inputs: dict) -> dict:
    response = requests.post(
        f"{PREVIEW_BASE_URL}/runs/wait",
        headers={
            "Content-Type": "application/json",
            "X-Api-Key": LANGSMITH_API_KEY,
            "X-Auth-Scheme": "langsmith-api-key",
        },
        json={
            "assistant_id": ASSISTANT_ID,
            "input": inputs,
        },
        timeout=900,
    )
    response.raise_for_status()
    return response.json()


def main():
    return evaluate(
        call_preview_agent,
        data=DATASET_NAME,
        evaluators=None,
        experiment_prefix="ambient-analyst-relevant-pr_",
        max_concurrency=1,
    )


if __name__ == "__main__":
    main()
