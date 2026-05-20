"""总结 Tab。"""

from __future__ import annotations

import streamlit as st

from src.core.constants import STATE_SUMMARY
from src.core.exceptions import (
    AppError,
    api_not_configured_error,
    classify_unknown_error,
    empty_content_error,
)
from src.services.llm_service import LLMService
from src.ui.errors import render_streamlit_error
from src.utils.markdown import md_to_html


def render_summary_tab(
    api_key: str,
    base_url: str | None,
    model: str,
    doc_for_ai: str,
) -> None:
    llm = LLMService()
    gen = st.button("生成总结", type="primary", use_container_width=False)
    if gen:
        if not api_key:
            render_streamlit_error(api_not_configured_error())
        elif not doc_for_ai.strip():
            render_streamlit_error(empty_content_error())
        else:
            with st.status("正在生成总结…", expanded=True) as status:
                status.write("解析文档片段与长度检查…")
                try:
                    status.write("调用模型生成摘要…")
                    with st.spinner("模型推理中…"):
                        summary = llm.summarize(
                            api_key=api_key,
                            base_url=base_url,
                            model=model,
                            document_text=doc_for_ai,
                        )
                    st.session_state[STATE_SUMMARY] = summary
                    status.write("整理输出与完成展示。")
                    status.update(label="总结完成", state="complete")
                except AppError as e:
                    status.update(label=e.title, state="error")
                    render_streamlit_error(e)
                except Exception as e:
                    err = classify_unknown_error(e)
                    status.update(label=err.title, state="error")
                    render_streamlit_error(err)
    if st.session_state.get(STATE_SUMMARY):
        st.markdown("#### 摘要")
        _sum_html = md_to_html(st.session_state[STATE_SUMMARY])
        st.markdown(
            f'<div class="ai-summary-wrap">{_sum_html}</div>',
            unsafe_allow_html=True,
        )
