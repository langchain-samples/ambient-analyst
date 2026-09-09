"""Sandbox path helpers."""

import posixpath


def analysis_path(path: str) -> str:
    raw = path.strip()
    if not raw:
        return "/analysis"
    if not raw.startswith("/"):
        raw = f"/analysis/{raw}"
    normalized = posixpath.normpath("/" + raw.lstrip("/"))
    if normalized != "/analysis" and not normalized.startswith("/analysis/"):
        raise ValueError("Data modeling artifacts must live under /analysis/")
    return normalized
