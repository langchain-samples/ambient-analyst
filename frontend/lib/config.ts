// Client-visible connection config. Defaults route through the same-origin
// proxy (app/api/lg) so the LangSmith key never reaches the browser. Override
// NEXT_PUBLIC_LANGGRAPH_API_URL to point straight at a server (e.g. a local
// `langgraph dev` at http://127.0.0.1:2024) and skip the proxy.
export const API_URL =
  process.env.NEXT_PUBLIC_LANGGRAPH_API_URL ?? "/api/lg";

export const ASSISTANT_ID =
  process.env.NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID ?? "llm_research_agent";
