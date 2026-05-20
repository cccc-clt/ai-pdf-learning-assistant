"""复制为 app_settings.py 并填写密钥（勿提交含真实密钥的文件）。"""

# 密钥请写在项目根目录 .env，勿在此文件填写真实 Key
OPENAI_BASE_URL = ""
OPENAI_API_KEY = ""

DEFAULT_MODEL_ID = "gpt-4o-mini"

# 可选：API 请求超时（秒）、上下文预检上限（tokens，为 completion 预留余量）
OPENAI_TIMEOUT = 120
MAX_CONTEXT_TOKENS = 120_000

# RAG：Embedding 模型、Chroma 持久化目录、检索参数
# 向量索引专用；与侧栏对话模型 DEFAULT_MODEL_ID 无关
EMBEDDING_MODEL_ID = "text-embedding-3-small"
CHROMA_PERSIST_DIR = ""  # 留空则使用项目下 data/chroma
RAG_TOP_K = 6
RAG_CHUNK_SIZE = 800
RAG_CHUNK_OVERLAP = 120
RAG_SCORE_THRESHOLD = 0.2

MODEL_OPTIONS: tuple[tuple[str, str], ...] = (
    ("GPT-4o mini（推荐）", "gpt-4o-mini"),
    ("GPT-4o", "gpt-4o"),
    ("GPT-4.1 mini", "gpt-4.1-mini"),
    ("GPT-4.1", "gpt-4.1"),
    ("o4-mini", "o4-mini"),
    ("o3-mini", "o3-mini"),
    ("GPT-3.5 Turbo", "gpt-3.5-turbo"),
)
