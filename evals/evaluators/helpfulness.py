"""Helpfulness (openevals RAG_HELPFULNESS_PROMPT) — does the answer actually
address the question? 1 = helpful and on-topic. Needs no reference or retrieval
context (the prompt formats only inputs + outputs). NEW relative to the original suite.
"""

from openevals.prompts import RAG_HELPFULNESS_PROMPT

from evals.shared import make_judge, question

NAME = "helpfulness"


def build():
    judge = make_judge(RAG_HELPFULNESS_PROMPT, NAME)

    def helpfulness(inputs: dict, outputs: dict) -> dict:
        return judge(inputs=question(inputs), outputs=outputs.get("answer", ""))

    return helpfulness
