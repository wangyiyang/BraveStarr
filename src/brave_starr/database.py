"""数据库连接和会话管理."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from sqlalchemy import Engine, create_engine, event
from sqlmodel import Session, SQLModel

# 数据库文件路径
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "brave_starr.db"

_engine: Engine | None = None


def get_engine() -> Engine:
    """获取或创建数据库引擎 (单例模式).

    Returns:
        SQLAlchemy 引擎实例
    """
    global _engine
    if _engine is None:
        # 确保数据目录存在
        DB_DIR.mkdir(parents=True, exist_ok=True)

        # 创建引擎 (SQLite)
        db_url = f"sqlite:///{DB_PATH}"
        _engine = create_engine(
            db_url,
            echo=False,  # 生产环境关闭 SQL 日志
            connect_args={"check_same_thread": False},  # 允许多线程访问
        )

        # 启用外键支持 (SQLite 默认关闭)
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


def init_db() -> None:
    """初始化数据库,创建所有表.

    基于 SQLModel 元数据创建表结构。
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """获取数据库会话 (上下文管理器).

    Yields:
        SQLModel 会话实例

    Example:
        with get_session() as session:
            record = IndexRecord(keyword="test", ...)
            session.add(record)
            session.commit()
    """
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
