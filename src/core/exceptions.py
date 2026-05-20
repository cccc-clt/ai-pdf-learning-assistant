"""领域异常与 OpenAI 错误分类。"""

from __future__ import annotations

from dataclasses import dataclass

_TOKEN_LIMIT_KEYWORDS = (
    "context_length",
    "maximum context",
    "max_tokens",
    "token limit",
    "too many tokens",
    "context length",
    "reduce the length",
)


@dataclass
class AppError(Exception):
    """领域异常。不可 frozen：作为 Exception 传播时 contextlib/st.spinner 需写入 __traceback__。"""

    code: str
    title: str
    message: str
    suggestion: str = ""

    def __str__(self) -> str:
        return self.message


def empty_file_error() -> AppError:
    return AppError(
        code="empty_file",
        title="文件为空",
        message="上传的文件没有任何内容，请选择有效的 PDF 文件。",
        suggestion="请重新选择非空的 PDF 后再试。",
    )


def empty_content_error() -> AppError:
    return AppError(
        code="empty_content",
        title="无可读正文",
        message="当前没有可用于模型分析的文本内容。",
        suggestion="请上传包含可选中文字的 PDF；扫描版需先进行 OCR。",
    )


def pdf_parse_error(detail: str = "") -> AppError:
    msg = "无法解析该 PDF，文件可能已损坏或不是有效的 PDF 格式。"
    if detail:
        msg = f"{msg}（{detail}）"
    return AppError(
        code="pdf_parse",
        title="PDF 解析失败",
        message=msg,
        suggestion="请确认文件可正常打开，或尝试重新导出/另存为 PDF 后上传。",
    )


def api_not_configured_error() -> AppError:
    return AppError(
        code="api_not_configured",
        title="模型服务未配置",
        message="未检测到可用的 API 密钥，无法调用 AI 功能。",
        suggestion="请联系管理员配置 OPENAI_API_KEY，或检查部署环境。",
    )


def token_limit_error(estimated: int, max_tokens: int) -> AppError:
    return AppError(
        code="token_limit",
        title="文档过长",
        message=(
            f"预估请求约 {estimated:,} tokens，超过当前限制（{max_tokens:,} tokens）。"
            "即使已截取正文，仍可能超出模型上下文窗口。"
        ),
        suggestion="请拆分 PDF 后分别学习，或更换上下文更大的模型。",
    )


def rag_not_ready_error() -> AppError:
    return AppError(
        code="rag_not_ready",
        title="检索索引未就绪",
        message="当前文档尚未建立向量索引，无法使用 RAG 问答。",
        suggestion="请在主界面点击「重新建立向量索引」；若失败，请根据错误提示检查 API、网络或 Embedding 模型配置。",
    )


def chroma_write_error(detail: str = "") -> AppError:
    msg = "向量库（Chroma）写入失败，无法保存嵌入结果。"
    if detail:
        msg = f"{msg}（{detail}）"
    return AppError(
        code="chroma_write",
        title="向量库写入失败",
        message=msg,
        suggestion="请确认 data/chroma 目录可写；若仍失败，可尝试清除文档后重新上传。",
    )


def classify_unknown_error(exc: Exception) -> AppError:
    return AppError(
        code="unknown",
        title="发生未知错误",
        message="操作未能完成，请稍后重试。",
        suggestion=f"若问题持续，请联系管理员并提供时间与环境信息。（{type(exc).__name__}）",
    )


def _exc_message(exc: Exception) -> str:
    parts: list[str] = []
    for attr in ("message", "body"):
        val = getattr(exc, attr, None)
        if val is not None:
            parts.append(str(val))
    parts.append(str(exc))
    return " ".join(parts).lower()


def _looks_like_token_limit(exc: Exception) -> bool:
    text = _exc_message(exc)
    return any(kw in text for kw in _TOKEN_LIMIT_KEYWORDS)


