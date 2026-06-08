# LangSmith Engine demo — runbook

> **Internal demo asset. Do not merge `demo/engine-missing-dates` into `main`.**
> This branch carries deliberately planted bugs so LangSmith Engine has something
> real to discover, diagnose, and fix in front of a customer. `main` is the clean,
> fixed reference state. Two bugs are planted (see below): a missing-dates
> correctness bug and a 5×-tool-retry latency/cost bug.

> [!IMPORTANT]
> **Keep this file out of Engine's view.** Engine reads the connected source
> repository to diagnose problems. If it scans a file that names the bug, the
> "Engine figured it out on its own" narrative is spoiled. When you connect the
> repo in Engine setup, point the **Code repository subfolder** at
> `llm_research_agent/` (the agent source) rather than the repo root, so this
> runbook and other demo notes stay invisible to Engine.

---

## Planted bug 1 — missing publication dates

**File:** `llm_research_agent/utils/tools.py`, inside `web_search()`.

**The change (one character of intent, easy to miss in review):**

```python
# Correct (on main):
"published_date": r.get("published_date"),

# Planted on this branch:
"published_date": r.get("date"),
```

Tavily returns each result's date under the key `published_date`. Reading
`r.get("date")` returns `None` for **every** result, because `"date"` is not a
key Tavily emits. The `published_date` field in the tool's JSON output is
therefore always `null`.

### Why this is a realistic, easy-to-miss mistake

- The wrong key is a plausible guess — `date` reads as the "obvious" field name,
  and different APIs really do use different keys (`date`, `published`,
  `publishedAt`, `published_date`).
- Nothing crashes. The tool returns well-formed JSON; the only difference is one
  field is consistently `null`.
- Unit tests that assert "results have a `published_date` key" still pass — the
  key exists, it's just always empty.
- Code review slides past it: the surrounding code, the docstring (which still
  promises `published_date`), and the call site all look correct.

### Why it's a real, valuable problem

This agent researches a **fast-moving** LLM landscape and is explicitly
instructed (in its system prompt and `web_search` docstring) to **cite every
claim with a link and a date**, and to record dates in the long-term scorecard.
With dates silently stripped at the tool boundary, the agent can no longer date
anything. Across runs you get a consistent, recurring quality defect:

- answers omit publication dates, or
- the agent hedges / says recency is "unverified," or
- the scorecard accumulates undated entries,

even though the prompt demands dated, sourced claims. It degrades exactly the
capability this agent exists to provide, and it does so quietly.

---

## Planted bug 2 — every tool call retries 5× (latency/cost)

**File:** `llm_research_agent/utils/tools.py`, the `_call_with_retries()` helper
that wraps both `web_search` and `fetch_page`.

**The bug:** the retry loop never stops on success, so every tool invocation
runs all 5 attempts instead of returning on the first one that works.

```python
def _call_with_retries(call):
    """... Returns the response from the first attempt that doesn't raise ..."""
    last_error = None
    response = None
    for _ in range(_MAX_ATTEMPTS):          # _MAX_ATTEMPTS = 5
        try:
            response = call()
        except Exception as exc:
            last_error = exc
        # BUG: no `break` / `return` on success — the loop runs all 5 times.
    if response is None and last_error is not None:
        raise last_error
    return response
```

The fix is one line — `break` (or `return response`) right after a successful
`call()`.

### Why this is a realistic, easy-to-miss mistake

- A retry wrapper for a flaky network client is normal, sensible defensive code.
- The docstring *says* it returns on the first success, so it reads as correct.
- It produces correct *answers* — the agent gets a valid response, just after 5
  identical calls — so no output looks wrong and tests pass.
- The missing `break` is the single most common bug in hand-rolled retry loops;
  it's exactly the kind of thing dropped during a refactor.

### Why it's a real, valuable problem

Every `web_search` and `fetch_page` makes **5×** the Tavily calls it should:
~5× tool latency, ~5× external API cost/quota, and far more total runtime per
research task. It's invisible in the answer but glaring in the traces — a
textbook **Latency / cost** issue for Engine to surface, distinct from bug 1's
correctness defect.

---

## What Engine should surface

