"""Conciseness (openevals CONCISENESS_PROMPT) — no padding, hedging, or
meta-commentary. 1 = tight. Needs no reference. NEW relative to the original suite.
"""

from openevals.prompts import CONCISENESS_PROMPT

from evals.shared import make_judge, question

NAME = "conciseness"


def build():
    judge = make_judge(CONCISENESS_PROMPT, NAME)

    def conciseness(inputs: dict, outputs: dict) -> dict:
        return judge(inputs=question(inputs), outputs=outputs.get("answer", ""))

    return conciseness
