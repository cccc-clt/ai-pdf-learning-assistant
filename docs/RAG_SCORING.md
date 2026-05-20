# RAG 检索分数说明

## 行为

- 建库时使用 Chroma 集合元数据 `hnsw:space: cosine`，与 OpenAI Embedding 的余弦相似度一致。
- 检索优先使用 `similarity_search_with_relevance_scores`；若返回的原始值 **大于 1**，按**距离**处理并归一化为 `1 / (1 + distance)`。
- 过滤条件：归一化相关度 `>= RAG_SCORE_THRESHOLD`（默认 `0.2`）。
- 若阈值过滤后无结果但检索到候选片段，将回退为按相关度取 Top-K（避免误报「无法找到答案」）。
- 建库元数据须为 `{"hnsw": {"space": "cosine"}}`，与 LangChain Chroma 一致。

## 调参

| 现象 | 建议 |
|------|------|
| 几乎总是「无法找到相关答案」 | 降低 `RAG_SCORE_THRESHOLD`（如 `0.15`），或**重新上传 PDF** 以用正确 cosine 元数据重建索引 |
| 回答与问题无关、噪声片段多 | 提高阈值（如 `0.45`–`0.5`） |

## 实现位置

- 归一化：[`src/utils/rag_scores.py`](../src/utils/rag_scores.py)
- 检索与过滤：[`src/services/rag_service.py`](../src/services/rag_service.py)
