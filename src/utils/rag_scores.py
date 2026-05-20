"""Chroma / LangChain 检索分数归一化为 0–1 相关度（越高越相关）。"""

from __future__ import annotations


def to_relevance_score(raw_score: float) -> float:
    """
    将检索分数转为 [0, 1] 相关度（越大越相关）。

    LangChain Chroma 的 ``similarity_search_with_relevance_scores`` 已返回相关度；
    仅当原始值明显为距离（>1）时再按距离映射。
    """
    s = float(raw_score)
    if s > 1.0:
        return 1.0 / (1.0 + s)
    return max(0.0, min(1.0, s))


def normalize_relevance_score(raw_score: float) -> float:
    """兼容旧名。"""
    return to_relevance_score(raw_score)


def passes_relevance_threshold(normalized: float, threshold: float) -> bool:
    return normalized >= threshold
