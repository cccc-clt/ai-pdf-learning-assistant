"""项目根路径与启动检查。"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def project_root() -> Path:
    return _PROJECT_ROOT


def _load_dotenv() -> None:
    """从项目根目录加载 .env（不覆盖已存在的环境变量）。"""
    env_path = _PROJECT_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
    except ImportError:
        pass


def ensure_project_ready() -> None:
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    _load_dotenv()
    marker = _PROJECT_ROOT / "src" / "core" / "exceptions.py"
    if not marker.is_file():
        raise RuntimeError(
            f"缺少核心模块（路径：{marker}）。请确认项目文件完整并已保存。"
        )
    for sub in ("data", ".streamlit"):
        (_PROJECT_ROOT / sub).mkdir(parents=True, exist_ok=True)
