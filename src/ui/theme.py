"""应用级 CSS（固定浅色主题）。"""

from __future__ import annotations

from src.ui.styles import LIGHT_APP_CSS


def get_app_css() -> str:
    """返回注入页面的 `<style>` 块（供 `st.markdown(..., unsafe_allow_html=True)`）。"""
    return LIGHT_APP_CSS
