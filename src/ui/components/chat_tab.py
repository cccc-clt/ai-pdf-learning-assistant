"""对话 Tab：RAG 问答与快捷提问。"""

from __future__ import annotations

import streamlit as st

from src.core.constants import (
    STATE_PENDING_QUESTION,
    STATE_QA,
    STATE_RAG_COLLECTION,
    STATE_RAG_READY,
    SUGGESTION_QUESTIONS,
)
from src.core.exceptions import (
    AppError,
    api_not_configured_error,
    classify_unknown_error,
    empty_content_error,
    rag_not_ready_error,
)
from src.services.rag_service import RAGService
from src.ui.errors import render_streamlit_error
from src.ui.session import queue_user_question
from src.utils.markdown import md_to_html


def render_chat_thread(messages: list[dict[str, str]]) -> None:
    if not messages:
        st.markdown(
            """
            <div class="ai-chat-tab-empty">
              <div class="ai-chat-tab-empty-icon" aria-hidden="true"></div>
              <div class="ai-chat-tab-empty-title">开始与文档对话</div>
              <p class="ai-chat-tab-empty-desc">
                在下方输入问题或使用快捷提问；多轮对话会保存在本会话。
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    for msg in messages:
        role = msg.get("role", "user")
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        if role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(md_to_html(content), unsafe_allow_html=True)
        else:
            with st.chat_message("user"):
                st.write(content)


def render_chat_tab(
    api_key: str,
    base_url: str | None,
    model: str,
    document_text: str,
) -> None:
    st.markdown(
        '<div class="ai-chat-shell ai-chat-workspace">'
        '<div class="ai-chat-hint">RAG 检索问答 · 仅依据文档片段作答 · 本会话内保存'
        '<span class="ai-dot-row" aria-hidden="true"><span class="ai-dot"></span>'
        '<span class="ai-dot"></span><span class="ai-dot"></span></span></div>',
        unsafe_allow_html=True,
    )
    render_chat_thread(st.session_state[STATE_QA])

    pending_q = st.session_state.get(STATE_PENDING_QUESTION)
    if pending_q:
        msgs = st.session_state[STATE_QA]
        if not msgs or msgs[-1].get("role") != "user" or msgs[-1].get("content") != pending_q:
            st.session_state.pop(STATE_PENDING_QUESTION, None)
            st.rerun()
        elif not api_key:
            render_streamlit_error(api_not_configured_error())
            st.session_state[STATE_QA].pop()
            st.session_state.pop(STATE_PENDING_QUESTION, None)
            st.rerun()
        elif not document_text.strip():
            render_streamlit_error(empty_content_error())
            st.session_state[STATE_QA].pop()
            st.session_state.pop(STATE_PENDING_QUESTION, None)
            st.rerun()
        elif not st.session_state.get(STATE_RAG_READY):
            render_streamlit_error(rag_not_ready_error())
            st.session_state[STATE_QA].pop()
            st.session_state.pop(STATE_PENDING_QUESTION, None)
            st.rerun()
        else:
            with st.chat_message("assistant"):
                st.caption("正在思考…")
                st.markdown(
                    '<span class="ai-dot-row ai-typing-inline" aria-hidden="true">'
                    '<span class="ai-dot"></span><span class="ai-dot"></span>'
                    '<span class="ai-dot"></span></span>',
                    unsafe_allow_html=True,
                )
            hist = list(msgs[:-1])
            rag = RAGService()
            with st.spinner("正在连接模型…"):
                try:
                    ans = rag.answer(
                        api_key=api_key,
                        base_url=base_url,
                        model=model,
                        collection_name=st.session_state[STATE_RAG_COLLECTION],
                        question=pending_q,
                        chat_history=hist,
                        document_text=document_text,
                    )
                    st.session_state[STATE_QA].append(
                        {"role": "assistant", "content": ans}
                    )
                    st.session_state.pop(STATE_PENDING_QUESTION, None)
                except AppError as e:
                    render_streamlit_error(e)
                    st.session_state[STATE_QA].pop()
                    st.session_state.pop(STATE_PENDING_QUESTION, None)
                except Exception as e:
                    render_streamlit_error(classify_unknown_error(e))
                    st.session_state[STATE_QA].pop()
                    st.session_state.pop(STATE_PENDING_QUESTION, None)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state[STATE_QA] and api_key:
        st.caption("快捷提问（点击即发送）")
        b1, b2, b3 = st.columns(3)
        for col, label, idx in zip(
            (b1, b2, b3),
            SUGGESTION_QUESTIONS,
            range(len(SUGGESTION_QUESTIONS)),
        ):
            with col:
                if st.button(label, key=f"qa_suggest_{idx}", use_container_width=True):
                    queue_user_question(label)

    if not api_key:
        st.chat_input("模型服务未就绪，无法开始对话…", disabled=True)
    else:
        q = st.chat_input("向文档提问…")
        if q:
            t = q.strip()
            if t:
                if st.session_state.get(STATE_PENDING_QUESTION):
                    st.caption("上一条回复仍在生成，请稍候。")
                else:
                    queue_user_question(t)
