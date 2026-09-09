---
name: ambient-analyst-benchmark-analysis
description: The major LLM benchmarks and how to judge whether a benchmark result is trustworthy — contamination, saturation, self-reported vs independent, harness sensitivity, and construct validity. Use whenever a benchmark score is cited, compared, or when the user asks how good or valid a benchmark is.
---

\# Benchmark Analysis

A benchmark score is a **claim**, not a fact. This skill is how you read, compare, and critique benchmarks so you don't launder marketing numbers into conclusions.

\## When to use

\- A benchmark score is being cited or compared.

\- "What are the best benchmarks?" / "Can I trust benchmark X?"

\- Any model recommendation that leans on benchmark numbers.

\## Map of the major benchmarks (verify specifics before quoting)

Categories and representative benchmarks (always confirm current versions and numbers via `web_searchfetch_page` — these evolve):

\- **General knowledge / reasoning**: MMLU and MMLU-Pro, GPQA Diamond (graduate-level science), BIG-Bench Hard, HLE ("Humanity's Last Exam").

\- **Math**: GSM8K (largely saturated), MATH, AIME-style competition sets.

\- **Coding**: SWE-bench (and SWE-bench Verified) for real GitHub issue fixing, LiveCodeBench (contamination-resistant, time-windowed), Aider polyglot, HumanEval/MBPP (older, largely saturated).

\- **Agentic / tool use**: tau-bench, GAIA, WebArena, tool-calling suites.

\- **Long context**: RULER, needle-in-a-haystack variants, LongBench.

\- **Human preference (crowd)**: LMArena (Chatbot Arena) Elo — preference, not correctness.

\- **Aggregators**: Artificial Analysis (blends quality, price, speed).

\## How to judge validity — the checklist

Run a cited score through these before trusting it:

1\. **Source independence.** Is this self-reported by the model's lab, or run by an independent third party? Self-reported numbers use the lab's own harness, prompts, and sometimes best-of-N — treat as an upper bound, flag clearly.

2\. **Contamination.** Could the test data be in the training set? Public, long-lived benchmarks (MMLU, HumanEval, GSM8K) are likely partly contaminated. Prefer time-windowed / held-out benchmarks (LiveCodeBench, fresh AIME years) for recency.

3\. **Saturation.** If top models all score &gt;90%, the benchmark has stopped discriminating — small gaps are noise. Say so; don't rank on a saturated test.

4\. **Harness / prompt sensitivity.** Scores swing with prompt format, few-shot count, chain-of-thought, scaffolding, and parsing of the answer. Compare only same-harness results. "SWE-bench with a custom agent scaffold" ≠ "raw model".

5\. **Construct validity.** Does the benchmark measure what its name implies and what the user cares about? Multiple-choice MMLU ≠ real reasoning; a coding benchmark on isolated functions ≠ working in a large repo.

6\. **Statistical significance.** Small N and small deltas → within the confidence interval. LMArena publishes CIs; respect them. Don't call a 5-Elo gap a "win".

7\. **Gaming / overfitting.** Watch for training specifically to a popular benchmark, or eval-only checkpoints. Cross-check against held-out or human evals.

8\. **Recency.** Note the date and the model versions tested; leaderboards lag new releases.

\## How to report a benchmark claim

\- State the number, the **exact benchmark + version**, the **source + date**, and whether it's **self-reported or independent**.

\- Add the relevant validity caveat (contamination / saturation / harness / CI).

\- When comparing, only line up like-for-like results, and prefer independent + contamination-resistant benchmarks for the headline.

\## One-line heuristics

\- Trust **independent, contamination-resistant, unsaturated** benchmarks most.

\- Treat **self-reported** numbers as upper bounds.

\- Use **LMArena** for "what do people prefer", not "what is correct".

\- Use **Artificial Analysis** for a quick price/speed/quality blend, not as the final word on a specific capability.