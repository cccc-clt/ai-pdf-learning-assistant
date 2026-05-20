"""纯文本工具。"""

from __future__ import annotations

from src.core.constants import MAX_DOC_CHARS


def clip_document(text: str) -> tuple[str, bool]:
    if len(text) <= MAX_DOC_CHARS:
        return text, False
    return text[:MAX_DOC_CHARS], True


def format_retrieved_context(chunks: list[tuple[str, float]]) -> str:
    parts: list[str] = []
    for i, (text, score) in enumerate(chunks, start=1):
        parts.append(f"### 片段 {i}（相关度 {score:.2f}）\n{text}")
    return "\n\n".join(parts)
