"""Token 估算与上下文预检。"""

from __future__ import annotations

from src.core.exceptions import AppError, token_limit_error

# 中文等 CJK 文本启发式：每字符约 0.6 token（偏保守）
_CHARS_PER_TOKEN = 1 / 0.6


def estimate_request_tokens(
    document_text: str,
    system_prompt: str,
    extra: str = "",
) -> int:
    total_chars = len(document_text) + len(system_prompt) + len(extra)
    return max(1, int(total_chars * _CHARS_PER_TOKEN))


def check_document_fits_context(
    estimated: int,
    max_tokens: int,
) -> AppError | None:
    if estimated > max_tokens:
        return token_limit_error(estimated, max_tokens)
    return None
