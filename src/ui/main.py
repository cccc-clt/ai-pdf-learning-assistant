"""Streamlit 主页面编排。"""

from __future__ import annotations

import html

import streamlit as st

from src.config import (
    get_chroma_persist_dir,
    get_embedding_model_id,
    get_openai_api_key,
    get_openai_base_url,
)
from src.core.constants import (
    MAX_DOC_CHARS,
    STATE_PDF_NAME,
    STATE_PDF_PAGES,
    STATE_PDF_SIG,
    STATE_PDF_TEXT,
    STATE_RAG_BUILD_DEBUG,
    STATE_RAG_CHUNKS,
    STATE_RAG_COLLECTION,
    STATE_RAG_READY,
)
from src.core.exceptions import (
    AppError,
    api_not_configured_error,
    classify_unknown_error,
    empty_file_error,
)
from src.services.document_service import DocumentService
from src.services.rag_service import RAGService
from src.ui.components.chat_tab import render_chat_tab
from src.ui.components.sidebar import render_sidebar
from src.ui.components.summary_tab import render_summary_tab
from src.ui.errors import render_streamlit_error
from src.ui.session import (
    init_session,
    mark_pdf_sig_processed,
    pdf_upload_sig,
    reset_pdf_state,
)
from src.ui.theme import get_app_css
from src.utils.text import clip_document


def _pdf_display_state() -> tuple[str | None, str, int]:
    return (
        st.session_state.get(STATE_PDF_NAME),
        st.session_state.get(STATE_PDF_TEXT) or "",
        st.session_state.get(STATE_PDF_PAGES, 0),
    )


def _rag_collection_id() -> str:
    coll = st.session_state.get(STATE_RAG_COLLECTION)
    if coll:
        return coll
    sig = st.session_state.get(STATE_PDF_SIG)
    name = st.session_state.get(STATE_PDF_NAME)
    if isinstance(sig, tuple) and len(sig) == 2 and name:
        return RAGService.collection_id_for(name, int(sig[1]))
    return ""


def _format_rag_build_debug(
    collection_id: str,
    *,
    build_index_return: int | None = None,
    phase: str = "",
) -> str:
    pdf_len = len(st.session_state.get(STATE_PDF_TEXT, "") or "")
    lines = [
        f"PDF 文本长度: {pdf_len}",
        f"collection_id: {collection_id or '(空)'}",
        f"chunk_count (build_index 返回值): "
        f"{build_index_return if build_index_return is not None else '(尚未返回)'}",
        f"STATE_RAG_READY: {st.session_state.get(STATE_RAG_READY)}",
        f"STATE_RAG_CHUNKS: {st.session_state.get(STATE_RAG_CHUNKS)}",
        f"Chroma 持久化目录: {get_chroma_persist_dir()}",
    ]
    if phase:
        lines.append(f"阶段: {phase}")
    return "\n".join(lines)


def _show_rag_build_debug(
    collection_id: str,
    *,
    build_index_return: int | None = None,
    phase: str = "",
) -> None:
    """页面临时展示建索引调试信息，并写入 session 供 rerun 后仍可见。"""
    text = _format_rag_build_debug(
        collection_id,
        build_index_return=build_index_return,
        phase=phase,
    )
    st.session_state[STATE_RAG_BUILD_DEBUG] = text
    with st.expander("建索引调试信息（临时）", expanded=True):
        st.code(text, language=None)


def _render_persisted_rag_build_debug() -> None:
    """展示上一轮建索引留下的调试信息。"""
    text = st.session_state.get(STATE_RAG_BUILD_DEBUG)
    if not text:
        return
    with st.expander("建索引调试信息（临时）", expanded=True):
        st.code(text, language=None)


def _rag_index_diag_lines(
    *,
    api_key: str,
    base_url: str | None,
    chat_model: str,
) -> list[str]:
    embedding_id = get_embedding_model_id()
    key_ok = bool((api_key or "").strip())
    return [
        f"base_url: {base_url or '(未设置，使用 OpenAI 官方默认)'}",
        f"embedding_model: {embedding_id}",
        f"chat_model (仅总结/对话，不用于建索引): {chat_model or '(未选择)'}",
        f"api_key: {'已配置' if key_ok else '未配置或为空'}",
    ]


