#!/usr/bin/env bash
#
# Seed LangSmith Engine demo traces against the DEPLOYED llm-research agent.
#
# Fires ~a dozen separate threads at the deployment's HTTP API, each asking a
# recency/date-sensitive research question. On the `demo/engine-missing-dates`
# branch, web_search reads the wrong Tavily key so every result's
# `published_date` is null — these queries demand dates, so the defect shows up
# in the traces (null published_date in tool outputs; undated / hedged answers).
# That gives Engine a recurring pattern to detect, diagnose, and fix.
#
# Secrets: the deployment URL is PROMPTED (or read from $DEPLOYMENT_URL) so
# nothing is hardcoded. The LangSmith key is referenced by name from the
# environment ($LANGSMITH_API_KEY) and is never printed.
#
# Usage:
#   export LANGSMITH_API_KEY=...      # or leave it in .env (auto-loaded below)
#   ./evals/seed_demo_traces.sh       # prompts for the deployment URL
#
set -uo pipefail

ASSISTANT_ID="llm_research_agent"   # graph id from langgraph.json
RUN_TIMEOUT=600                     # seconds to wait per thread (research runs are long)

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

# --- Date-demanding research queries (each forces the agent to need dates) ---
QUERIES=(
  "Which LLMs were released in the last 30 days, and what is the exact announcement date for each?"
  "Give me a timeline of major frontier-model releases in 2026 so far, with the publication date next to every entry."
  "What is the most recent Claude model, and on what date was it released? Cite the source and its date."
  "List the newest models added to the LMArena leaderboard and the date each one appeared."
  "What changed in the LLM landscape this past week? Date every development you mention."
  "When did the latest GPT and Gemini models ship, and which came out more recently?"
  "Show me the freshest SWE-bench results and the date those numbers were published."
  "What are the latest benchmark scores for Claude Opus 4.8, and when was each figure published?"
  "Rank today's top 5 frontier models and note each model's release date."
  "Which lab has shipped most recently, and on exactly what date?"
  "Summarize this month's AI model announcements in chronological order, with a date on each."
  "What is the newest open-weight model, and when was it published? Include the source date."
)

total=${#QUERIES[@]}
echo "Firing $total threads at $DEPLOYMENT_URL (assistant: $ASSISTANT_ID)"
echo

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

ok=0; fail=0; i=0
for q in "${QUERIES[@]}"; do
  i=$((i + 1))

  # 1) Create a fresh thread for this query.
  thread_id="$(curl -sS -X POST "$DEPLOYMENT_URL/threads" \
    -H "x-api-key: $LANGSMITH_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{}' | jq -r '.thread_id // empty')"

  if [[ -z "$thread_id" ]]; then
    echo "[$i/$total] FAILED to create thread" >&2
    fail=$((fail + 1)); continue
  fi
  echo "[$i/$total] thread $thread_id"
  echo "          q: $q"

  # 2) Run the graph on that thread and block until it finishes.
  payload="$(jq -n --arg a "$ASSISTANT_ID" --arg c "$q" \
    '{assistant_id:$a, input:{messages:[{role:"user", content:$c}]}, metadata:{demo:"engine-missing-dates"}}')"

  http="$(curl -sS -o "$tmp" -w '%{http_code}' --max-time "$RUN_TIMEOUT" \
    -X POST "$DEPLOYMENT_URL/threads/$thread_id/runs/wait" \
    -H "x-api-key: $LANGSMITH_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$payload")"

  if [[ "$http" == "200" ]]; then
    echo "          done (HTTP 200)"
    ok=$((ok + 1))
  else
    echo "          run FAILED (HTTP $http): $(head -c 300 "$tmp")" >&2
    fail=$((fail + 1))
  fi
  echo
done

echo "Done. $ok succeeded, $fail failed, $total total."
echo "Filter these in LangSmith by metadata: demo = engine-missing-dates"
