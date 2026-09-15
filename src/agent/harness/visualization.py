"""Create browser-safe links to static sandbox visualizations."""

import logging
import posixpath
import re
from pathlib import PurePosixPath

from langchain.messages import AIMessage, ToolMessage
from langchain.tools import ToolRuntime
from langchain_core.tools import tool
from langgraph.types import Command


logger = logging.getLogger(__name__)

ANALYSIS_ROOT = PurePosixPath("/analysis")
VISUALIZATION_LINK_TTL_SECONDS = 60 * 60
FAVICON = '<link rel="icon" href="data:,">'
SANDBOX_UNAVAILABLE = "the analysis sandbox is unavailable"


def visualization_path(path: str) -> str:
    candidate = PurePosixPath(posixpath.normpath(path))
    if (
        not candidate.is_absolute()
        or candidate.parent == candidate
        or ANALYSIS_ROOT not in (candidate, *candidate.parents)
        or candidate.suffix.lower() not in {".html", ".htm"}
    ):
        raise ValueError("visualizations must be HTML files under /analysis/")
    return str(candidate)


def sandbox_path(path: str) -> str:
    return "/" + str(PurePosixPath(visualization_path(path)).relative_to(ANALYSIS_ROOT))


def share_visualization(sandbox, path: str):
    """Mint or regenerate a one-hour inline link for an existing visualization."""
    path = sandbox_path(path)
    html = sandbox.read(path).decode()
    if FAVICON not in html:
        html, count = re.subn(
            r"<head(?:\s[^>]*)?>", lambda m: m.group() + FAVICON, html, count=1
        )
        if not count:
            html = f"<head>{FAVICON}</head>{html}"
        sandbox.write(path, html)
    return sandbox.generate_download_url(
        path,
        expires_in_seconds=VISUALIZATION_LINK_TTL_SECONDS,
        content_type="text/html",
        content_disposition="inline",
    )


def publish_failed(reason: str, tool_call_id: str) -> Command:
    """Report a failed publish as a tool error the model can still recover from."""
    logger.warning("Publishing a visualization failed (%s).", reason)
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=(
                        f"Error: could not publish the visualization: {reason}. "
                        "Answer the user in text instead of publishing an artifact."
                    ),
                    tool_call_id=tool_call_id,
                )
            ]
        },
        # The tool is return_direct, so a tool result alone ends the run and the
        # user sees nothing; the failure path has to re-enter the model loop.
        goto="model",
    )


def build_share_visualization_link(analysis_sandbox):
    """Build the publish tool bound to a lazily mounted analysis sandbox."""

    @tool(return_direct=True)
    def share_visualization_link(path: str, runtime: ToolRuntime) -> Command:
        """Publish HTML under /analysis/ as the final user-facing response."""
        sandbox = analysis_sandbox.sandbox()
        if sandbox is None:
            return publish_failed(SANDBOX_UNAVAILABLE, runtime.tool_call_id)
        try:
            link = share_visualization(sandbox, path)
        except Exception as exc:  # noqa: BLE001 — a sandbox failure must not end the run
            return publish_failed(f"{type(exc).__name__}: {exc}", runtime.tool_call_id)
        response = f"[Open visualization]({link.download_url})\n\nExpires in one hour."
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Visualization published.", tool_call_id=runtime.tool_call_id
                    ),
                    AIMessage(content=response),
                ]
            }
        )

    return share_visualization_link
