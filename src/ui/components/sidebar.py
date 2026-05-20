"""侧栏：主题、模型、会话摘要、操作。"""

from __future__ import annotations

import streamlit as st

from src.config import get_default_model_id, get_model_options, get_openai_api_key
from src.core.constants import (
    STATE_PENDING_QUESTION,
    STATE_QA,
    STATE_SELECTED_MODEL,
)
from src.ui.session import clear_pdf


def _api_ready() -> bool:
    return bool(get_openai_api_key())


def _render_sidebar_history(messages: list[dict[str, str]]) -> None:
    st.markdown("#### 本会话")
    if not messages:
        st.caption("暂无消息。在主区「对话」中发送后，此处显示摘要。")
        return
    n = len(messages)
    user_turns = sum(1 for m in messages if m.get("role") == "user")
    st.metric("消息条数", n)
    st.caption(f"含用户发言约 {user_turns} 条")
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            c = (m.get("content") or "").strip()
            if c:
                last_user = c
                break
    if last_user:
        st.caption("最近提问")
        preview = last_user.replace("\n", " ")[:100]
        if len(last_user) > 100:
            preview += "…"
        st.text(preview)
    if n > 40:
        st.caption("对话较长，请注意模型上下文限制。")


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### PDF 学习助手")
        model_opts = get_model_options()
        labels = [m[0] for m in model_opts]
        ids = [m[1] for m in model_opts]
        cur = st.session_state.get(STATE_SELECTED_MODEL, get_default_model_id())
        try:
            idx = ids.index(cur)
        except ValueError:
            idx = 0
        picked = st.selectbox("选择模型", labels, index=idx)
        model_id = ids[labels.index(picked)]
        st.session_state[STATE_SELECTED_MODEL] = model_id

        if _api_ready():
            st.caption("模型服务已就绪。")
        else:
            st.warning("模型服务未配置，无法调用 AI。请联系管理员或检查部署环境。")

        st.divider()
        _render_sidebar_history(st.session_state.get(STATE_QA, []))

        st.divider()
        if st.button("清除文档与对话", type="secondary", use_container_width=True):
            clear_pdf()
            st.rerun()
        if st.button("清空问答记录", type="secondary", use_container_width=True):
            st.session_state[STATE_QA] = []
            st.session_state.pop(STATE_PENDING_QUESTION, None)
            st.rerun()

    return model_id
