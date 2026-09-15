"""Tests for degraded-mode behavior when the analysis sandbox will not mount."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, List

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.composite import CompositeBackend
from deepagents.backends.protocol import ReadResult, WriteResult
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from agent.harness.sandbox import AnalysisSandbox
from agent.harness.visualization import build_share_visualization_link


class _FakeSandboxBackend:
    def __init__(self, sandbox: Any) -> None:
        self.sandbox = sandbox
        self.written: list[tuple[str, str]] = []

    def read(self, file_path, offset=0, limit=2000):
        return ReadResult(file_data={"content": "chart"})

    def write(self, file_path, content):
        self.written.append((file_path, content))
        return WriteResult(path=file_path)


class _ScriptedModel(BaseChatModel):
    """Chat model that replays a fixed list of AI messages."""

    responses: List[AIMessage] = []
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        message = self.responses[min(self.calls, len(self.responses) - 1)]
        object.__setattr__(self, "calls", self.calls + 1)
        return ChatResult(generations=[ChatGeneration(message=message)])


class _FakeSandbox:
    def read(self, path):
        return b"<html><head></head><body>chart</body></html>"

    def write(self, path, content):
        pass

    def generate_download_url(self, path, **kwargs):
        return SimpleNamespace(download_url="https://sandbox.test/chart.html")


def _always_down():
    raise RuntimeError("sandbox mount failed")


def _publish_agent(analysis_sandbox, answer):
    model = _ScriptedModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "share_visualization_link",
                        "args": {"path": "/analysis/chart.html"},
                        "id": "call_1",
                    }
                ],
            ),
            AIMessage(content=answer),
        ]
    )
    return create_deep_agent(
        model=model, tools=[build_share_visualization_link(analysis_sandbox)]
    )


def test_unmounted_analysis_route_errors_instead_of_falling_through():
    backend = CompositeBackend(
        default=StateBackend(),
        routes={"/analysis/": AnalysisSandbox(_always_down, _FakeSandboxBackend)},
    )

    write = backend.write("/analysis/chart.html", "<html></html>")
    read = backend.read("/analysis/chart.html")

    assert write.path is None
    assert "analysis sandbox is unavailable" in write.error
    assert "analysis sandbox is unavailable" in read.error


def test_mount_is_retried_and_cached_after_it_recovers():
    attempts = []

    def _down_once():
        attempts.append(None)
        if len(attempts) == 1:
            raise RuntimeError("sandbox mount failed")
        return "sandbox-handle"

    analysis_sandbox = AnalysisSandbox(_down_once, _FakeSandboxBackend)

    assert analysis_sandbox.available is False
    assert analysis_sandbox.available is True
    assert analysis_sandbox.sandbox() == "sandbox-handle"
    assert len(attempts) == 2

    result = analysis_sandbox.write("/chart.html", "<html></html>")
    assert result.error is None


def test_agent_answers_in_text_when_the_sandbox_is_unavailable():
    agent = _publish_agent(
        AnalysisSandbox(_always_down, _FakeSandboxBackend),
        "A put is an option to sell at a set strike.",
    )

    messages = agent.invoke({"messages": [{"role": "user", "content": "visualize it"}]})[
        "messages"
    ]

    tool_message = next(m for m in messages if m.type == "tool")
    assert "could not publish the visualization" in tool_message.content
    assert messages[-1].type == "ai"
    assert messages[-1].content == "A put is an option to sell at a set strike."


def test_agent_returns_the_link_when_the_sandbox_is_mounted():
    agent = _publish_agent(
        AnalysisSandbox(_FakeSandbox, lambda sandbox: sandbox), "follow-up"
    )

    messages = agent.invoke({"messages": [{"role": "user", "content": "visualize it"}]})[
        "messages"
    ]

    assert any(
        "https://sandbox.test/chart.html" in m.content
        for m in messages
        if m.type == "ai"
    )
