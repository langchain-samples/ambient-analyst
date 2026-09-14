import os

from managed_deepagents import define_deep_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilyExtract, TavilySearch

from middleware.budget import RecursionFloorMiddleware, StepBudgetMiddleware
from middleware.citations import CitationGuardMiddleware
from middleware.pii import PIIRedactionMiddleware
from middleware.retry import rate_limit_retry_middleware
from tools.context import run_context_interpreter

# LangSmith Gateway serves this model on your workspace's Gateway Credits, so
# the agent needs no model provider key of its own — only a LangSmith one.
#
# The key is read from LANGSMITH_GATEWAY_API_KEY rather than LANGSMITH_API_KEY:
# the latter is reserved by the platform, so `mda deploy` never forwards it, and
# the one a deployment is issued cannot reach the gateway. Put your own
# LangSmith API key under both names in `.env`.
api_key = os.environ.get(
    "LANGSMITH_GATEWAY_API_KEY",
    "missing-langsmith-gateway-api-key",
)

# The gateway speaks the OpenAI API, which is why an OpenAI client addresses it.
base_url = "https://gateway.smith.langchain.com/v1"

agent = define_deep_agent(
    name="ambient-analyst-managed",
    model=ChatOpenAI(
        model="openai/gpt-5.6-luna",
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "X-Tenant-ID": os.environ.get(
                "GATEWAY_WORKSPACE_ID", os.environ.get("LANGSMITH_WORKSPACE_ID", "")
            )
        },
    ),
    tools=[
        TavilySearch(max_results=5),
        TavilyExtract(extract_depth="advanced", format="markdown"),
        run_context_interpreter,
    ],
    subagents=[
        {
            "name": "macro-analysis-worker",
            "description": "Analyze one company, industry, country, source, or scenario for a comparative research task.",
            "system_prompt": "You are a macroeconomic and business analysis specialist. Separate facts from inference, quantify material drivers where possible, identify risks and counterarguments, and cite dated primary sources. Return a concise analyst brief.",
        }
    ],
    middleware=[
        rate_limit_retry_middleware(),
        PIIRedactionMiddleware(),
        CitationGuardMiddleware(),
        RecursionFloorMiddleware(),
        StepBudgetMiddleware(max_model_turns=25),
    ],
)