def _execute_build_rag_index(
    *,
    api_key: str,
    base_url: str | None,
    collection_id: str,
    rerun_on_success: bool = True,
) -> None:
    """从 session 读取 PDF 正文并建索引；成功写回 STATE_RAG_*，失败 st.exception。"""
    pdf_text = st.session_state.get(STATE_PDF_TEXT) or ""
    if not pdf_text.strip():
        st.error("PDF 文本为空，无法建立索引")
        return
    if not (api_key or "").strip():
        st.exception(api_not_configured_error())
        return
    if not collection_id:
        st.error("缺少向量集合 ID，无法建立索引")
        return

    _show_rag_build_debug(collection_id, phase="调用 build_index 之前")

    try:
        with st.spinner("正在建立向量索引（首次可能需 1–3 分钟，请稍候）…"):
            chunk_count = DocumentService().build_index(
                pdf_text, collection_id, api_key, base_url
            )
        st.session_state[STATE_RAG_READY] = True
        st.session_state[STATE_RAG_CHUNKS] = chunk_count
        st.session_state[STATE_RAG_COLLECTION] = collection_id
        _show_rag_build_debug(
            collection_id,
            build_index_return=chunk_count,
            phase="build_index 成功，session 已更新",
        )
        st.success(f"向量索引建立成功，共 {chunk_count} 个文本块")
        if rerun_on_success:
            st.rerun()
    except Exception as e:
        _show_rag_build_debug(
            collection_id,
            build_index_return=None,
            phase=f"build_index 失败: {type(e).__name__}",
        )
        if isinstance(e, AppError):
            render_streamlit_error(e)
        st.exception(e)


def _render_rag_index_panel(
    *,
    api_key: str,
    base_url: str | None,
    chat_model: str,
) -> None:
    """RAG 未就绪时展示配置与重建索引按钮（建索引仅用 embedding 模型，不用 chat_model）。"""
    embedding_id = get_embedding_model_id()
    st.caption(
        f"对话模型 `{chat_model}`（总结/回答）· "
        f"Embedding `{embedding_id}`（向量索引，与左侧模型选择无关）"
    )

    diag = _rag_index_diag_lines(
        api_key=api_key, base_url=base_url, chat_model=chat_model
    )
    with st.expander("向量索引配置", expanded=False):
        st.code("\n".join(diag), language=None)

    coll_id = _rag_collection_id()
    if not coll_id:
        st.warning("缺少向量集合 ID，请重新上传 PDF 后再试。")
        return

    if st.button("重新建立向量索引", type="primary", key="rebuild_rag_index"):
        st.markdown("**本次请求上下文**")
        st.code("\n".join(diag), language=None)
        _execute_build_rag_index(
            api_key=api_key,
            base_url=base_url,
            collection_id=coll_id,
            rerun_on_success=True,
        )


def _handle_pdf_upload(
    uploaded: object,
    *,
    api_key: str,
    base_url: str | None,
) -> None:
    """解析 PDF；同一文件只解析一次（按 name+size 去重）。索引失败后可用手动按钮重建。"""
    sig = pdf_upload_sig(uploaded.name, uploaded.size)
    if st.session_state.get(STATE_PDF_SIG) == sig:
        # 仅跳过重复解析；RAG 未就绪时请用「重新建立向量索引」按钮（读 STATE_PDF_TEXT）
        return

    raw = uploaded.getvalue()
    doc_svc = DocumentService()
    parsed_ok = False
    pdf_text_parsed = ""
    pdf_pages_parsed = 0
    coll_id = ""

    with st.spinner("正在解析 PDF…"):
        if not raw:
            render_streamlit_error(empty_file_error())
            mark_pdf_sig_processed(uploaded.name, uploaded.size)
        else:
            try:
                pdf_text_parsed, pdf_pages_parsed = doc_svc.parse_pdf(raw)
                coll_id = (
                    RAGService.collection_id_for(uploaded.name, uploaded.size)
                    if pdf_text_parsed.strip()
                    else ""
                )
                reset_pdf_state(
                    uploaded.name,
                    uploaded.size,
                    pdf_text_parsed,
                    pdf_pages_parsed,
                    rag_collection=coll_id,
                    rag_chunks=0,
                    rag_ready=False,
                )
                parsed_ok = True
            except AppError as e:
                render_streamlit_error(e)
                mark_pdf_sig_processed(uploaded.name, uploaded.size)
            except Exception as e:
                render_streamlit_error(classify_unknown_error(e))
                mark_pdf_sig_processed(uploaded.name, uploaded.size)

    if parsed_ok and pdf_text_parsed.strip() and api_key and coll_id:
        st.session_state[STATE_PDF_TEXT] = pdf_text_parsed
        _execute_build_rag_index(
            api_key=api_key,
            base_url=base_url,
            collection_id=coll_id,
            rerun_on_success=True,
        )


