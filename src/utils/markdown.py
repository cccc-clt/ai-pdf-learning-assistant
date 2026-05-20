"""Markdown 转 HTML（Streamlit 展示）。"""

from __future__ import annotations

from markdown import markdown

_MD_EXTENSIONS = ["fenced_code", "tables", "nl2br"]


def md_to_html(text: str) -> str:
    return markdown(text, extensions=_MD_EXTENSIONS)
