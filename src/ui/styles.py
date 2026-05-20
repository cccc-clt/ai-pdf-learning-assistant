"""浅色主题统一 CSS（固定 light，覆盖 Streamlit 默认组件）。"""

from __future__ import annotations

# 设计令牌
_BG_PAGE = "#F8FAFC"
_BG_CARD = "#FFFFFF"
_BG_SUBTLE = "#F3F4F6"
_TEXT_PRIMARY = "#111827"
_TEXT_BODY = "#1F2937"
_TEXT_MUTED = "#6B7280"
_BORDER = "#E5E7EB"
_ACCENT = "#10B981"
_ACCENT_ALT = "#2563EB"
_WARN_BG = "#FEF3C7"
_WARN_TEXT = "#92400E"
_SUCCESS_BG = "#DCFCE7"
_SUCCESS_TEXT = "#166534"
_INFO_BG = "#DBEAFE"
_INFO_TEXT = "#1E40AF"
_ERROR_BG = "#FEE2E2"
_ERROR_TEXT = "#991B1B"

LIGHT_APP_CSS = f"""
<style>
  :root {{
    color-scheme: light;
    --ai-bg: {_BG_PAGE};
    --ai-card: {_BG_CARD};
    --ai-text: {_TEXT_PRIMARY};
    --ai-body: {_TEXT_BODY};
    --ai-muted: {_TEXT_MUTED};
    --ai-border: {_BORDER};
    --ai-accent: {_ACCENT};
    --ai-accent-soft: rgba(16, 185, 129, 0.12);
  }}

  .stApp {{
    background: var(--ai-bg) !important;
    color: var(--ai-body) !important;
  }}

  .main .block-container {{
    color: var(--ai-body);
  }}

  /* —— 侧栏 —— */
  section[data-testid="stSidebar"] {{
    background: var(--ai-card) !important;
    border-right: 1px solid var(--ai-border) !important;
  }}
  section[data-testid="stSidebar"] .stMarkdown,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3,
  section[data-testid="stSidebar"] h4 {{
    color: var(--ai-body) !important;
  }}
  section[data-testid="stSidebar"] .stCaption,
  section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
    color: var(--ai-muted) !important;
  }}
  [data-testid="stSidebarHeader"] {{
    color: var(--ai-text) !important;
  }}

  /* —— 标题与正文 —— */
  h1, h2, h3, h4, h5, h6 {{
    color: var(--ai-text) !important;
  }}
  .stMarkdown, .stMarkdown p, .stMarkdown li {{
    color: var(--ai-body);
  }}
  .stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--ai-muted) !important;
  }}

  /* —— 指标 —— */
  [data-testid="stMetricValue"] {{
    color: var(--ai-text) !important;
  }}
  [data-testid="stMetricLabel"] {{
    color: var(--ai-muted) !important;
  }}

  /* —— 上传区 —— */
  [data-testid="stFileUploader"] {{
    background: var(--ai-card) !important;
  }}
  [data-testid="stFileUploader"] section {{
    background: var(--ai-card) !important;
    border: 1px dashed var(--ai-border) !important;
    border-radius: 12px !important;
  }}
  [data-testid="stFileUploader"] span,
  [data-testid="stFileUploader"] small,
  [data-testid="stFileUploader"] label {{
    color: var(--ai-body) !important;
  }}
  [data-testid="stFileUploader"] button {{
    background: var(--ai-accent) !important;
    color: #ffffff !important;
    border: none !important;
  }}

  /* —— 下拉框 / 选择器 —— */
  div[data-baseweb="select"] > div {{
    background-color: var(--ai-card) !important;
    color: var(--ai-text) !important;
    border-color: var(--ai-border) !important;
  }}
  div[data-baseweb="popover"] {{
    background: var(--ai-card) !important;
  }}
  ul[data-baseweb="menu"] {{
    background: var(--ai-card) !important;
  }}
  li[data-baseweb="option"] {{
    color: var(--ai-text) !important;
    background: var(--ai-card) !important;
  }}
  li[data-baseweb="option"]:hover {{
    background: var(--ai-accent-soft) !important;
  }}

  /* —— 输入框 —— */
  .stTextInput input,
  .stTextArea textarea,
  [data-testid="stChatInput"] textarea,
  input[type="text"],
  textarea {{
    background-color: var(--ai-card) !important;
    color: var(--ai-text) !important;
    border-color: var(--ai-border) !important;
  }}
  .stTextInput label,
  .stTextArea label,
  .stSelectbox label {{
    color: var(--ai-body) !important;
  }}

  /* —— 按钮 —— */
  .stButton > button {{
    background: var(--ai-card) !important;
    color: var(--ai-text) !important;
    border: 1px solid var(--ai-border) !important;
  }}
  .stButton > button[kind="primary"],
  .stButton > button[data-testid="baseButton-primary"] {{
    background: var(--ai-accent) !important;
    color: #ffffff !important;
    border-color: var(--ai-accent) !important;
  }}
  .stButton > button[kind="secondary"] {{
    background: var(--ai-card) !important;
    color: var(--ai-text) !important;
  }}

  /* —— Tabs —— */
  div[data-testid="stTabs"] button {{
    color: var(--ai-muted) !important;
    background: transparent !important;
  }}
  div[data-testid="stTabs"] [aria-selected="true"] {{
    color: var(--ai-accent) !important;
    border-bottom-color: var(--ai-accent) !important;
  }}

  /* —— Expander —— */
  [data-testid="stExpander"] summary,
  [data-testid="stExpander"] [data-testid="stMarkdownContainer"] {{
    color: var(--ai-text) !important;
    background: var(--ai-card) !important;
  }}
  [data-testid="stExpander"] details {{
    border-color: var(--ai-border) !important;
    background: var(--ai-card) !important;
  }}

  /* —— 提示框 —— */
  div[data-testid="stAlert"] {{
    border-radius: 10px !important;
  }}
  div[data-testid="stNotification"][data-baseweb="notification"] {{
    background: var(--ai-card) !important;
  }}
  [data-testid="stAlert"]:has([data-testid="stAlertContainer"][data-type="info"]),
  .stAlert[data-testid="stNotification"]:has(svg[data-testid*="info"]) {{
    background-color: {_INFO_BG} !important;
    color: {_INFO_TEXT} !important;
  }}
  [data-baseweb="toast"] {{
    background: var(--ai-card) !important;
  }}

  /* Streamlit 原生 alert 容器（按图标/结构尽量覆盖） */
  [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {{
    color: inherit !important;
  }}
  div.stAlert {{
    border-radius: 10px !important;
  }}
  /* info */
  [data-testid="stAlertContainer"][data-type="info"],
  .stAlert > div:has(svg[aria-label="info"]) {{
    background-color: {_INFO_BG} !important;
    color: {_INFO_TEXT} !important;
  }}
  /* success */
  [data-testid="stAlertContainer"][data-type="success"] {{
    background-color: {_SUCCESS_BG} !important;
    color: {_SUCCESS_TEXT} !important;
  }}
  /* warning */
  [data-testid="stAlertContainer"][data-type="warning"] {{
    background-color: {_WARN_BG} !important;
    color: {_WARN_TEXT} !important;
  }}
  /* error */
  [data-testid="stAlertContainer"][data-type="error"] {{
    background-color: {_ERROR_BG} !important;
    color: {_ERROR_TEXT} !important;
  }}

  /* Element 异常块 */
  .stException {{
    background: {_ERROR_BG} !important;
    color: {_ERROR_TEXT} !important;
  }}

  /* —— 代码块 —— */
  .stCode, pre, code {{
    background: {_BG_SUBTLE} !important;
    color: {_TEXT_BODY} !important;
  }}

  /* —— 顶栏 / 状态 / 旋转器 —— */
  header[data-testid="stHeader"] {{
    background: rgba(248, 250, 252, 0.92) !important;
  }}
  [data-testid="stStatusWidget"],
  [data-testid="stStatusWidget"] label {{
    color: var(--ai-body) !important;
  }}
  [data-testid="stSpinner"] {{
    color: var(--ai-muted) !important;
  }}

  /* —— 分隔线 —— */
  hr {{
    border-color: var(--ai-border) !important;
  }}

  /* —— 聊天气泡区域 —— */
  [data-testid="stChatMessage"] {{
    background: var(--ai-card) !important;
    color: var(--ai-body) !important;
    border: 1px solid var(--ai-border) !important;
  }}
  [data-testid="stChatMessage"] .stMarkdown {{
    color: var(--ai-body) !important;
  }}

  /* —— 自定义品牌组件 —— */
  .ai-brand-wrap {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.25rem;
    padding: 0.75rem 0;
  }}
  .ai-brand {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
  }}
  .ai-logo {{
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--ai-accent), {_ACCENT_ALT});
    color: #ffffff;
    font-weight: 800;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    letter-spacing: -0.02em;
  }}
  .ai-title {{
    margin: 0;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--ai-text);
  }}
  .ai-subtitle {{
    margin: 0.15rem 0 0 0;
    font-size: 0.9rem;
    color: var(--ai-muted);
  }}
  .ai-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    color: var(--ai-muted);
    border: 1px solid var(--ai-border);
    background: var(--ai-card);
  }}
  .ai-pill-online {{
    color: {_SUCCESS_TEXT};
    border-color: #86efac;
    background: {_SUCCESS_BG};
  }}
  .ai-pill-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--ai-muted);
  }}
  .ai-pill-online .ai-pill-dot {{
    background: var(--ai-accent);
  }}
  .ai-card {{
    background: var(--ai-card);
    border: 1px solid var(--ai-border);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.75rem;
    color: var(--ai-body);
  }}
  .ai-card-tight {{
    padding: 0.85rem 1rem;
  }}
  .ai-workbench {{
    padding: 0.75rem 0.9rem 1rem;
  }}
  .ai-inline-muted {{
    font-size: 0.78rem;
    color: var(--ai-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}
  .ai-inline-title {{
    font-size: 1.05rem;
    font-weight: 600;
    margin-top: 0.2rem;
    color: var(--ai-text);
  }}
  .ai-meta-sub {{
    font-size: 0.85rem;
    color: var(--ai-muted);
    margin-top: 0.25rem;
  }}
  .ai-chat-shell {{
    border-radius: 12px;
    border: 1px solid var(--ai-border);
    background: {_BG_SUBTLE};
    padding: 0.5rem 0.65rem 0.75rem;
  }}
  .ai-chat-workspace .ai-chat-hint {{
    font-size: 0.82rem;
    color: var(--ai-muted);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }}
  .ai-dot-row {{
    display: inline-flex;
    gap: 4px;
    align-items: center;
  }}
  .ai-dot {{
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--ai-accent);
    opacity: 0.85;
    animation: ai-bounce 1.2s infinite ease-in-out;
  }}
  .ai-dot:nth-child(2) {{ animation-delay: 0.15s; }}
  .ai-dot:nth-child(3) {{ animation-delay: 0.3s; }}
  @keyframes ai-bounce {{
    0%, 80%, 100% {{ transform: translateY(0); opacity: 0.5; }}
    40% {{ transform: translateY(-3px); opacity: 1; }}
  }}
  .ai-typing-inline {{
    margin-left: 0.35rem;
  }}
  .ai-chat-tab-empty {{
    text-align: center;
    padding: 2.5rem 1rem 2rem;
    color: var(--ai-muted);
  }}
  .ai-chat-tab-empty-icon {{
    width: 48px;
    height: 48px;
    margin: 0 auto 0.75rem;
    border-radius: 14px;
    background: var(--ai-accent-soft);
    border: 1px dashed var(--ai-border);
  }}
  .ai-chat-tab-empty-title {{
    font-weight: 600;
    color: var(--ai-text);
    margin-bottom: 0.35rem;
  }}
  .ai-chat-tab-empty-desc {{
    font-size: 0.88rem;
    margin: 0;
    color: var(--ai-muted);
  }}
  .ai-summary-wrap {{
    max-height: 70vh;
    overflow: auto;
    padding: 0.5rem 0.25rem;
    line-height: 1.65;
    color: var(--ai-body);
  }}
  .ai-summary-wrap table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 0.9rem;
  }}
  .ai-summary-wrap th, .ai-summary-wrap td {{
    border: 1px solid var(--ai-border);
    padding: 0.45rem 0.55rem;
    color: var(--ai-body);
  }}

  /* 覆盖系统深色偏好下 Streamlit 仍注入的浅色字 */
  @media (prefers-color-scheme: dark) {{
    .stApp,
    section[data-testid="stSidebar"],
    .main .block-container {{
      background: var(--ai-bg) !important;
      color: var(--ai-body) !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    [data-testid="stFileUploader"] section,
    div[data-baseweb="select"] > div,
    .stTextInput input,
    [data-testid="stChatInput"] textarea {{
      background-color: var(--ai-card) !important;
      color: var(--ai-text) !important;
    }}
  }}
</style>
"""
