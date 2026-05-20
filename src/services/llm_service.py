"""OpenAI 兼容 API：总结与 RAG 上下文作答。"""

from __future__ import annotations

from openai import OpenAI

from src.config import get_max_context_tokens, get_openai_timeout
from src.core.exceptions import (
    AppError,
    classify_openai_error,
    empty_content_error,
)
from src.prompts import FULL_DOCUMENT_SYSTEM, RAG_SYSTEM, SUMMARY_SYSTEM
from src.utils.tokens import check_document_fits_context, estimate_request_tokens


def _client(api_key: str, base_url: str | None) -> OpenAI:
    kwargs: dict = {"api_key": api_key, "timeout": get_openai_timeout()}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _guard_document(document_text: str, system_prompt: str, extra: str = "") -> None:
    if not (document_text or "").strip():
        raise empty_content_error()
    estimated = estimate_request_tokens(document_text, system_prompt, extra)
    err = check_document_fits_context(estimated, get_max_context_tokens())
    if err is not None:
        raise err


def _chat_completion(
    client: OpenAI,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
) -> str:
    try:
        r = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
    except AppError:
        raise
    except Exception as e:
        raise classify_openai_error(e) from e
    return (r.choices[0].message.content or "").strip()


class LLMService:
    """聊天补全封装。"""

    def summarize(
        self,
        api_key: str,
        base_url: str | None,
        model: str,
        document_text: str,
    ) -> str:
        user = (
            "请根据以下从 PDF 提取的正文，按系统提示中的输出模板生成学习笔记。\n\n"
            f"{document_text}"
        )
        _guard_document(document_text, SUMMARY_SYSTEM, user)
        client = _client(api_key, base_url)
        messages = [
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user", "content": user},
        ]
        return _chat_completion(client, model, messages, temperature=0.3)

    def answer_from_full_document(
        self,
        api_key: str,
        base_url: str | None,
        model: str,
        document_text: str,
        question: str,
        chat_history: list[dict[str, str]] | None = None,
    ) -> str:
        user_block = f"【PDF 全文正文】\n{document_text}\n\n【用户问题】\n{question}"
        extra_parts = [question]
        if chat_history:
            for m in chat_history:
                extra_parts.append(m.get("content", ""))
        _guard_document(document_text, FULL_DOCUMENT_SYSTEM, "\n".join(extra_parts))

        client = _client(api_key, base_url)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": FULL_DOCUMENT_SYSTEM},
            {
                "role": "user",
                "content": (
                    "以下是从 PDF 提取的全文正文。"
                    "请严格依据全文回答后续问题；信息不足时请明确说明。"
                ),
            },
            {
                "role": "assistant",
                "content": "好的，我将仅根据全文内容作答，不会使用正文以外的信息。",
            },
        ]
        if chat_history:
            for m in chat_history:
                role = m.get("role", "user")
                content = m.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_block})
        return _chat_completion(client, model, messages, temperature=0.3)

    def answer_from_rag_context(
        self,
        api_key: str,
        base_url: str | None,
        model: str,
        context: str,
        question: str,
        chat_history: list[dict[str, str]] | None = None,
    ) -> str:
        user_block = f"【检索到的文档片段】\n{context}\n\n【用户问题】\n{question}"
        extra_parts = [context, question]
        if chat_history:
            for m in chat_history:
                extra_parts.append(m.get("content", ""))
        _guard_document(context, RAG_SYSTEM, "\n".join(extra_parts))

        client = _client(api_key, base_url)
        messages: list[dict[str, str]] = [
            {"role": "system", "content": RAG_SYSTEM},
            {
                "role": "user",
                "content": (
                    "以下是从 PDF 向量检索得到的文档片段。"
                    "请严格仅依据这些片段回答后续问题；片段不足时请明确说明无法从文档中找到答案。"
                ),
            },
            {
                "role": "assistant",
                "content": "好的，我将仅根据检索片段作答，不会使用片段以外的信息。",
            },
        ]
        if chat_history:
            for m in chat_history:
                role = m.get("role", "user")
                content = m.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_block})
        return _chat_completion(client, model, messages, temperature=0.2)
