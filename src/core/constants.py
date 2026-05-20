"""应用级常量与会话状态键。"""

from __future__ import annotations

MAX_DOC_CHARS = 100_000

STATE_PDF_SIG = "pdf_sig"
STATE_PDF_NAME = "pdf_name"
STATE_PDF_TEXT = "pdf_text"
STATE_PDF_PAGES = "pdf_pages"
STATE_SUMMARY = "ai_summary"
STATE_QA = "qa_messages"
STATE_PENDING_QUESTION = "pending_question"
STATE_SELECTED_MODEL = "selected_model_id"
STATE_RAG_COLLECTION = "rag_collection_id"
STATE_RAG_CHUNKS = "rag_chunk_count"
STATE_RAG_READY = "rag_ready"
STATE_RAG_BUILD_DEBUG = "rag_build_debug"

SUGGESTION_QUESTIONS: tuple[str, ...] = (
    "这篇文档主要讲什么？",
    "请列出 5 个关键要点",
    "有哪些结论或建议？",
)
