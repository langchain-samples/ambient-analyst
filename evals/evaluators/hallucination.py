"""Groundedness / no fabricated specifics (openevals HALLUCINATION_PROMPT).

Polarity: HALLUCINATION_PROMPT scores high when the output is *without*
hallucinations, so the feedback key `hallucination_free` means 1 = grounded. The
prompt cross-references claims against ground truth; the golden reference answer
is that ground truth (both `context` and `reference_outputs` are template vars).
"""

from openevals.prompts import HALLUCINATION_PROMPT

from evals.shared import final_text, make_judge, question

NAME = "hallucination_free"


def build():
    judge = make_judge(HALLUCINATION_PROMPT, NAME)

    def hallucination_free(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        reference = final_text((reference_outputs or {}).get("messages"))
        return judge(
            inputs=question(inputs),
            outputs=outputs.get("answer", ""),
            context=reference,
            reference_outputs=reference,
        )

    return hallucination_free
