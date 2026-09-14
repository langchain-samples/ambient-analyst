"""Create browser-safe links to static sandbox visualizations."""

import posixpath
import re
from pathlib import PurePosixPath


ANALYSIS_ROOT = PurePosixPath("/analysis")
VISUALIZATION_LINK_TTL_SECONDS = 60 * 60
FAVICON = '<link rel="icon" href="data:,">'


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
