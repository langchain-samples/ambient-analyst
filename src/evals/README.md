# Offline evals with the LangSmith SDK

Offline evals run your agent over a fixed **dataset** of example inputs, score
every output with **evaluators**, and record the results as an **experiment**
in LangSmith. You can then compare experiments side by side (prompt change vs.
baseline, model A vs. model B, PR vs. main).

```
src/evals/
├── evaluators.py    # scoring functions, shared by both runners
├── run_local.py     # target = agent built in-process
└── run_deployed.py  # target = agent running on a LangSmith Deployment
```

## Setup

```bash
uv sync
```

Add these to `.env` at the repo root:

```bash
LANGSMITH_API_KEY=lsv2_...
DEPLOYMENT_URL=https://<your-deployment>.us.langgraph.app   # only for run_deployed
ASSISTANT_ID=ambient-analyst                               # optional
```

`run_local` also needs the agent's own environment variables (model and Tavily
keys and so on), because it builds the agent in this process.

## Run

```bash
# Check that the evaluators work without calling the agent or LangSmith
uv run python -m src.evals.evaluators

# Evaluate the agent in-process. --repetitions runs each example N times to measure variance.
uv run python -m src.evals.run_local --repetitions 3

# Evaluate a deployed agent (the CI workflow runs this one)
uv run python -m src.evals.run_deployed
```

Each run prints a link to its experiment. Open **Datasets & Experiments →
ambient-analyst-golden** in LangSmith to see and compare all experiments.

## How it works

Both runners make a single `Client().evaluate(...)` call:

```python
Client().evaluate(
    target,                      # dict of example inputs -> dict of outputs
    data="ambient-analyst-golden",
    evaluators=EVALUATORS,       # each scores one output
    experiment_prefix="ambient-analyst-local",
    max_concurrency=1,
)
```

**Dataset.** Each example's `inputs` holds the agent's input state, for example
`{"messages": [{"type": "human", "content": "..."}]}`. LangSmith passes
`inputs` to `target` unchanged. To build your own dataset, run the agent, find
good traces in LangSmith, and add them with **Add to Dataset**. You can also
create examples in code:

```python
from langsmith import Client

client = Client()
dataset = client.create_dataset("my-golden-set")
client.create_examples(
    dataset_id=dataset.id,
    examples=[{"inputs": {"messages": [{"type": "human", "content": "How do rate cuts affect SaaS multiples?"}]}}],
)
```

**Target.** A function from inputs to outputs. `run_local` calls
`agent.invoke(inputs)`. `run_deployed` calls the deployment with
`langgraph_sdk`'s `runs.wait`. If the target raises an exception, LangSmith
records the error on that row and runs the remaining rows.

**Evaluators.** Plain functions that LangSmith calls with whichever of
`inputs`, `outputs` and `reference_outputs` they declare as parameters. The
return value is the score, and the function name is the feedback key. The
evaluators in `evaluators.py` are cheap regex checks. Each one tests a single
quality the analyst's answers should have:

| Key | Checks that the answer… |
| --- | --- |
| `substantive_answer` | is at least 500 characters |
| `source_grounding` | cites sources (URLs, markdown links, "according to") |
| `dated_evidence` | mentions a year or a month |
| `quantitative_evidence` | includes numbers ($, %, bps, millions…) |
| `uncertainty_or_caveat` | states confidence, risks or caveats |

To add an evaluator, write a function and add it to `EVALUATORS`. A reference
check looks like this:

```python
def mentions_expected_ticker(outputs: dict, reference_outputs: dict) -> bool:
    return reference_outputs["ticker"] in final_answer(outputs)
```

You can also use an LLM as the judge, for example with `openevals`, which is
already a dependency:

```python
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

correctness = create_llm_as_judge(prompt=CORRECTNESS_PROMPT, model="openai:<model>", feedback_key="correctness")
```

## CI

`.github/workflows/deploy.yml` runs `run_deployed` on every PR to `main`. The
job needs `LANGSMITH_API_KEY` and `DEPLOYMENT_URL` as repository secrets,
passed to the job through `env:`.
