"""Streamlit 错误展示。"""

from __future__ import annotations

import streamlit as st

from src.core.exceptions import AppError

_ERROR_CATEGORY: dict[str, str] = {
    "api_auth": "认证失败",
    "rate_limit": "限流",
    "timeout": "超时",
    "network": "网络问题",
    "model_unsupported": "模型不支持",
    "api_bad_request": "请求被拒绝",
    "api_status": "服务异常",
    "token_limit": "超出上下文",
    "empty_content": "内容为空",
    "chroma_write": "向量库写入",
    "api_unknown": "模型调用失败",
    "unknown": "未知错误",
}


def error_category_label(err: AppError) -> str:
    return _ERROR_CATEGORY.get(err.code, "其他错误")


def render_streamlit_error(err: AppError) -> None:
    category = error_category_label(err)
    st.error(f"**[{category}] {err.title}**\n\n{err.message}")
    if err.suggestion:
        st.info(err.suggestion)
