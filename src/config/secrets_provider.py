"""配置读取：环境变量（.env）> Streamlit secrets > 本地 app_settings（可选）。"""

from __future__ import annotations

import os
from typing import Any


def _app_settings_module() -> Any | None:
    try:
        from src import app_settings as mod

        return mod
    except ImportError:
        return None


def get_from_app_settings(name: str) -> str | None:
    mod = _app_settings_module()
    if mod is None:
        return None
    val = getattr(mod, name, None)
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def get_from_env(name: str) -> str | None:
    raw = (os.environ.get(name) or "").strip()
    return raw if raw else None


def get_from_streamlit_secrets(name: str) -> str | None:
    try:
        import streamlit as st
    except ImportError:
        return None
    try:
        if name not in st.secrets:
            return None
        raw = str(st.secrets[name]).strip()
        return raw if raw else None
    except (FileNotFoundError, KeyError, RuntimeError, TypeError):
        return None


def resolve_setting(name: str, *, env_name: str | None = None) -> str | None:
    """按优先级返回配置字符串，未设置则 None。"""
    env_key = env_name or name
    for reader in (
        lambda: get_from_env(env_key),
        lambda: get_from_streamlit_secrets(env_key),
        lambda: get_from_app_settings(name),
    ):
        val = reader()
        if val is not None:
            return val
    return None
