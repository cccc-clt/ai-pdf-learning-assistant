"""LLM 系统提示词。"""

from src.prompts.full_document import FULL_DOCUMENT_SYSTEM
from src.prompts.rag import RAG_SYSTEM
from src.prompts.summary import SUMMARY_SYSTEM

__all__ = ["FULL_DOCUMENT_SYSTEM", "SUMMARY_SYSTEM", "RAG_SYSTEM"]
