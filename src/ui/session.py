"""Streamlit session_state 初始化与文档状态。"""

from __future__ import annotations

import streamlit as st

from src.config import get_default_model_id, get_model_options
from src.core.constants import (
    STATE_PDF_NAME,
    STATE_PDF_PAGES,
    STATE_PDF_SIG,
    STATE_PDF_TEXT,
    STATE_PENDING_QUESTION,
    STATE_QA,
    STATE_RAG_BUILD_DEBUG,
    STATE_RAG_CHUNKS,
    STATE_RAG_COLLECTION,
    STATE_RAG_READY,
    STATE_SELECTED_MODEL,
    STATE_SUMMARY,
)
from src.services.document_service import DocumentService


def init_session() -> None:
    if STATE_QA not in st.session_state:
        st.session_state[STATE_QA] = []
    if STATE_SELECTED_MODEL not in st.session_state:
        default = get_default_model_id()
        ids = [m[1] for m in get_model_options()]
        st.session_state[STATE_SELECTED_MODEL] = (
            default if default in ids else (ids[0] if ids else "gpt-4o-mini")
        )


def pdf_upload_sig(name: str, size: int) -> tuple[str, int]:
    """上传文件身份：(文件名, 声明大小)。

    用 size 而非 len(bytes)，避免 rerun 后 getvalue 为空导致 sig 漂移。
    """
    return (name, size)


def mark_pdf_sig_processed(name: str, size: int) -> None:
    """解析失败时写入 sig，避免 Streamlit 反复重试同一文件。"""
    st.session_state[STATE_PDF_SIG] = pdf_upload_sig(name, size)


def reset_pdf_state(
    name: str,
    size: int,
    text: str,
    pages: int,
    *,
    rag_collection: str = "",
    rag_chunks: int = 0,
    rag_ready: bool = False,
) -> None:
    st.session_state[STATE_PDF_SIG] = pdf_upload_sig(name, size)
    st.session_state[STATE_PDF_NAME] = name
    st.session_state[STATE_PDF_TEXT] = text
    st.session_state[STATE_PDF_PAGES] = pages
    st.session_state[STATE_SUMMARY] = ""
    st.session_state[STATE_QA] = []
    st.session_state[STATE_RAG_COLLECTION] = rag_collection
    st.session_state[STATE_RAG_CHUNKS] = rag_chunks
    st.session_state[STATE_RAG_READY] = rag_ready
    st.session_state.pop(STATE_PENDING_QUESTION, None)


def clear_pdf(doc_svc: DocumentService | None = None) -> None:
    coll = st.session_state.get(STATE_RAG_COLLECTION)
    if coll:
        (doc_svc or DocumentService()).clear_vector_index(coll)
    for k in (
        STATE_PDF_SIG,
        STATE_PDF_NAME,
        STATE_PDF_TEXT,
        STATE_PDF_PAGES,
        STATE_SUMMARY,
        STATE_QA,
        STATE_PENDING_QUESTION,
        STATE_RAG_COLLECTION,
        STATE_RAG_CHUNKS,
        STATE_RAG_READY,
        STATE_RAG_BUILD_DEBUG,
    ):
        st.session_state.pop(k, None)


def queue_user_question(text: str) -> None:
    t = (text or "").strip()
    if not t or st.session_state.get(STATE_PENDING_QUESTION):
        return
    st.session_state[STATE_QA].append({"role": "user", "content": t})
    st.session_state[STATE_PENDING_QUESTION] = t
    st.rerun()
