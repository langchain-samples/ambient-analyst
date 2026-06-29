"""Run the LLM research agent evals — one entrypoint, flags pick the type.

  # offline eval over the golden dataset, all evaluators (default)
  uv run --env-file .env python evals/run.py

  # offline, a subset of evaluators
  uv run --env-file .env python evals/run.py --evaluators correctness conciseness

  # A/B model comparison: same evaluators, one experiment per model arm
  uv run --env-file .env python evals/run.py --type ab --matchup anthropic-vs-openai

  # list available evaluators + matchups and exit
  uv run --env-file .env python evals/run.py --list

Evaluators live in evals/evaluators/ (one module per metric); shared building
blocks (target, gateway judge, helpers) live in evals/shared.py.
"""

import argparse
import os
import pathlib
import sys

import dotenv

dotenv.load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from langchain.chat_models import init_chat_model
from langsmith import Client, evaluate

from evals.evaluators import ALL
from evals.shared import DATASET, MAX_CONCURRENCY, make_target

# --- A/B matchups (only used by --type ab) ---------------------------------
GATEWAY = "https://gateway.smith.langchain.com"
# The gateway is authed by a LangSmith gateway key; ANTHROPIC_API_KEY is already
# set to that key in this repo's .env, so it's the fallback.
GATEWAY_KEY = os.environ.get("LANGSMITH_API_KEY_GATEWAY") or os.environ.get("ANTHROPIC_API_KEY")

# Overridable via env so provider renames don't need code changes.
ANTHROPIC = os.environ.get("AB_ANTHROPIC", "claude-sonnet-4-6")
OPENAI_EXPENSIVE = os.environ.get("AB_OPENAI_EXPENSIVE", "gpt-5")
OPENAI_CHEAP = os.environ.get("AB_OPENAI_CHEAP", "gpt-5-mini")

MATCHUPS = {
    "anthropic-vs-openai": [
        {"label": "anthropic", "model": ANTHROPIC, "provider": "anthropic"},
        {"label": "openai", "model": OPENAI_EXPENSIVE, "provider": "openai"},
    ],
    "openai-cost": [
        {"label": "openai-expensive", "model": OPENAI_EXPENSIVE, "provider": "openai"},
        {"label": "openai-cheap", "model": OPENAI_CHEAP, "provider": "openai"},
    ],
}


def _evaluators(names):
    """Instantiate the requested evaluators (default: all, in registry order)."""
    return [ALL[name]() for name in (names or list(ALL))]


def _gateway_chat(model: str, provider: str):
    return init_chat_model(
        model=model, model_provider=provider, base_url=f"{GATEWAY}/{provider}", api_key=GATEWAY_KEY
    )


def run_offline(names) -> None:
    from llm_research_agent.agent import agent

    results = evaluate(
        make_target(agent),
        data=DATASET,
        evaluators=_evaluators(names),
        experiment_prefix="llm-research-offline",
        max_concurrency=MAX_CONCURRENCY,
    )
    print(getattr(results, "experiment_name", results))


def run_ab(matchup: str, names) -> None:
    from llm_research_agent.agent import build_agent

    arms = MATCHUPS[matchup]
    client = Client()
    ds = client.read_dataset(dataset_name=DATASET)
    print(f"\n=== matchup '{matchup}' over '{DATASET}' ({ds.id}) ===")

    session_ids = []
    for arm in arms:
        target = make_target(build_agent(_gateway_chat(arm["model"], arm["provider"])))
        print(f"\n--- arm '{arm['label']}': {arm['provider']}:{arm['model']} ---")
        results = evaluate(
            target,
            data=DATASET,
            evaluators=_evaluators(names),
            experiment_prefix=f"ab-{matchup}-{arm['label']}",
            metadata={"matchup": matchup, "provider": arm["provider"], "model": arm["model"]},
            max_concurrency=MAX_CONCURRENCY,
        )
        exp = getattr(results, "experiment_name", str(results))
        print(f"    experiment: {exp}")
        try:
            session_ids.append(str(client.read_project(project_name=exp).id))
        except Exception as e:  # noqa: BLE001 — compare URL is best-effort
            print(f"    (couldn't resolve session id for compare URL: {e})")

    print("\nCompare arms in the LangSmith UI:")
    if len(session_ids) == len(arms):
        sel = "".join(f"&selectedSessions={s}" for s in session_ids)
        print(f"  https://smith.langchain.com/datasets/{ds.id}/compare?{sel.lstrip('&')}")
    else:
        print(f"  Open dataset {ds.id} -> Experiments tab, select the 'ab-{matchup}-*' runs.")


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--type", choices=["offline", "ab"], default="offline", help="eval type (default: offline)")
    p.add_argument(
        "--evaluators", nargs="*", choices=list(ALL), metavar="NAME",
        help=f"subset to run (default: all). Choices: {', '.join(ALL)}",
    )
    p.add_argument("--matchup", choices=list(MATCHUPS), help="A/B matchup (required for --type ab)")
    p.add_argument("--list", action="store_true", help="list evaluators + matchups and exit")
    args = p.parse_args()

    if args.list:
        print("evaluators:", ", ".join(ALL))
        print("matchups:  ", ", ".join(MATCHUPS))
        return

    if args.type == "ab":
        if not args.matchup:
            p.error("--type ab requires --matchup (one of: " + ", ".join(MATCHUPS) + ")")
        run_ab(args.matchup, args.evaluators)
    else:
        run_offline(args.evaluators)


if __name__ == "__main__":
    main()
