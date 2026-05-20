"""服务层协议（便于测试与替换实现）。"""

from __future__ import annotations

from typing import Protocol


class ChatClient(Protocol):
    def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float,
    ) -> str: ...


class VectorStore(Protocol):
    def build_index(
        self,
        document_text: str,
        collection_name: str,
        api_key: str,
        base_url: str | None,
    ) -> int: ...

    def retrieve_chunks(
        self,
        question: str,
        collection_name: str,
        api_key: str,
        base_url: str | None,
    ) -> list[tuple[str, float]]: ...

    def clear_collection(self, collection_name: str) -> None: ...
