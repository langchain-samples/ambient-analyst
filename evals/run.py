"""Run the LLM research agent evals — one entrypoint, flags pick the type.

Every run records the agent's model in experiment metadata (`agent_model` +
`agent_provider`), so you can group/compare experiments by model in LangSmith.

  # offline eval over the golden dataset, all evaluators (default)
  uv run --env-file .env python evals/run.py

  # offline, a subset of evaluators
  uv run --env-file .env python evals/run.py --evaluators correctness conciseness

  # A/B two models you choose independently — one experiment per arm
  uv run --env-file .env python evals/run.py --type ab \
      --model-a anthropic:claude-sonnet-4-6 --model-b openai:gpt-5
  # --model-a defaults to the agent's own model, so the common case is just:
  uv run --env-file .env python evals/run.py --type ab --model-b openai:gpt-5

  # Every assistant on a deployment — discover all assistants at an endpoint and
  # run the evals against each (one experiment per assistant, tagged by identity).
  uv run --env-file .env python evals/run.py --type assistants \
      --endpoint https://my-deployment.us.langgraph.app
  # --endpoint defaults to $LANGGRAPH_DEPLOYMENT_URL; --graph-id filters to one graph.

  # list available evaluators and exit
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

GATEWAY = "https://gateway.smith.langchain.com"
# The gateway is authed by a LangSmith gateway key; ANTHROPIC_API_KEY is already
# set to that key in this repo's .env, so it's the fallback.
GATEWAY_KEY = os.environ.get("LANGSMITH_API_KEY_GATEWAY") or os.environ.get("ANTHROPIC_API_KEY")


def _spec(value: str):
    """Parse a 'provider:model' CLI arg into (provider, model)."""
    provider, sep, model = value.partition(":")
    if not sep or not provider or not model:
        raise argparse.ArgumentTypeError(f"expected 'provider:model', got {value!r}")
    return provider, model


def _evaluators(names):
    """Instantiate the requested evaluators (default: all, in registry order)."""
    return [ALL[name]() for name in (names or list(ALL))]


def _gateway_chat(model: str, provider: str):
    return init_chat_model(
        model=model, model_provider=provider, base_url=f"{GATEWAY}/{provider}", api_key=GATEWAY_KEY
    )


def _evaluate_arm(
    target, names, experiment_prefix: str, *, eval_type: str,
    model: str | None = None, provider: str | None = None, extra: dict | None = None,
) -> str:
    """Run one evaluate() over the dataset, always tagging eval_type and — when
    known — the agent model plus any `extra` metadata (e.g. the assistant identity
    for remote assistants, whose model is fixed by the deployment, not chosen here)."""
    metadata = {"eval_type": eval_type, **(extra or {})}
    if model is not None:
        metadata["agent_model"] = model
    if provider is not None:
        metadata["agent_provider"] = provider
    results = evaluate(
        target,
        data=DATASET,
        evaluators=_evaluators(names),
        experiment_prefix=experiment_prefix,
        metadata=metadata,
        max_concurrency=MAX_CONCURRENCY,
    )
    return getattr(results, "experiment_name", str(results))


def run_offline(names) -> None:
    from llm_research_agent.agent import DEFAULT_MODEL, DEFAULT_PROVIDER, agent

    exp = _evaluate_arm(
        make_target(agent), names, "llm-research-offline",
        model=DEFAULT_MODEL, provider=DEFAULT_PROVIDER, eval_type="offline",
    )
    print(exp)


def run_ab(model_a, model_b, names) -> None:
    from llm_research_agent.agent import build_agent

    client = Client()
    ds = client.read_dataset(dataset_name=DATASET)
    print(f"\n=== A/B over '{DATASET}' ({ds.id}) ===")

    session_ids = []
    for provider, model in (model_a, model_b):
        target = make_target(build_agent(_gateway_chat(model, provider)))
        print(f"\n--- arm {provider}:{model} ---")
        exp = _evaluate_arm(
            target, names, f"ab-{provider}-{model}",
            model=model, provider=provider, eval_type="ab",
        )
        print(f"    experiment: {exp}")
        try:
            session_ids.append(str(client.read_project(project_name=exp).id))
        except Exception as e:  # noqa: BLE001 — compare URL is best-effort
            print(f"    (couldn't resolve session id for compare URL: {e})")

    print("\nCompare arms in the LangSmith UI:")
    if len(session_ids) == 2:
        sel = "".join(f"&selectedSessions={s}" for s in session_ids)
        print(f"  https://smith.langchain.com/datasets/{ds.id}/compare?{sel.lstrip('&')}")
    else:
        print(f"  Open dataset {ds.id} -> Experiments tab, select the 'ab-*' runs.")


def run_assistants(endpoint: str, names, graph_id: str | None = None) -> None:
    """Discover every assistant on `endpoint` and eval each one against the dataset.

    Each assistant is a saved config (prompt + tools) of a deployed graph; we bind a
    RemoteGraph to its assistant_id and run the full evaluator suite over it, so the
    ACTUAL deployed configuration is what's scored (not a locally rebuilt copy)."""
    from langgraph.pregel.remote import RemoteGraph
    from langgraph_sdk import get_client, get_sync_client

    client, sync_client = get_client(url=endpoint), get_sync_client(url=endpoint)

    assistants, offset = [], 0
    while True:
        page = sync_client.assistants.search(graph_id=graph_id, limit=100, offset=offset)
        assistants.extend(page)
        if len(page) < 100:
            break
        offset += 100

    scope = f" for graph {graph_id!r}" if graph_id else ""
    if not assistants:
        print(f"No assistants found at {endpoint}{scope}.")
        return

    print(f"\n=== evals over {len(assistants)} assistant(s) at {endpoint}{scope} ===")
    for a in assistants:
        aid, name = a["assistant_id"], a.get("name") or a["assistant_id"]
        print(f"\n--- assistant {name} ({aid}, graph={a.get('graph_id')}) ---")
        exp = _evaluate_arm(
            make_target(RemoteGraph(aid, client=client, sync_client=sync_client)),
            names, f"assistants-{name}", eval_type="assistants",
            extra={"assistant_id": aid, "assistant_name": name, "graph_id": a.get("graph_id")},
        )
        print(f"    experiment: {exp}")


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--type", choices=["offline", "ab", "assistants"], default="offline", help="eval type (default: offline)")
    p.add_argument(
        "--evaluators", nargs="*", choices=list(ALL), metavar="NAME",
        help=f"subset to run (default: all). Choices: {', '.join(ALL)}",
    )
    p.add_argument(
        "--model-a", type=_spec, default=None, metavar="PROVIDER:MODEL",
        help="first A/B arm (default: the agent's own model)",
    )
    p.add_argument(
        "--model-b", type=_spec, default=None, metavar="PROVIDER:MODEL",
        help="second A/B arm (required for --type ab)",
    )
    p.add_argument(
        "--endpoint", default=os.environ.get("LANGGRAPH_DEPLOYMENT_URL"), metavar="URL",
        help="deployment URL for --type assistants (default: $LANGGRAPH_DEPLOYMENT_URL)",
    )
    p.add_argument("--graph-id", default=None, metavar="ID", help="filter assistants to one graph (--type assistants)")
    p.add_argument("--list", action="store_true", help="list evaluators and exit")
    args = p.parse_args()

    if args.list:
        print("evaluators:", ", ".join(ALL))
        return

    if args.type == "ab":
        if args.model_b is None:
            p.error("--type ab requires --model-b PROVIDER:MODEL (--model-a defaults to the agent's model)")
        model_a = args.model_a
        if model_a is None:
            from llm_research_agent.agent import DEFAULT_MODEL, DEFAULT_PROVIDER

            model_a = (DEFAULT_PROVIDER, DEFAULT_MODEL)
        run_ab(model_a, args.model_b, args.evaluators)
    elif args.type == "assistants":
        if not args.endpoint:
            p.error("--type assistants requires --endpoint URL (or set $LANGGRAPH_DEPLOYMENT_URL)")
        run_assistants(args.endpoint, args.evaluators, args.graph_id)
    else:
        run_offline(args.evaluators)


if __name__ == "__main__":
    main()
