"""RAG 分数归一化单测。"""

from src.utils.rag_scores import passes_relevance_threshold, to_relevance_score


def test_relevance_already_normalized():
    assert to_relevance_score(0.85) == 0.85
    assert to_relevance_score(1.0) == 1.0
    assert to_relevance_score(0.0) == 0.0


def test_distance_to_relevance():
    assert to_relevance_score(2.0) == 1.0 / 3.0
    assert to_relevance_score(100.0) < 0.02


def test_threshold():
    assert passes_relevance_threshold(0.25, 0.2)
    assert not passes_relevance_threshold(0.15, 0.2)
