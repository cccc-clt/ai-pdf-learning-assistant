"""LangChain + ChromaDB：建库、检索与 RAG 问答编排。"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    get_chroma_persist_dir,
    get_embedding_model_id,
    get_openai_timeout,
    get_rag_chunk_overlap,
    get_rag_chunk_size,
    get_rag_score_threshold,
    get_rag_top_k,
)
from src.core.exceptions import (
    AppError,
    api_not_configured_error,
    classify_openai_error,
    empty_content_error,
)
from src.services.llm_service import LLMService
from src.utils.rag_scores import passes_relevance_threshold, to_relevance_score
from src.utils.text import format_retrieved_context

logger = logging.getLogger(__name__)

# Chroma 0.5+ 要求 collection metadata 为扁平键值；嵌套 dict 会触发 MetadataValue TypeError
_CHROMA_COLLECTION_METADATA = {"hnsw:space": "cosine"}

_NO_CONTEXT_REPLY = (
    "根据当前文档内容，无法找到与您问题相关的答案。"
    "请尝试换一种问法，或确认相关内容是否在所上传的 PDF 中。"
)

_SUMMARY_KEYWORDS: tuple[str, ...] = (
    "总结",
    "概括",
    "主要讲什么",
    "主要内容",
    "研究内容",
    "核心内容",
    "文章大意",
    "创新点",
    "结论",
    "摘要",
)


def is_summary_question(question: str) -> bool:
    """判断是否为全文总结/概括类问题（应基于全文而非片段检索）。"""
    q = (question or "").strip()
    if not q:
        return False
    return any(kw in q for kw in _SUMMARY_KEYWORDS)


class RAGService:
    def __init__(self, llm: LLMService | None = None) -> None:
        self._llm = llm or LLMService()

    @staticmethod
    def collection_id_for(pdf_name: str, raw_byte_len: int) -> str:
        digest = hashlib.sha256(f"{pdf_name}:{raw_byte_len}".encode("utf-8")).hexdigest()
        return f"pdf_{digest[:24]}"

    def _embeddings(
        self,
        api_key: str,
        base_url: str | None,
        *,
        embedding_model_id: str | None = None,
    ) -> OpenAIEmbeddings:
        """向量嵌入客户端；仅使用 EMBEDDING_MODEL_ID，与侧栏对话模型无关。"""
        model_id = embedding_model_id or get_embedding_model_id()
        kwargs: dict = {
            "api_key": api_key,
            "model": model_id,
            "timeout": get_openai_timeout(),
        }
        if base_url:
            kwargs["base_url"] = base_url
        return OpenAIEmbeddings(**kwargs)

    @staticmethod
    def _delete_collection(persist_dir: Path, collection_name: str) -> None:
        try:
            client = chromadb.PersistentClient(path=str(persist_dir))
            client.delete_collection(collection_name)
            logger.debug("Deleted Chroma collection %s", collection_name)
        except (ValueError, chromadb.errors.NotFoundError):
            logger.debug("Chroma collection %s not found, skip delete", collection_name)
        except Exception as e:
            logger.warning(
                "Failed to delete Chroma collection %s: %s",
                collection_name,
                e,
                exc_info=True,
            )

    def build_index(
        self,
        document_text: str,
        collection_name: str,
        api_key: str,
        base_url: str | None,
    ) -> int:
        if not (api_key or "").strip():
            raise api_not_configured_error()
        if not (document_text or "").strip():
            raise empty_content_error()

        embedding_model = get_embedding_model_id()
        text_len = len(document_text)
        logger.info(
            "build_index start collection=%s text_len=%d embedding_model=%s",
            collection_name,
            text_len,
            embedding_model,
        )

        persist_dir = get_chroma_persist_dir()
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._delete_collection(persist_dir, collection_name)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=get_rag_chunk_size(),
            chunk_overlap=get_rag_chunk_overlap(),
            separators=["\n\n", "\n", "。", "；", ". ", " ", ""],
        )
        docs = splitter.split_documents(
            [Document(page_content=document_text, metadata={"source": "pdf"})]
        )
        if not docs:
            raise empty_content_error()

        chunk_count = len(docs)
        logger.info("build_index chunk_count=%d", chunk_count)

        try:
            logger.info("embedding start model=%s", embedding_model)
            embeddings = self._embeddings(
                api_key, base_url, embedding_model_id=embedding_model
            )
            logger.info("embedding done")

            logger.info("chroma write start collection=%s", collection_name)
            Chroma.from_documents(
                documents=docs,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=str(persist_dir),
                collection_metadata=_CHROMA_COLLECTION_METADATA,
            )
            logger.info("chroma write done collection=%s", collection_name)
        except AppError:
            raise
        except Exception as e:
            raise classify_openai_error(e) from e

        logger.info(
            "build_index done collection=%s chunk_count=%d persist_dir=%s",
            collection_name,
            chunk_count,
            persist_dir,
        )
        return chunk_count

    def _open_store(
        self,
        collection_name: str,
        api_key: str,
        base_url: str | None,
    ) -> Chroma:
        persist_dir = get_chroma_persist_dir()
        return Chroma(
            collection_name=collection_name,
            embedding_function=self._embeddings(api_key, base_url),
            persist_directory=str(persist_dir),
        )

    def _collection_distance_metric(self, store: Chroma) -> str | None:
        try:
            coll = getattr(store, "_collection", None)
            if coll is None:
                return None
            cfg = coll.configuration or {}
            hnsw = cfg.get("hnsw")
            if isinstance(hnsw, dict):
                return hnsw.get("space")
            return cfg.get("hnsw:space")
        except Exception:
            return None

    def _distance_to_relevance(self, distance: float, metric: str | None) -> float:
        if metric == "l2":
            return VectorStore._euclidean_relevance_score_fn(distance)
        if metric == "ip":
            return VectorStore._max_inner_product_relevance_score_fn(distance)
        return VectorStore._cosine_relevance_score_fn(distance)

    def _search_pairs(
        self,
        store: Chroma,
        question: str,
    ) -> list[tuple[Document, float]]:
        """多路径检索，返回 (文档, 相关度)。"""
        k = get_rag_top_k()
        metric = self._collection_distance_metric(store)

        try:
            pairs = store.similarity_search_with_relevance_scores(question, k=k)
            if pairs:
                return pairs
        except Exception as exc:
            logger.warning("similarity_search_with_relevance_scores failed: %s", exc)

        try:
            scored = store.similarity_search_with_score(question, k=k)
            if scored:
                return [
                    (doc, self._distance_to_relevance(float(dist), metric))
                    for doc, dist in scored
                ]
        except Exception as exc:
            logger.warning("similarity_search_with_score failed: %s", exc)

        try:
            docs = store.similarity_search(question, k=k)
            if docs:
                return [(doc, 0.5) for doc in docs]
        except Exception as exc:
            logger.warning("similarity_search failed: %s", exc)

        return []

    def retrieve_chunks(
        self,
        question: str,
        collection_name: str,
        api_key: str,
        base_url: str | None,
    ) -> list[tuple[str, float]]:
        persist_dir = get_chroma_persist_dir()
        if not persist_dir.is_dir() or not (collection_name or "").strip():
            return []

        try:
            store = self._open_store(collection_name, api_key, base_url)
            pairs = self._search_pairs(store, question)
        except AppError:
            raise
        except Exception as e:
            raise classify_openai_error(e) from e

        threshold = get_rag_score_threshold()
        candidates: list[tuple[str, float]] = []
        for doc, raw_score in pairs:
            content = (doc.page_content or "").strip()
            if not content:
                continue
            relevance = to_relevance_score(float(raw_score))
            candidates.append((content, relevance))

        out = [
            (c, r) for c, r in candidates if passes_relevance_threshold(r, threshold)
        ]
        if not out and candidates:
            relaxed = max(0.0, threshold * 0.5)
            out = [
                (c, r)
                for c, r in candidates
                if passes_relevance_threshold(r, relaxed)
            ]
        if not out and candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            out = candidates[: get_rag_top_k()]
        return out

    def clear_collection(self, collection_name: str) -> None:
        persist_dir = get_chroma_persist_dir()
        if persist_dir.is_dir():
            self._delete_collection(persist_dir, collection_name)

    def answer(
        self,
        api_key: str,
        base_url: str | None,
        model: str,
        collection_name: str,
        question: str,
        chat_history: list[dict[str, str]] | None = None,
        document_text: str | None = None,
    ) -> str:
        if is_summary_question(question) and (document_text or "").strip():
            return self._llm.answer_from_full_document(
                api_key=api_key,
                base_url=base_url,
                model=model,
                document_text=document_text.strip(),
                question=question,
                chat_history=chat_history,
            )

        chunks = self.retrieve_chunks(
            question=question,
            collection_name=collection_name,
            api_key=api_key,
            base_url=base_url,
        )
        if not chunks:
            return _NO_CONTEXT_REPLY

        context = format_retrieved_context(chunks)
        return self._llm.answer_from_rag_context(
            api_key=api_key,
            base_url=base_url,
            model=model,
            context=context,
            question=question,
            chat_history=chat_history,
        )
