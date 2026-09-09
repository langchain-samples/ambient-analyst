import os
import logging

import dotenv
import requests
from langsmith import evaluate

logger = logging.getLogger(__name__)
dotenv.load_dotenv()

DATASET_NAME = "ambient-analyst-golden-8"
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "ambient-analyst")


def _error_message(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"missing {name}")
    return value


def call_preview_agent(inputs: dict) -> dict:
    ###
    ### ANY CUSTOM LOGC/DATA HERE
    ###

    ###
    ### CALL AGENT
    ###
    try:
        response = requests.post(
            f"{_required_env('PREVIEW_BASE_URL')}/runs/wait",
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": _required_env("LANGSMITH_API_KEY"),
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
    except (requests.RequestException, ValueError) as exc:
        return {
            "error": "Preview agent unavailable",
            "detail": _error_message(exc),
            "retryable": isinstance(exc, requests.RequestException),
        }


def main():
    return evaluate(
        call_preview_agent, # target function
        data=DATASET_NAME, # input data to agent
        evaluators=None, # custom evaluators
        experiment_prefix="ambient-analyst-relevant-pr_",
        max_concurrency=1,
    )


if __name__ == "__main__":
    main()