def classify_openai_error(exc: Exception) -> AppError:
    try:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            AuthenticationError,
            BadRequestError,
            RateLimitError,
        )
    except ImportError:
        return classify_unknown_error(exc)

    if isinstance(exc, APITimeoutError):
        return AppError(
            code="timeout",
            title="请求超时",
            message="连接模型服务超时，未能在限定时间内收到响应。",
            suggestion="请检查网络状况后重试；若文档很长，可尝试拆分后再生成。",
        )

    if isinstance(exc, APIConnectionError):
        return AppError(
            code="network",
            title="无法连接到模型服务",
            message="无法与 API 服务器建立连接。",
            suggestion="请检查网络、代理设置及 OPENAI_BASE_URL 是否正确，然后重试。",
        )

    if isinstance(exc, AuthenticationError):
        return AppError(
            code="api_auth",
            title="认证失败",
            message="API 密钥无效或已过期，无法调用模型。",
            suggestion="请检查 OPENAI_API_KEY 是否正确，或联系管理员更新密钥。",
        )

    if isinstance(exc, RateLimitError):
        return AppError(
            code="rate_limit",
            title="请求过于频繁",
            message="模型服务暂时限制了请求频率。",
            suggestion="请稍等片刻后重试，或更换其他模型。",
        )

    if isinstance(exc, BadRequestError) or (
        isinstance(exc, APIStatusError) and getattr(exc, "status_code", None) == 400
    ):
        text = _exc_message(exc)
        if "model" in text and any(
            kw in text
            for kw in (
                "not found",
                "does not exist",
                "does not have access",
                "not available",
                "unknown model",
                "invalid model",
            )
        ):
            return AppError(
                code="model_unsupported",
                title="模型不可用",
                message="当前配置的模型（含 Embedding 模型）在 API 端不可用或无权使用。",
                suggestion="请检查 EMBEDDING_MODEL_ID / 所选对话模型 ID 是否与服务商支持列表一致。",
            )
        if _looks_like_token_limit(exc):
            return AppError(
                code="token_limit",
                title="超出模型上下文限制",
                message="文档或对话内容过长，模型无法处理本次请求。",
                suggestion="请缩短文档、清空部分对话记录，或更换上下文更大的模型。",
            )
        return AppError(
            code="api_bad_request",
            title="请求被拒绝",
            message="模型服务拒绝了本次请求，参数或内容可能不符合要求。",
            suggestion="请检查所选模型是否可用，或尝试缩短文档后重试。",
        )

    if isinstance(exc, APIStatusError):
        code = getattr(exc, "status_code", None)
        if code == 401:
            return AppError(
                code="api_auth",
                title="认证失败",
                message="API 密钥无效或已过期，无法调用模型。",
                suggestion="请检查 OPENAI_API_KEY 是否正确，或联系管理员更新密钥。",
            )
        if code == 429:
            return AppError(
                code="rate_limit",
                title="请求过于频繁",
                message="模型服务暂时限制了请求频率。",
                suggestion="请稍等片刻后重试，或更换其他模型。",
            )
        return AppError(
            code="api_status",
            title="模型服务异常",
            message=f"模型服务返回错误（HTTP {code}）。",
            suggestion="请稍后重试；若持续失败，请联系管理员。",
        )

    if _looks_like_token_limit(exc):
        return AppError(
            code="token_limit",
            title="超出模型上下文限制",
            message="文档或对话内容过长，模型无法处理本次请求。",
            suggestion="请缩短文档、清空部分对话记录，或更换上下文更大的模型。",
        )

    text = _exc_message(exc)
    if isinstance(exc, TypeError) and (
        "metadatavalue" in text or "cannot convert python object to metadata" in text
    ):
        return chroma_write_error(str(exc))

    return AppError(
        code="api_unknown",
        title="模型调用失败",
        message="调用模型时发生错误，未能完成本次请求。",
        suggestion="请稍后重试；若问题持续，请检查网络与 API 配置。",
    )
