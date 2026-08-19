"""Regression tests for newline-delimited tool results.

Runnable as a plain script (`python tests/test_tool_results.py`) or under pytest.
"""

from __future__ import annotations

import tempfile

from deepagents.backends.filesystem import FilesystemBackend
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ambient_analyst.utils.tool_results import (
    MAX_LINE_CHARS,
    line_delimited,
    line_delimited_tool,
)


class _Args(BaseModel):
    query: str = Field(description="search query")


def _big_payload() -> dict:
    return {
        "results": [
            {
                "url": f"https://example.com/{i}",
                "title": f"result {i}",
                "raw_content": "lorem ipsum dolor sit amet " * 400,
            }
            for i in range(5)
        ]
    }


def test_offloaded_artifact_is_line_paginatable() -> None:
    """A spilled artifact must have many lines and serve non-zero offsets."""
    tool = line_delimited_tool(
        StructuredTool.from_function(
            func=lambda query: _big_payload(),
            name="tavily_search",
            description="search",
            args_schema=_Args,
        )
    )
    artifact = tool.invoke({"query": "corporate margins"})

    lines = artifact.splitlines()
    assert len(lines) > 1, "offloaded artifact must be newline-delimited"
    assert max(len(line) for line in lines) <= MAX_LINE_CHARS

    with tempfile.TemporaryDirectory() as root:
        backend = FilesystemBackend(root_dir=root, virtual_mode=True)
        path = "/large_tool_results/call_test"
        backend.write(path, artifact)

        result = backend.read(path, offset=120, limit=80)
        assert result.error is None, result.error
        assert result.file_data is not None
        assert result.file_data["content"].strip()

        first_page = backend.read(path, offset=0, limit=80)
        assert first_page.file_data["content"] != artifact


def test_line_delimited_preserves_payload_content() -> None:
    rendered = line_delimited({"url": "https://example.com", "text": "a" * 1000})
    assert "https://example.com" in rendered.replace("\n", "")
    assert "a" * 1000 in rendered.replace("\n", "")


if __name__ == "__main__":
    test_offloaded_artifact_is_line_paginatable()
    test_line_delimited_preserves_payload_content()
    print("tool result tests passed")
