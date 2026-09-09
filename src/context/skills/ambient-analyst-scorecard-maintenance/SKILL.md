---
name: ambient-analyst-scorecard-maintenance
description: The schema for the long-term model scorecard at /memory/scorecard.md and how to read and update it safely. Use whenever you verify a model's performance, find a new leader for a category, or need to record or revise scorecard entries.
---

# Scorecard Maintenance

The scorecard (`/memory/scorecard.md`) is your durable, long-term memory of the best models per category. It is loaded into your context every run and persists to the LangSmith Context Hub when you write to it. Treat it as a living dataset: append and revise carefully, never overwrite blindly.

## When to update

- You verified a model's benchmark result or capability from a credible source.
- A new model takes the lead in a category, or a new credible contender appears.
- An existing entry is stale (see freshness rule) and you re-verified it.
- You found a correction to an existing entry (wrong figure, better source).

Do **not** record unverified, single-source-marketing, or speculative numbers as facts. If you must note them, mark them clearly as unverified.

## The schema

The file is organized by **category**. Each category has a ranked table of models. Keep this exact structure so entries stay machine-readable and diffable:

```markdown
# Model Scorecard

_Last reviewed: YYYY-MM-DD_

## <Category, e.g. Coding / agentic>

_Primary metric: <e.g. SWE-bench Verified>. Updated: YYYY-MM-DD_

| Rank | Model (version) | Lab | Key metric | Score | Source type | Verified | Source URL | Notes / caveats |
|------|-----------------|-----|------------|-------|-------------|----------|------------|-----------------|
| 1 | Example 4.8 | LabCo | SWE-bench Verified | 72.5% | independent | 2026-05-30 | https://... | harness: agentic scaffold |
| 2 | ... | ... | ... | ... | self-reported | 2026-05-20 | https://... | upper bound; not independently confirmed |

## <Next category>
...

## Changelog
- YYYY-MM-DD: what changed and why (URL).
```

Field rules:

- **Source type**: `independent` or `self-reported` (per the ambient-analyst-benchmark-analysis skill). Never blur the two.
- **Verified**: the date you confirmed the figure from the cited source.
- **Notes/caveats**: harness/scaffold, contamination/saturation risk, confidence-interval overlap, price/latency flags.

Suggested categories (add more as needed): Coding / agentic, Reasoning & math, Long-context, Multimodal/vision, Cost-efficiency, Open-weights, Overall (human preference / LMArena).

## How to update safely

1. **Read first.** `read_file` `/memory/scorecard.md` before editing. (It's also already in your loaded memory, but re-read to edit precisely.)
2. **Edit, don't clobber.** Use `edit_file` for targeted changes to one row or one category. Use `write_file` only when creating the file or doing a wholesale, intentional restructure.
3. **Never silently delete a data point.** If a figure changes or an entry drops in rank, update it AND add a one-line **Changelog** entry with the date, what changed, and the source URL.
4. **Always stamp dates.** Update the category's `Updated:` line and the file's `Last reviewed:` line when you touch them.
5. **Keep it comparable.** Within a category, use one primary metric so ranks mean something. Note in caveats if an entry's figure comes from a different harness.

## Freshness rule

LLM standings go stale fast. When you load the scorecard:

- Flag any entry whose `Verified` date is **&gt; \~30 days old** as due for re-verification.
- If the user's question depends on a stale entry, re-verify it with `web_search` before answering, then update the row.

## After updating

State in your answer exactly what you changed (which rows/categories) and what remains stale or uncertain. See the `ambient-analyst-continuous-learning` skill for what else to capture beyond the scorecard.