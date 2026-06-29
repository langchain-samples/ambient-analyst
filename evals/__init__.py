"""Eval suite for the LLM research agent.

Layout:
- run.py            single entrypoint; flags pick the eval type (--type, --evaluators)
- shared.py         constants, message-state helpers, gateway judge + target factory
- evaluators/       one module per metric (the registry is evaluators.ALL)
- datasets/         the golden snapshot + the script that syncs it from LangSmith
- online_memory_eval.py   standalone server-side evaluator, uploaded separately

Package marker so the entrypoints can share `evals.shared` / `evals.evaluators`.
Not shipped in the wheel — pyproject's package `include` filter keeps the deploy
build scoped to `llm_research_agent*`.
"""
