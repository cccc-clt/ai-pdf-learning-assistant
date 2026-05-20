"""配置：优先环境变量（.env），其次 Streamlit secrets，最后本地 app_settings。"""

from __future__ import annotations

from pathlib import Path

from src.config.secrets_provider import resolve_setting

_FALLBACK_MODEL_OPTIONS: tuple[tuple[str, str], ...] = (
    ("GPT-4o mini（推荐）", "gpt-4o-mini"),
    ("GPT-4o", "gpt-4o"),
    ("GPT-4.1 nano", "gpt-4.1-nano"),
    ("GPT-4.1 mini", "gpt-4.1-mini"),
    ("GPT-4.1", "gpt-4.1"),
    ("GPT-4 Turbo", "gpt-4-turbo"),
    ("GPT-4 Turbo Preview", "gpt-4-turbo-preview"),
    ("o4-mini", "o4-mini"),
    ("o3-mini", "o3-mini"),
    ("o1-mini", "o1-mini"),
    ("o1-preview", "o1-preview"),
    ("GPT-3.5 Turbo", "gpt-3.5-turbo"),
)


def _app_settings():
    try:
        from src import app_settings as _s

        return _s
    except ImportError:
        return None


def get_openai_api_key() -> str:
    return resolve_setting("OPENAI_API_KEY") or ""


def get_openai_base_url() -> str | None:
    raw = resolve_setting("OPENAI_BASE_URL")
    return raw.rstrip("/") if raw else None


def get_default_model_id() -> str:
    mid = resolve_setting("DEFAULT_MODEL_ID")
    if mid:
        return mid
    return resolve_setting("OPENAI_MODEL", env_name="OPENAI_MODEL") or "gpt-4o-mini"


def get_model_options() -> tuple[tuple[str, str], ...]:
    mod = _app_settings()
    if mod is not None:
        opts = getattr(mod, "MODEL_OPTIONS", None)
        if opts and isinstance(opts, (list, tuple)) and len(opts) > 0:
            return tuple((str(a), str(b)) for a, b in opts)
    return _FALLBACK_MODEL_OPTIONS


def get_default_model() -> str:
    return get_default_model_id()


def _int_setting(name: str, default: int) -> int:
    raw = resolve_setting(name)
    if raw:
        try:
            return int(raw)
        except ValueError:
            pass
    return default


def get_openai_timeout() -> float:
    return float(_int_setting("OPENAI_TIMEOUT", 120))


def get_max_context_tokens() -> int:
    return _int_setting("MAX_CONTEXT_TOKENS", 120_000)


def get_embedding_model_id() -> str:
    return resolve_setting("EMBEDDING_MODEL_ID") or "text-embedding-3-small"


def get_rag_top_k() -> int:
    return _int_setting("RAG_TOP_K", 6)


def get_rag_chunk_size() -> int:
    return _int_setting("RAG_CHUNK_SIZE", 800)


def get_rag_chunk_overlap() -> int:
    return _int_setting("RAG_CHUNK_OVERLAP", 120)


def get_rag_score_threshold() -> float:
    raw = resolve_setting("RAG_SCORE_THRESHOLD")
    if raw:
        try:
            return float(raw)
        except ValueError:
            pass
    return 0.2


def get_chroma_persist_dir() -> Path:
    raw = resolve_setting("CHROMA_PERSIST_DIR")
    if raw:
        return Path(raw)
    root = Path(__file__).resolve().parent.parent.parent
    return root / "data" / "chroma"
