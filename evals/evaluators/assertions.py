"""Grade the agent's answer against free-form assertions saved on the dataset
example (https://docs.langchain.com/langsmith/assertions).

Assertions are English acceptance criteria a reviewer writes in a single-run
annotation queue; LangSmith stores them on the example as
`reference_outputs["assertions"] = [{"key", "comment"}, ...]`. This evaluator
emits ONE binary feedback score per assertion, keyed by the assertion's own
`key`, via an openevals LLM judge prompted with that assertion's `comment`. It
returns the `EvaluationResults` (`{"results": [...]}`) shape so an example with
no assertions is a clean no-op (LangSmith's wrapper rejects a bare `[]`).

`NAME` ("assertions") is just the registry selector — the feedback keys it emits
are the per-assertion keys (e.g. must_cite_source). Examples without assertions
yield no feedback, so it no-ops on the messages-based golden dataset; point it at
an assertions dataset to use it:

    EVAL_DATASET=<assertions-dataset> uv run --env-file .env \
        python evals/run.py --evaluators assertions
"""

from evals.shared import make_judge, question

NAME = "assertions"

# {inputs}/{outputs} are openevals' standard vars; {assertion} is an extra kwarg
# we pass per claim (openevals formats any provided kwargs into the template).
_PROMPT = """You are checking whether a model's answer satisfies one specific \
acceptance criterion (an "assertion") written by a human reviewer.

<question>
{inputs}
</question>

<answer>
{outputs}
</answer>

<assertion>
{assertion}
</assertion>

Return a BINARY score: 1 if the answer satisfies the assertion, 0 if it does \
not. Judge ONLY the assertion above."""


def build():
    judge = make_judge(_PROMPT, "assertion")

    def assertions(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        claims = (reference_outputs or {}).get("assertions") or []
        q, answer = question(inputs), outputs.get("answer", "")
        feedback = []
        for claim in claims:
            result = judge(inputs=q, outputs=answer, assertion=claim.get("comment", ""))
            feedback.append({
                "key": claim.get("key", "assertion"),
                "score": result["score"],
                "comment": result.get("comment", ""),
            })
        # EvaluationResults shape: an empty list here is a valid no-op; a bare
        # [] return is rejected by LangSmith's evaluator wrapper.
        return {"results": feedback}

    return assertions
