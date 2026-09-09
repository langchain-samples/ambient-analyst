---
name: ambient-analyst-landscape-mapping
description: Who the major players are in the LLM field — frontier labs, their model families, open-weights players, and how to track new releases and shifts. Use when the user asks who the major players are, about a specific lab, or for a state-of-the-landscape overview.
---

# Landscape Mapping

How to give an accurate, current map of who builds frontier and notable LLMs and what they've shipped — without relying on stale recall.

## When to use

- "Who are the major players / labs?"
- "What's the state of the field right now?"
- "What has released recently?"
- Establishing context before a model comparison.

## The major players (verify current model versions before quoting)

Frontier / API-first labs and their flagship families (confirm latest versions and dates with `web_search`, `topic="news"`):

- **Anthropic** — Claude family (Opus / Sonnet / Haiku tiers).
- **OpenAI** — GPT family and reasoning ("o"-series) models.
- **Google DeepMind** — Gemini family (Pro / Flash tiers).
- **Meta** — Llama family (open weights).
- **Mistral AI** — open and commercial models.
- **xAI** — Grok family.
- **DeepSeek** — open-weights reasoning/coding models.
- **Alibaba** — Qwen family (open weights, many sizes).
- **Cohere** — enterprise/RAG-focused (Command family).

Also track: notable open-weights releases, regional leaders, and inference/hosting players (Together, Fireworks, Groq, OpenRouter) that affect price/latency.

> This list is a starting point as of authoring. **Always re-verify** current flagship versions, who leads which axis, and any new entrants — the roster and rankings shift constantly.

## What to capture per player

- Lab name, flagship family, current top model + version + release date.
- Open weights vs API-only; licensing if open.
- Where they currently lead (coding, reasoning, cost, long context, multimodal).
- Recent notable releases and direction of travel.
- Source URL + date for each.

## How to track releases and shifts

- `web_search` with `topic="news"` for " new model " and recent "frontier model release" roundups.
- Check lab blogs/model cards (primary source) and aggregators (Artificial Analysis, LMArena) for where each currently ranks.
- Cross-reference the **scorecard** (`/memory/scorecard.md`) for which player holds each category, and update it when leadership changes.

## Reporting

- Group by what the user asked (by lab, by capability, or "who leads right now").
- For "who leads X", point to the scorecard's category winner with its source + date, and note runners-up.
- Flag entries that are stale and due for re-verification.

## Pitfalls

- Naming a model version from memory — versions churn; verify.
- Conflating "biggest/most famous lab" with "currently best at task X".
- Ignoring open-weights players when the user cares about self-hosting or cost.