#!/usr/bin/env bash
#
# Seed LangSmith Engine demo traces against the DEPLOYED llm-research agent.
#
# Fires 30 separate threads at the deployment's HTTP API IN PARALLEL, each
# asking a recency/date-sensitive research question. On the
# `demo/engine-missing-dates` branch, web_search reads the wrong Tavily key so
# every result's `published_date` is null — these queries demand dates, so the
# defect shows up in the traces (null published_date in tool outputs; undated /
# hedged answers). That gives Engine a recurring pattern to detect and fix.
#
# Concurrency: all threads launch at once by default. Set MAX_PARALLEL=N to cap
# in-flight runs (recommended if you hit rate limits or want fewer Context Hub
# memory-write 409s from concurrent runs sharing the same memory backend).
#
# Secrets: the deployment URL is PROMPTED (or read from $DEPLOYMENT_URL) so
# nothing is hardcoded. The LangSmith key is referenced by name from the
# environment ($LANGSMITH_API_KEY) and is never printed.
#
# Usage:
#   export LANGSMITH_API_KEY=...      # or leave it in .env (auto-loaded below)
#   ./evals/seed_demo_traces.sh       # prompts for the deployment URL
#   MAX_PARALLEL=8 ./evals/seed_demo_traces.sh
#
set -uo pipefail

ASSISTANT_ID="llm_research_agent"   # graph id from langgraph.json
RUN_TIMEOUT=600                     # seconds to wait per thread (research runs are long)
MAX_PARALLEL="${MAX_PARALLEL:-0}"   # 0 = no cap (launch all at once)

command -v curl >/dev/null 2>&1 || { echo "curl is required." >&2; exit 1; }
command -v jq   >/dev/null 2>&1 || { echo "jq is required (brew install jq)." >&2; exit 1; }

# --- API key: by name only, never echoed. Auto-load from .env if not exported. ---
if [[ -z "${LANGSMITH_API_KEY:-}" && -f .env ]]; then
  set -a; source .env; set +a
fi
: "${LANGSMITH_API_KEY:?Set LANGSMITH_API_KEY (export it, or add it to .env).}"

# --- Deployment URL: prompted so no endpoint is baked into the repo. ---
DEPLOYMENT_URL="${DEPLOYMENT_URL:-}"
if [[ -z "$DEPLOYMENT_URL" ]]; then
  read -r -p "LangGraph deployment URL (e.g. https://<id>.us.langgraph.app): " DEPLOYMENT_URL
fi
DEPLOYMENT_URL="${DEPLOYMENT_URL%/}"   # strip trailing slash
[[ -n "$DEPLOYMENT_URL" ]] || { echo "No deployment URL provided." >&2; exit 1; }

# --- 30 date-demanding research queries (each forces the agent to need dates) ---
QUERIES=(
  "Give me a timeline of every frontier-model release this quarter, with the exact announcement date next to each entry."
  "What is the most recent Claude model, and on what date was it released? Cite the source and its date."
  "What is the latest Gemini version, and when was it announced? Include the publication date of your source."
  "When did the newest GPT model ship, and how does that date compare to the one before it?"
  "Which models were added to the LMArena leaderboard this month, and on what date did each appear?"
  "Show me the freshest SWE-bench Verified numbers and the date those results were published."
  "What is the newest dedicated reasoning model, and what is its launch date?"
  "What is the most recent open-weight model release, and when was it published?"
  "What did the major AI labs announce this past week? Date every announcement."
  "List the latest frontier-API pricing changes and the effective date of each."
  "What recent context-window increases have been announced, and on what dates?"
  "What is the newest multimodal model, and when was it released? Cite a dated source."
  "What are the most recent GPQA and MMLU-Pro results you can find, and when were they published?"
  "What is Mistral's latest model, and on what date was it released?"
  "What is the most recent Llama release, and when did it come out?"
  "What is the newest model from a Chinese lab (e.g. DeepSeek or Qwen), and its release date?"
  "What do the latest Artificial Analysis rankings look like, and what is the snapshot date?"
  "Summarize the most recent benchmark-contamination or eval-validity news, with dates."
  "What are the latest agentic coding benchmark results (e.g. Terminal-Bench), and when were they published?"
  "What recent AI-lab funding or org news has there been, and on what dates?"
  "Which models have been deprecated most recently, and what are the effective shutdown dates?"
  "What new safety or evaluation frameworks have been released lately, and when?"
  "What are the most recent throughput and latency benchmark updates, and their publication dates?"
  "What recent fine-tuning or distillation releases have there been, with their announcement dates?"
  "What are the latest long-context benchmark results, and when were they published?"
  "What is the newest realtime or voice model, and what is its launch date?"
  "How have the top leaderboard ranks shifted over the past month? Date each change."
  "What is the newest small or on-device model, and when was it released?"
  "What is the most recently published frontier model card, and what is its date?"
  "Give me a chronological summary of the last 14 days in AI model news, with a date on every item."
)

total=${#QUERIES[@]}
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

if [[ "$MAX_PARALLEL" -gt 0 ]]; then
  echo "Firing $total threads at $DEPLOYMENT_URL (assistant: $ASSISTANT_ID), max $MAX_PARALLEL in parallel"
else
  echo "Firing $total threads at $DEPLOYMENT_URL (assistant: $ASSISTANT_ID), all in parallel"
fi
echo

# One thread end-to-end: create thread -> run graph -> record status. Writes its
# result to "$tmpdir/<index>.status" so the parent can tally after `wait`.
run_one() {
  local idx="$1" q="$2"
  local thread_id payload http body

  thread_id="$(curl -sS -X POST "$DEPLOYMENT_URL/threads" \
    -H "x-api-key: $LANGSMITH_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{}' | jq -r '.thread_id // empty')"

  if [[ -z "$thread_id" ]]; then
    echo "[$idx/$total] FAILED to create thread" >&2
    echo "fail" > "$tmpdir/$idx.status"
    return
  fi

  payload="$(jq -n --arg a "$ASSISTANT_ID" --arg c "$q" \
    '{assistant_id:$a, input:{messages:[{role:"user", content:$c}]}, metadata:{demo:"engine-missing-dates"}}')"

  body="$tmpdir/$idx.body"
  http="$(curl -sS -o "$body" -w '%{http_code}' --max-time "$RUN_TIMEOUT" \
    -X POST "$DEPLOYMENT_URL/threads/$thread_id/runs/wait" \
    -H "x-api-key: $LANGSMITH_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload")"

  if [[ "$http" == "200" ]]; then
    echo "[$idx/$total] done (thread $thread_id)"
    echo "ok" > "$tmpdir/$idx.status"
  else
    echo "[$idx/$total] run FAILED (HTTP $http): $(head -c 200 "$body")" >&2
    echo "fail" > "$tmpdir/$idx.status"
  fi
}

i=0
for q in "${QUERIES[@]}"; do
  i=$((i + 1))
  run_one "$i" "$q" &
  # Optional concurrency gate (portable to bash 3.2 / macOS default shell).
  if [[ "$MAX_PARALLEL" -gt 0 ]]; then
    while [[ "$(jobs -rp | wc -l | tr -d ' ')" -ge "$MAX_PARALLEL" ]]; do
      sleep 0.3
    done
  fi
done

wait

ok=0; fail=0
for f in "$tmpdir"/*.status; do
  [[ -f "$f" ]] || continue
  if [[ "$(cat "$f")" == "ok" ]]; then ok=$((ok + 1)); else fail=$((fail + 1)); fi
done

echo
echo "Done. $ok succeeded, $fail failed, $total total."
echo "Filter these in LangSmith by metadata: demo = engine-missing-dates"
