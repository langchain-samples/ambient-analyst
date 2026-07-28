from __future__ import annotations

import argparse
import asyncio
import importlib
import dotenv
from langsmith import Client


dotenv.load_dotenv(override=True)


DATASET = "e7fc5f98-83ca-4cb4-87b5-b6a5540fd374"
TARGET = "ambient_analyst.agent:agent"
APPLICATION = "ambient-analyst"
LLM_EVALUATOR = "ambient-analyst-correctness"
CODE_EVALUATOR = "ambient-analyst-answer-present"
JUDGE_PROMPT = "ambient-analyst-eval-correctness"
REGRESSION_KEY = "answer_present"

ANSWER_PRESENT_CODE = """
def perform_eval(run, example):
    answer = (run.outputs or {}).get("answer")
    answer = "" if answer is None else str(answer).strip()
    return {
        "key": "answer_present",
        "score": bool(answer),
        "comment": "answer was non-empty" if answer else "answer was empty",
    }
""".strip()


def import_target(spec: str):
    module, attr = spec.split(":", 1)
    target = importlib.import_module(module)
    for name in attr.split("."):
        target = getattr(target, name)
    return target


def predict_for(target_spec):
    target = import_target(target_spec)

    def predict(inputs):
        request = (
            inputs
            if "messages" in inputs
            else {"messages": [{"role": "user", "content": inputs.get("question") or inputs.get("input") or inputs}]}
        )
        result = target.invoke(request) if hasattr(target, "invoke") else target(request)
        message = result["messages"][-1] if isinstance(result, dict) and result.get("messages") else result
        return {"answer": str(getattr(message, "content", message.get("content") if isinstance(message, dict) else message))}

    return predict


def answer_present(*, outputs, **_):
    answer = str(outputs.get("answer") or "").strip()
    return {
        "key": "answer_present",
        "score": bool(answer),
        "comment": "answer was non-empty" if answer else "answer was empty",
    }


def average_score(feedback_stats, key: str) -> float:
    value = (feedback_stats or {}).get(key)
    if isinstance(value, dict):
        value = value.get("avg")
    if value is None:
        raise ValueError(f"experiment has no feedback average for {key!r}")
    return float(value)


def result_score(results, key: str) -> float:
    scores = []
    for row in results:
        eval_results = row["evaluation_results"] if isinstance(row, dict) else row.evaluation_results
        for item in eval_results["results"]:
            item_key = item.get("key") if isinstance(item, dict) else item.key
            if item_key == key:
                score = item.get("score") if isinstance(item, dict) else item.score
                scores.append(float(score))
    if not scores:
        raise ValueError(f"experiment has no feedback scores for {key!r}")
    return sum(scores) / len(scores)


def previous_experiment(client: Client, *, current_id, dataset: str, prefix: str):
    experiments = sorted(
        client.list_projects(
            name_contains=prefix,
            reference_dataset_id=dataset,
            include_stats=True,
            limit=100,
        ),
        key=lambda project: project.start_time,
        reverse=True,
    )
    return next((project for project in experiments if project.id != current_id), None)


def check_regression(client: Client, results, args: argparse.Namespace) -> None:
    previous = previous_experiment(
        client,
        current_id=results.experiment_id,
        dataset=args.dataset,
        prefix=args.experiment_prefix,
    )
    if previous is None:
        print("No previous experiment found; skipping regression check.")
        return

    current_score = result_score(results, args.regression_key)
    previous_score = average_score(previous.feedback_stats, args.regression_key)
    print(
        f"{args.regression_key}: current={current_score:.4f} "
        f"previous={previous_score:.4f} ({previous.name})"
    )
    if current_score < previous_score:
        raise SystemExit(
            f"Regression detected: {results.experiment_name} scored {current_score:.4f}, "
            f"below {previous.name} at {previous_score:.4f}"
        )


def judge_prompt():
    prompt = Client().pull_prompt(JUDGE_PROMPT, skip_cache=True)
    template = prompt.messages[0].prompt.template
    if "Ambient Analyst" not in template:
        raise ValueError(f"{JUDGE_PROMPT} is not customized for Ambient Analyst")
    return template


def judge_prompt_commit():
    return next(Client().list_prompt_commits(JUDGE_PROMPT)).commit_hash


def run(args: argparse.Namespace) -> None:
    client = Client()
    results = client.evaluate(
        predict_for(args.target),
        data=args.dataset,
        evaluators=[answer_present],
        experiment_prefix=args.experiment_prefix,
        max_concurrency=args.max_concurrency,
        metadata={
            "target": args.target,
            "application": APPLICATION,
            "evaluators": [args.code_evaluator, args.llm_evaluator],
            "framework": "openevals",
        },
    )
    print(f"Experiment: {results.experiment_name}")
    if args.regression_check:
        check_regression(client, results, args)


async def find_evaluator(client, name):
    async for evaluator in client.evaluators.list(name_contains=name, limit=20):
        if evaluator.name == name:
            return evaluator
    return None


async def save_evaluator(client, name, evaluator_type, feedback_key, **body):
    existing = await find_evaluator(client, name)
    kwargs = {"name": name, "extra_body": {"feedback_keys": [feedback_key]}, **body}
    if existing and existing.id:
        await client.evaluators.update(existing.id, **kwargs)
        return await client.evaluators.retrieve(existing.id)
    created = await client.evaluators.create(type=evaluator_type, **kwargs)
    return await client.evaluators.retrieve(created.id)


async def sync_evaluators(args: argparse.Namespace) -> None:
    judge_prompt()
    commit_hash = judge_prompt_commit()
    client = Client()
    llm = await save_evaluator(
        client,
        args.llm_evaluator,
        "llm",
        "correctness",
        llm_evaluator={
            "prompt_repo_handle": JUDGE_PROMPT,
            "commit_hash_or_tag": commit_hash,
            "variable_mapping": {
                "inputs": "inputs",
                "outputs": "outputs",
                "reference_outputs": "reference_outputs",
            },
        },
    )
    code = await save_evaluator(
        client,
        args.code_evaluator,
        "code",
        "answer_present",
        code_evaluator={"code": ANSWER_PRESENT_CODE, "language": "python"},
    )
    print(f"{llm.name}: {llm.id} {llm.feedback_keys}")
    print(f"{code.name}: {code.id} {code.feedback_keys}")


def self_test() -> None:
    assert answer_present(outputs={"answer": "ok"})["score"] is True
    assert answer_present(outputs={"answer": ""})["score"] is False
    assert average_score({"answer_present": {"avg": True}}, "answer_present") == 1.0
    assert average_score({"answer_present": {"avg": 0.5}}, "answer_present") == 0.5
    row = {"evaluation_results": {"results": [{"key": "answer_present", "score": True}]}}
    assert result_score([row], "answer_present") == 1.0
    print("self-test passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Ambient Analyst evals.")
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--llm-evaluator", default=LLM_EVALUATOR)
    parser.add_argument("--code-evaluator", default=CODE_EVALUATOR)
    parser.add_argument("--experiment-prefix", default="ambient-analyst-offline")
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--regression-check", action="store_true")
    parser.add_argument("--regression-key", default=REGRESSION_KEY)
    parser.add_argument("--sync-evaluators", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
    elif args.sync_evaluators:
        asyncio.run(sync_evaluators(args))
    else:
        run(args)


if __name__ == "__main__":
    main()
