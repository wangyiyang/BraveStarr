"""测试数据库配置."""

from pathlib import Path

from brave_starr.database import DEFAULT_DB_PATH, resolve_db_path


def test_resolve_db_path_defaults_to_repo_data(monkeypatch):
    """未配置环境变量时，使用仓库默认数据目录."""
    monkeypatch.delenv("BRAVE_STARR_DB_PATH", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    assert resolve_db_path() == DEFAULT_DB_PATH


def test_resolve_db_path_prefers_brave_starr_env(monkeypatch, tmp_path):
    """优先使用 BRAVE_STARR_DB_PATH，兼容旧变量名."""
    new_path = tmp_path / "custom.db"
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "legacy.db"))
    monkeypatch.setenv("BRAVE_STARR_DB_PATH", str(new_path))

    assert resolve_db_path() == Path(new_path).resolve()
