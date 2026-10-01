import unittest

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

from agent.harness.budget import ParallelToolCallCapMiddleware


@tool
def search(query: str) -> str:
    """Search the web."""
    return f"results for {query}"


class ToolCallingFakeModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def _flood(n):
    return AIMessage(
        content="",
        tool_calls=[
            {"name": "search", "args": {"query": f"q{i}"}, "id": f"call_{i}"}
            for i in range(n)
        ],
    )


class ParallelToolCallCapTest(unittest.TestCase):
    def test_trims_flood_to_cap(self):
        update = ParallelToolCallCapMiddleware(max_calls=12).after_model(
            {"messages": [HumanMessage("hi"), _flood(200)]}, None
        )

        self.assertEqual(len(update["messages"][0].tool_calls), 12)

    def test_leaves_small_turns_alone(self):
        update = ParallelToolCallCapMiddleware(max_calls=12).after_model(
            {"messages": [HumanMessage("hi"), _flood(5)]}, None
        )

        self.assertIsNone(update)

    def test_agent_history_has_no_orphaned_tool_calls(self):
        model = ToolCallingFakeModel(messages=iter([_flood(200), AIMessage("done")]))
        agent = create_agent(
            model, tools=[search], middleware=[ParallelToolCallCapMiddleware(max_calls=12)]
        )

        messages = agent.invoke({"messages": [HumanMessage("hi")]})["messages"]

        calls = [c["id"] for m in messages if isinstance(m, AIMessage) for c in m.tool_calls]
        replies = [m.tool_call_id for m in messages if isinstance(m, ToolMessage)]
        self.assertEqual(len(calls), 12)
        self.assertEqual(sorted(calls), sorted(replies))
        self.assertEqual(messages[-1].content, "done")


if __name__ == "__main__":
    unittest.main()
