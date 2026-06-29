"""Evaluator registry.

Convention (strict — keep it that way): each module in this package defines ONE
metric, like a unit test defines one unit. A module exposes:

    NAME     : str   -- the LangSmith feedback key for this metric
    build()  : ()    -- returns a LangSmith-compatible evaluator function

To add a metric: drop a new <metric>.py in here following that shape and add it
to `_MODULES` below. `evals/run.py` discovers everything through `ALL`.
"""

from evals.evaluators import (
    conciseness,
    correctness,
    hallucination,
    helpfulness,
    memory,
)

_MODULES = (correctness, hallucination, conciseness, helpfulness, memory)

# name -> zero-arg builder. Call the builder to get a ready evaluator.
ALL = {m.NAME: m.build for m in _MODULES}
