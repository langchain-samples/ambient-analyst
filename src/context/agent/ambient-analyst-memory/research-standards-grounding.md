# Research Standards — Grounding & Memory-Write Guard

This file supplements the Research Standards section of AGENTS.md. It is a hard, non-negotiable policy that exists because the agent has been observed asserting specific figures, dates, percentages, and named-source attributions that do not appear in any same-session tool result, and then persisting them to memory as "verified."

## Grounding rule for final answers
- Every specific figure, date, percentage, currency/dollar amount, index level, correlation, statistic, or named-source attribution (e.g. BlackRock, J.P. Morgan, Munich Re, IEA, EIA) in a final answer MUST be backed by a tool result retrieved in the SAME session.
- If a figure or attribution is not present in a same-session tool result, either omit it or explicitly label it "from background knowledge, unverified this session."
- Never present a parametric-knowledge figure with a confident named-source attribution.
- Put an inline citation (the retrieved URL or a clearly identified retrieved source) next to each specific figure used.

## Memory-write guard
- Only persist a figure, date, percentage, or named-source attribution to memory as "verified" when it is backed by a same-session tool result.
- Unverified or background-knowledge figures MUST NOT be written to memory as verified. Omit them, or write them with an explicit "unverified" label so they cannot be recycled as verified fact on future runs.
- A figure already stored in memory counts as verified only if it was written with a source and verification date; otherwise treat it as background and re-confirm this session before restating it as fact.