Two distinct issues are planted, so Engine should ideally raise both — a nice way
to show it separating a correctness problem from a latency/cost problem.

**Bug 1 — missing dates (correctness):**

- **Category:** a correctness / answer-quality issue (not a hard tool failure).
  Select priorities like **Tool Call Failures** and a custom concern such as
  *"answers must cite publication dates"* during Engine setup to steer it.
- **Diagnosis (expected):** the agent consistently fails to provide publication
  dates despite instructions; root cause traced to `web_search` returning
  `published_date: null` because of the wrong Tavily result key.
- **Proposed fix:** restore `r.get("published_date")`.
- **Suggested evaluator:** asserts that answers citing sources include dates /
  that tool outputs carry non-null `published_date`. This is the regression
  guard that auto-reopens the issue if it returns.
- **Offline examples:** Engine generates ground-truth examples from the failing
  production traces (dated answers as the expected output).

**Bug 2 — 5× tool retries (latency/cost):**

- **Category:** latency / cost / excessive tool calls. Add **Latency** to the
  Engine priorities to steer it.
- **Diagnosis (expected):** every `web_search` / `fetch_page` span makes 5
  identical Tavily calls and takes ~5× as long; root cause traced to the
  `_call_with_retries` loop never breaking on success.
- **Proposed fix:** `break` / `return` on the first successful call.
- **Suggested evaluator:** flag traces whose tool spans show redundant repeated
  calls or anomalously high tool latency.

---

## Running the demo

1. **Be on the bug branch.**
   ```bash
   git checkout demo/engine-missing-dates
   ```

2. **Seed recurring traces against the deployed agent.** Engine surfaces
   *recurring* patterns, so the script fires 30 date-demanding research
   questions at the deployment **in parallel** — these force the agent to need
   the `published_date` that the bug nulls out, so the defect shows up in every
   trace. It prompts for the deployment URL (nothing hardcoded) and reads
   `LANGSMITH_API_KEY` from the environment / `.env`:
   ```bash
   export LANGSMITH_API_KEY=...          # or leave it in .env
   ./evals/seed_demo_traces.sh           # prompts for the deployment URL
   MAX_PARALLEL=8 ./evals/seed_demo_traces.sh   # cap in-flight runs (fewer 409s)
   ```
   All 30 launch at once by default; set `MAX_PARALLEL=N` to throttle (concurrent
   runs share the Context Hub memory backend, so a high fan-out produces some
   harmless memory-write 409s).
   Traces land in the **tracing project configured on the deployment**, and each
   run is tagged `metadata.demo = engine-missing-dates` for easy filtering. For a
   clean per-demo slate, point the deployment at a fresh `LANGSMITH_PROJECT`
   before seeding (or just filter by the metadata tag).

3. **Set up Engine on that project.** In LangSmith → Tracing → *(the demo
   project)* → **Engine** tab → connect the repo with subfolder
   `llm_research_agent/`, pick priorities (add the custom *"answers must cite
   publication dates"* concern), **Start Analyzing**. Allow up to ~20 min for the
   first scan.

4. **Walk the customer through the issue:** diagnosis → Linked traces (point out
   the `published_date: null` in tool outputs and the undated answers) →
   **Proposed Fix** → **Open PR** → **Suggested Evaluator** → **Offline
   examples**.

---

## Resetting between demos (zero re-authoring)

- Easiest: use a **new `LANGSMITH_PROJECT` name** each run (step 2). Engine
  analyzes per project, so a fresh project = a fresh detection from scratch.
- Alternatively, in Engine settings use **Delete all issues**.
- Discard or close the PR Engine opened during the demo; **do not merge it into
  `main`**. The `demo/engine-missing-dates` branch stays broken and ready for the
  next run.

## The fixes (for reference / what "after" looks like)

`main` is the clean reference. To show the fixed state live, check out `main`, or
apply Engine's PRs against a throwaway branch.

Bug 1 — restore the correct Tavily key in `web_search`:
```python
"published_date": r.get("published_date"),
```

Bug 2 — stop the retry loop on the first success in `_call_with_retries`:
```python
        try:
            response = call()
            break          # success — don't keep retrying
        except Exception as exc:
            last_error = exc
```
