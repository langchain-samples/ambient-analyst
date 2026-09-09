# Issue: Build a Resilient Error Handling Model

## Problem

Ambient Analyst has grown several independent failure surfaces without a shared
error handling model. The current code has good local fixes, but the behavior is
inconsistent across startup, agent middleware, Context Hub, sandbox routing,
frontend proxying, and eval entrypoints.

The result is that some failures are correctly downgraded to tool-level errors,
some are logged and ignored, some disable features, and some crash at import time
or bubble up as framework errors. That makes failures harder to triage and lets
SDK shape changes, transient service errors, and optional capability outages
break user-facing runs.

## Current Failure Surfaces

- Required startup dependencies:
  - Prompt Hub pull in `src/agent/agent.py`.
  - Skill repo pulls in `src/agent/agent.py`.
  - Model initialization in `src/agent/agent.py`.

- Optional startup dependencies:
  - LangSmith analysis sandbox creation/start in `src/agent/agent.py`.
  - Memory corpus size check in `src/agent/harness/memory.py`.

- Runtime infrastructure:
  - Context Hub read/write/edit in `src/agent/harness/hub.py`.
  - Hot-path memory append in `src/agent/harness/memory.py`.
  - Model rate limits in `src/agent/harness/retry.py`.
  - LangGraph recursion/step budget in `src/agent/harness/budget.py`.

- User-visible app edges:
  - Next proxy to LangGraph in `src/frontend/app/api/lg/[...path]/route.ts`.
  - LangSmith Custom App bridge calls in `ambient-analyst-review/src/api.ts`.
  - Review UI component-level loading/error state in `ambient-analyst-review/src/App.tsx`.

- Eval and tooling:
  - Preview agent HTTP calls in `src/evals/pr_check.py`.
  - Local agent import/invoke in `src/evals/golden_evals.py`.
  - Context pull/push scripts in `src/agent/harness/context.py`.

## Proposed Error Handling Contract

Use four buckets. Keep this as code conventions first; do not add a large
exception hierarchy unless the buckets stop being enough.

1. Required startup
   - Examples: prompt pull, skill pull, model config.
   - Behavior: fail fast with a short contextual message.
   - Reason: the agent cannot answer correctly without these.

2. Optional capability
   - Examples: analysis sandbox, memory budget measurement.
   - Behavior: log once, disable the route/capability, continue.
   - Reason: a run can still produce useful work.

3. Nonfatal bookkeeping
   - Examples: hot-path memory append, preference extraction persistence.
   - Behavior: never fail the user request; log warning with operation name.
   - Reason: observability/memory should not discard a successful tool result.

4. User-facing upstream
   - Examples: frontend proxy to LangGraph, Custom App bridge calls, eval HTTP calls.
   - Behavior: return or display a small structured error with retry context.
   - Reason: the caller needs a clear actionable failure instead of a stack trace.

## Plan

### Phase 1: Normalize SDK result access

- [ ] Move the dict-or-object result access helper from memory handling into a
      shared harness helper, likely `src/agent/harness/hub.py`.
- [ ] Use it in `_is_retryable_result` so dict-shaped Context Hub errors still
      trigger retries.
- [ ] Use it anywhere Context Hub result fields are read (`error`, `content`,
      `file_data`).
- [ ] Add one small regression check for dict-shaped read/write/edit results.

Acceptance criteria:
- Context Hub object-shaped and dict-shaped results behave identically.
- Transient dict-shaped error results retry.
- Memory append failure never raises into a completed tool call.

### Phase 2: Make startup failures intentional

- [ ] Wrap required startup pulls with a small helper that raises
      `RuntimeError("Failed to initialize <component>: <cause>")`.
- [ ] Keep analysis sandbox startup optional, but expose whether `/analysis/`
      was mounted.
- [ ] Validate required env vars before model/gateway use.

Acceptance criteria:
- Missing prompt/skill/model config fails with one clear startup error.
- Sandbox outage logs once and the agent still starts without `/analysis/`.
- Env var failures point to the missing variable.

### Phase 3: Clean user-facing boundaries

- [ ] Add a `try/catch` around the Next LangGraph proxy fetch.
- [ ] Return `502` with `{ "error": "LangGraph agent unavailable" }` for
      connection failures.
- [ ] Add a tiny `errorMessage(e)` helper in the review app API layer or reuse
      the component helper consistently.
- [ ] Stop swallowing review-app background load failures with only
      `console.error`; surface them in the existing `ErrorBanner` where useful.

Acceptance criteria:
- Local frontend shows a clear agent-unavailable error when LangGraph is down.
- Review app bridge failures render in the UI, not only devtools.
- Existing streaming/SSE proxy behavior remains unchanged on success.

### Phase 4: Remove shared mutable middleware state

- [ ] Change `CitationGuardMiddleware` to derive retrieved URLs/evidence from
      `request.messages` per model call.
- [ ] Avoid accumulating run state on middleware instances unless the state is
      explicitly thread-scoped.
- [ ] Add a small self-check that two synthetic runs cannot share citations.

Acceptance criteria:
- Concurrent runs cannot leak citation evidence through middleware instance state.
- Citation scrubbing behavior is unchanged for a single run.

### Phase 5: Add minimal resilience checks

- [ ] Keep assert-based self-checks for harness modules.
- [ ] Add focused checks for each bucket:
      required startup, optional capability, bookkeeping, user-facing upstream.
- [ ] Do not build a broad test framework unless the repo adopts one.

Acceptance criteria:
- One command can verify the core resilience behavior.
- Each bucket has at least one failure-path check.

## Priority

| Priority | Work | Impact | Risk | Effort |
| --- | --- | ---: | ---: | ---: |
| P0 | Normalize Context Hub result access | 5 | 5 | 1 |
| P0 | Frontend proxy error envelope | 4 | 4 | 1 |
| P1 | Required startup error helper | 4 | 4 | 2 |
| P1 | Remove citation middleware shared state | 4 | 3 | 2 |
| P2 | Review app visible bridge errors | 3 | 3 | 2 |
| P2 | Eval env validation | 2 | 3 | 1 |

## Non-Goals

- No custom exception hierarchy yet.
- No retry framework for every operation.
- No production-grade incident system.
- No broad rewrite of middleware ordering.

## First PR Shape

Keep the first change small:

- Shared `hub_result_value(result, key)` helper.
- Shared `hub_result_content(result)` helper.
- Use both in `hub.py` and `memory.py`.
- Add dict-shaped result tests.

That fixes the bug class that just surfaced without turning resilience work into
an architecture project.
