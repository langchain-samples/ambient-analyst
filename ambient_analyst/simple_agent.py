"""A simple, configurable Ambient Analyst — the deployment's second graph.

A graph factory: the deployment calls `make_agent` per run with the assistant's
config and builds a minimal LangGraph ReAct agent with the selected system
prompt and tools (see `assistant_settings`). Reuses the same Tavily tools, Hub
prompt, and PII redaction as the DeepAgents analyst, but nothing heavier.
"""

import os

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig

from ambient_analyst.utils.assistants import assistant_settings
from ambient_analyst.utils.pii import PIIRedactionMiddleware
from ambient_analyst.utils.retry import rate_limit_retry_middleware

# ponytail: same gateway model init as agent.py, duplicated on purpose so
# importing this graph doesn't pull agent.py's skills or connect its sandbox.
model = init_chat_model(
    model=os.environ.get("AMBIENT_ANALYST_MODEL", "claude-sonnet-4-6"),
    model_provider="anthropic",
    base_url="https://gateway.smith.langchain.com/anthropic",
    api_key=os.getenv("LANGSMITH_API_KEY_GATEWAY")
    or os.getenv("LANGSMITH_API_KEY")
    or os.getenv("LC_GATEWAY_KEY")
    or os.getenv("ANTHROPIC_API_KEY"),
)


def make_agent(config: RunnableConfig):
    system_prompt, tools = assistant_settings(config)
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[rate_limit_retry_middleware(), PIIRedactionMiddleware()],
    )
