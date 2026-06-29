"""Correctness against the golden reference answer (openevals CORRECTNESS_PROMPT).

1 = consistent with the reference and covers the question's key points.
"""

from openevals.prompts import CORRECTNESS_PROMPT

from evals.shared import final_text, make_judge, question

NAME = "correctness"


def build():
    judge = make_judge(CORRECTNESS_PROMPT, NAME)

    def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
        return judge(
            inputs=question(inputs),
            outputs=outputs.get("answer", ""),
            reference_outputs=final_text((reference_outputs or {}).get("messages")),
        )

    return correctness
