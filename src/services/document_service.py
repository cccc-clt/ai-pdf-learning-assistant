"""文档加载与向量索引编排。"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from src.services.rag_service import RAGService
from src.utils.pdf import load_pdf_bytes

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DocumentLoadResult:
    text: str
    pages: int
    collection_id: str
    chunk_count: int
    rag_ready: bool


class DocumentService:
    def __init__(self, rag: RAGService | None = None) -> None:
        self._rag = rag or RAGService()

    @staticmethod
    def parse_pdf(raw: bytes) -> tuple[str, int]:
        return load_pdf_bytes(raw)

    def build_index(
        self,
        document_text: str,
        collection_name: str,
        api_key: str,
        base_url: str | None,
    ) -> int:
        text_len = len(document_text or "")
        logger.info(
            "build_index start collection=%s text_len=%d",
            collection_name,
            text_len,
        )
        n = self._rag.build_index(
            document_text, collection_name, api_key, base_url
        )
        logger.info(
            "build_index done collection=%s chunk_count=%d",
            collection_name,
            n,
        )
        return n

    def load_and_index(
        self,
        pdf_name: str,
        raw: bytes,
        api_key: str,
        base_url: str | None,
    ) -> DocumentLoadResult:
        text, pages = self.parse_pdf(raw)
        coll_id = self._rag.collection_id_for(pdf_name, len(raw)) if text.strip() else ""
        chunk_count = 0
        rag_ready = False
        if text.strip() and api_key and coll_id:
            chunk_count = self.build_index(text, coll_id, api_key, base_url)
            rag_ready = True
        return DocumentLoadResult(
            text=text,
            pages=pages,
            collection_id=coll_id,
            chunk_count=chunk_count,
            rag_ready=rag_ready,
        )

    def clear_vector_index(self, collection_id: str) -> None:
        if collection_id:
            self._rag.clear_collection(collection_id)
