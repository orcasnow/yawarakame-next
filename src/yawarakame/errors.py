from __future__ import annotations

import re


_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_ ]?key(?:\s+provided)?\s*[:=]\s*)[^'\s,}]+"),
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s,}]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]+\b"),
)


def safe_error_message(exc: BaseException) -> str:
    """Return an actionable error message without echoing credentials."""
    status_code = getattr(exc, "status_code", None)
    if status_code == 401:
        return (
            "OpenAI APIの認証に失敗しました（401）。"
            "OPENAI_API_KEYが有効なキーか確認してください。"
        )

    message = str(exc)
    for pattern in _SECRET_PATTERNS:
        message = pattern.sub(
            lambda match: f"{match.group(1)}[REDACTED]" if match.lastindex else "[REDACTED]",
            message,
        )
    return message
