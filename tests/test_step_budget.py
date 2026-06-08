"""Unit tests for `StepBudgetMiddleware._over_budget`."""

from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from llm_research_agent.utils.budget import StepBudgetMiddleware


def _request(messages: list) -> SimpleNamespace:
    return SimpleNamespace(messages=messages)


def test_triggers_when_ai_messages_reach_max_model_turns() -> None:
    middleware = StepBudgetMiddleware(max_model_turns=25, max_graph_steps=60)
    messages = [HumanMessage(content="q")] + [AIMessage(content="x") for _ in range(25)]
    assert middleware._over_budget(_request(messages)) is True


def test_triggers_when_combined_messages_exceed_step_ceiling() -> None:
    middleware = StepBudgetMiddleware(max_model_turns=25, max_graph_steps=60)
    # 20 AIMessages (under max_model_turns) but with heavy tool fanout pushing
    # combined steps over the graph-step ceiling.
    messages = (
        [HumanMessage(content="q")]
        + [AIMessage(content="x") for _ in range(20)]
        + [ToolMessage(content="r", tool_call_id=str(i)) for i in range(40)]
    )
    assert middleware._over_budget(_request(messages)) is True


def test_does_not_trigger_below_both_thresholds() -> None:
    middleware = StepBudgetMiddleware(max_model_turns=25, max_graph_steps=60)
    messages = (
        [HumanMessage(content="q")]
        + [AIMessage(content="x") for _ in range(5)]
        + [ToolMessage(content="r", tool_call_id=str(i)) for i in range(5)]
    )
    assert middleware._over_budget(_request(messages)) is False
