"""从 PDF 字节流提取纯文本。"""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.core.exceptions import empty_file_error, pdf_parse_error


def _read_pdf(data: bytes) -> PdfReader:
    if not data:
        raise empty_file_error()
    try:
        return PdfReader(BytesIO(data))
    except PdfReadError as e:
        raise pdf_parse_error(str(e)) from e
    except Exception as e:
        raise pdf_parse_error(str(e)) from e


def extract_text_from_pdf_bytes(data: bytes) -> str:
    reader = _read_pdf(data)
    if len(reader.pages) == 0:
        raise empty_file_error()
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n\n".join(chunks).strip()


def pdf_page_count(data: bytes) -> int:
    reader = _read_pdf(data)
    return len(reader.pages)


def load_pdf_bytes(data: bytes) -> tuple[str, int]:
    """解析 PDF，返回 (正文, 页数)。正文可能为空（扫描版）。"""
    reader = _read_pdf(data)
    pages = len(reader.pages)
    if pages == 0:
        raise empty_file_error()
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n\n".join(chunks).strip(), pages