def run_app() -> None:
    st.set_page_config(
        page_title="AI PDF 学习助手",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session()
    # selected_model 仅用于总结/对话；向量索引固定使用 EMBEDDING_MODEL_ID
    # （见 RAGService.build_index）
    selected_model = render_sidebar()
    st.markdown(get_app_css(), unsafe_allow_html=True)

    api_key = get_openai_api_key()
    base_url = get_openai_base_url()
    chat_model = selected_model

    def _api_ready() -> bool:
        return bool(api_key)

    _pill_class = "ai-pill ai-pill-online" if _api_ready() else "ai-pill"
    _pill_label = "模型已连接" if _api_ready() else "服务未就绪"

    st.markdown(
        f"""
        <div class="ai-brand-wrap">
          <div class="ai-brand">
            <div class="ai-logo">AI</div>
            <div>
              <p class="ai-title">PDF 学习助手</p>
              <p class="ai-subtitle">上传文档 · 智能总结 · RAG 检索问答</p>
            </div>
          </div>
          <div class="{_pill_class}">
            <span class="ai-pill-dot"></span>{html.escape(_pill_label)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1, 1.35], gap="large")

    uploaded = None
    with left_col:
        st.markdown('<div class="ai-card ai-card-tight">', unsafe_allow_html=True)
        st.markdown("**文档**")
        uploaded = st.file_uploader(
            "拖拽或选择 PDF",
            type=["pdf"],
            accept_multiple_files=False,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        if uploaded is not None:
            _handle_pdf_upload(uploaded, api_key=api_key, base_url=base_url)

    pdf_name, pdf_text, pdf_pages = _pdf_display_state()

    with right_col:
        if pdf_text:
            st.markdown(
                f'<div class="ai-card ai-card-tight">'
                f'<span class="ai-inline-muted">当前文件</span>'
                f'<div class="ai-inline-title">{html.escape(pdf_name or "—")}</div>'
                f'<div class="ai-meta-sub">{pdf_pages} 页 · {len(pdf_text):,} 字符</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="ai-card ai-card-tight"><p class="ai-inline-muted" style="margin:0;">'
                "上传 PDF 后，可在此查看概要信息并开始总结与对话。"
                "</p></div>",
                unsafe_allow_html=True,
            )

    if pdf_text:
        doc_for_ai, truncated = clip_document(pdf_text)
        st.markdown('<div class="ai-card ai-card-tight">', unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                "文档",
                (pdf_name or "—")[:24] + ("…" if pdf_name and len(pdf_name) > 24 else ""),
            )
        with m2:
            st.metric("页数", pdf_pages)
        with m3:
            st.metric("字符数", f"{len(pdf_text):,}")
        st.markdown("</div>", unsafe_allow_html=True)

        if truncated:
            st.warning(
                f"正文较长，已截取前 {MAX_DOC_CHARS:,} 个字符用于「总结」Tab；"
                "「对话」中总结类问题将使用全文（受模型上下文限制），"
                "普通问题仍通过向量检索作答。"
            )

        _render_persisted_rag_build_debug()

        if st.session_state.get(STATE_RAG_READY):
            st.caption(
                f"RAG 已就绪：已向量化 {st.session_state.get(STATE_RAG_CHUNKS, 0)} 个文本块 · "
                f"Embedding 模型：`{get_embedding_model_id()}`"
            )
        elif pdf_text.strip() and api_key:
            st.warning("向量索引未建立，RAG 对话暂不可用。可点击下方按钮重新建立索引。")
            _render_rag_index_panel(
                api_key=api_key,
                base_url=base_url,
                chat_model=chat_model,
            )
        elif pdf_text.strip() and not api_key:
            st.caption("未配置 API 密钥，无法建立向量索引。")

        st.markdown('<div class="ai-card ai-workbench">', unsafe_allow_html=True)
        tab_sum, tab_qa = st.tabs(["总结", "对话"])

        with tab_sum:
            render_summary_tab(api_key, base_url, chat_model, doc_for_ai)

        with tab_qa:
            render_chat_tab(api_key, base_url, chat_model, pdf_text)

        st.markdown("</div>", unsafe_allow_html=True)

    elif pdf_name:
        st.warning(
            "已上传文件，但未提取到可读文本。扫描版 PDF 需先 OCR；"
            "或导出为可选中文字的 PDF。"
        )
    else:
        st.info("请在左侧上传 PDF，开始总结与对话。")
