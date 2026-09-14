---
name: ambient-analyst-model-evaluation
description: How to research and compare current large language models — gathering capabilities, benchmark results, pricing, context, and modalities into a fair, sourced comparison. Use whenever the user asks which model is best for a task, or to compare two or more models.
---

# Model Evaluation

A repeatable workflow for answering "which model is best for X" with sourced, dated evidence rather than vibes or stale recall.

## When to use

- "Which model is best for coding / reasoning / agents / long context / cost?"
- "Compare model A vs model B vs model C."
- "Is there anything newer/better than X for Y?"

## Step 1 — Frame the question by use case

There is no single "best" model. Pin down the axis that matters before searching:

- **Capability domain**: coding, agentic/tool use, math/reasoning, long-context retrieval, multilingual, vision/multimodal, writing, instruction following.
- **Constraints**: cost per token, latency/throughput, context window, open weights vs API-only, on-prem/licensing, rate limits, data-retention/privacy.
- **Deployment**: API, local/open-weights, or via a specific platform.

If the user didn't specify, state the axis you're optimizing and why.

## Step 2 — Pull the current field (don't trust memory)

This field changes weekly. Always verify with `tavily_search` and corroborate across ≥2 independent sources:

- Aggregators / leaderboards: **Artificial Analysis**, **LMArena** (human preference Elo), **OpenRouter** usage rankings, domain leaderboards (e.g. **SWE-bench**, **Aider polyglot**, **GPQA**, **LiveCodeBench**).
- Primary sources: the lab's model card / release post / pricing page for the authoritative spec, price, and self-reported scores.
- Independent evals: third-party runs that don't come from the model's own lab.

Prefer the **scorecard** first (`/memories/agent/scorecard.md`) — if it has a recent, verified entry, start there and only re-verify what's stale.

## Step 3 — Capture a comparable record per model

For each candidate, collect (with a source URL + date for every figure):

- Model name + exact version, lab, release date.
- Headline benchmark scores **relevant to the use case** — note whether each is self-reported or independent (see the `benchmark-analysis` skill).
- Context window (input/output limits), modalities, tool-use/agent support.
- Price (input/output per 1M tokens), and latency/throughput if relevant.
- Open weights vs API-only, license.
- Known weaknesses / caveats.

## Step 4 — Compare fairly

- Compare **like for like**: same benchmark, same harness/settings, same date range. Don't put a lab's self-reported number next to an independent number without flagging it.
- Weight by the user's use case, not by the headline aggregate score.
- Distinguish **statistically meaningful** gaps from noise (LMArena Elo and small benchmark deltas are often within confidence intervals — say so).
- Note recency: a model from 2 weeks ago may already be beaten.

## Step 5 — Answer, then persist

- Give a direct recommendation for the stated use case, with the one or two runners-up and *why* you'd switch.
- Cite every figure (URL + date).
- Update `/memories/agent/scorecard.md` per the `scorecard-maintenance` skill, and log durable learnings per `continuous-learning`.

## Common pitfalls

- Treating one aggregate leaderboard as ground truth across all tasks.
- Quoting a self-reported score as if it were independently verified.
- Ignoring price/latency when the user cares about production cost.
- Reporting a ranking without a date — making it impossible to know when it goes stale.
