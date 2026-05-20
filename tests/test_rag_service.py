"""RAG 服务工具方法单测。"""

from unittest.mock import MagicMock

from src.services.rag_service import RAGService, is_summary_question


def test_collection_id_stable():
    a = RAGService.collection_id_for("doc.pdf", 1024)
    b = RAGService.collection_id_for("doc.pdf", 1024)
    c = RAGService.collection_id_for("doc.pdf", 2048)
    assert a == b
    assert a != c
    assert a.startswith("pdf_")


def test_is_summary_question():
    assert is_summary_question("这篇文档主要讲什么？")
    assert is_summary_question("请总结这篇文档")
    assert is_summary_question("这篇论文的创新点是什么？")
    assert not is_summary_question("文中 RSU 布置优化方法是什么？")
    assert not is_summary_question("作者构建了什么模型？")
    assert not is_summary_question("")


def test_answer_summary_uses_full_document():
    llm = MagicMock()
    llm.answer_from_full_document.return_value = "全文回答"
    rag = RAGService(llm=llm)
    out = rag.answer(
        api_key="k",
        base_url=None,
        model="gpt-4o-mini",
        collection_name="pdf_abc",
        question="这篇文档主要讲什么？",
        document_text="正文内容",
    )
    assert out == "全文回答"
    llm.answer_from_full_document.assert_called_once()
    llm.answer_from_rag_context.assert_not_called()


def test_answer_specific_uses_rag():
    llm = MagicMock()
    llm.answer_from_rag_context.return_value = "片段回答"
    rag = RAGService(llm=llm)
    rag.retrieve_chunks = MagicMock(return_value=[("chunk", 0.9)])
    out = rag.answer(
        api_key="k",
        base_url=None,
        model="gpt-4o-mini",
        collection_name="pdf_abc",
        question="RSU 布置优化方法是什么？",
        document_text="正文内容",
    )
    assert out == "片段回答"
    llm.answer_from_full_document.assert_not_called()
    llm.answer_from_rag_context.assert_called_once()
