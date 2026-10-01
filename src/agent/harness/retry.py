"""Retry model calls on provider rate limits."""

from __future__ import annotations

from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware


def _is_rate_limit(exc: BaseException) -> bool:
    while exc:
        if getattr(exc, "status_code", None) == 429:
            return True
        text = f"{type(exc).__name__}: {exc}".lower()
        if "429" in text or "rate limit" in text or "rate_limit" in text:
            return True
        exc = exc.__cause__ or exc.__context__
    return False


def rate_limit_retry_middleware() -> ModelRetryMiddleware:
    return ModelRetryMiddleware(
        max_retries=6,
        retry_on=_is_rate_limit,
        on_failure="continue",
        initial_delay=2,
        max_delay=30,
    )


def subagent_failure_middleware() -> ToolRetryMiddleware:
    """Return a failed `task` subagent to the parent as an error ToolMessage instead of ending the run."""
    return ToolRetryMiddleware(
        max_retries=0,
        tools=["task"],
        on_failure=lambda exc: (
            f"Subagent failed with {type(exc).__name__}: {exc}. Do not re-dispatch "
            "the same task; continue with the evidence already gathered."
        ),
    )


if __name__ == "__main__":
    class RateLimited(Exception):
        status_code = 429

    assert _is_rate_limit(RateLimited("too many requests"))
    assert _is_rate_limit(Exception("rate_limit_error"))
    assert not _is_rate_limit(Exception("authentication error"))
    print("ok")
