"""测试 MCP 服务."""

import sys
import uuid

import pytest
from sqlalchemy import create_engine, event
from sqlmodel import SQLModel

from brave_starr import database as db_module
from brave_starr.models import IndexRecordInput
from brave_starr.server import (
    SERVER_INSTRUCTIONS,
    brave_starr_add_records,
    brave_starr_get_records,
    main,
    mcp,
)


@pytest.fixture(autouse=True)
def temp_database(monkeypatch, tmp_path):
    """使用临时数据库文件进行测试."""
    # 创建临时数据库文件
    temp_db_path = tmp_path / f"test_{uuid.uuid4().hex}.db"

    # 创建新引擎指向临时数据库
    db_url = f"sqlite:///{temp_db_path}"
    test_engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})

    # 启用外键
    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # 保存原始引擎并替换为测试引擎
    original_engine = db_module._engine
    db_module._engine = test_engine

    # 创建表
    SQLModel.metadata.create_all(test_engine)

    yield

    # 恢复原始引擎
    db_module._engine = original_engine


def test_add_single_record():
    """测试添加单条记录."""
    records = [
        IndexRecordInput(
            keyword="Claude",
            index_value=1234567,
            change_percent=15.5,
            trend="↑",
            category="AI",
            record_date="2024-01-15",
            note="测试",
        )
    ]

    result = brave_starr_add_records(records)

    assert result.success is True
    assert result.inserted_count == 1


def test_add_multiple_records():
    """测试批量添加记录."""
    records = [
        IndexRecordInput(keyword="Claude", index_value=1234567, record_date="2024-01-15"),
        IndexRecordInput(keyword="Cursor", index_value=876543, record_date="2024-01-15"),
    ]

    result = brave_starr_add_records(records)

    assert result.success is True
    assert result.inserted_count == 2


def test_upsert_existing_record():
    """测试更新已存在的记录."""
    # 先添加一条记录
    records = [IndexRecordInput(keyword="Claude", index_value=1000, record_date="2024-01-15")]
    brave_starr_add_records(records)

    # 用相同 keyword + date 添加新值
    records = [IndexRecordInput(keyword="Claude", index_value=2000, record_date="2024-01-15")]
    result = brave_starr_add_records(records)

    assert result.success is True
    # upsert 时更新不计入新增
    assert result.inserted_count == 0

    # 验证值已更新
    query_result = brave_starr_get_records(keyword="Claude")
    assert query_result.records[0].index_value == 2000


def test_add_records_limit():
    """测试批量添加限制."""
    records = [
        IndexRecordInput(keyword=f"Keyword{i}", index_value=i, record_date="2024-01-15")
        for i in range(101)
    ]

    result = brave_starr_add_records(records)

    assert result.success is False
    assert "最多 100 条" in result.message


def test_get_records_empty():
    """测试空记录查询."""
    result = brave_starr_get_records()

    assert result.records == []
    assert result.total == 0


def test_get_records_by_keyword():
    """测试按关键词查询."""
    # 添加测试数据
    records = [
        IndexRecordInput(keyword="Claude", index_value=1000, record_date="2024-01-15"),
        IndexRecordInput(keyword="Cursor", index_value=2000, record_date="2024-01-15"),
    ]
    brave_starr_add_records(records)

    # 查询特定关键词
    result = brave_starr_get_records(keyword="Claude")

    assert result.total == 1
    assert result.records[0].keyword == "Claude"
    assert result.records[0].index_value == 1000


def test_get_records_by_date_range():
    """测试按日期范围查询."""
    # 添加测试数据
    records = [
        IndexRecordInput(keyword="Claude", index_value=1000, record_date="2024-01-10"),
        IndexRecordInput(keyword="Claude", index_value=2000, record_date="2024-01-15"),
        IndexRecordInput(keyword="Claude", index_value=3000, record_date="2024-01-20"),
    ]
    brave_starr_add_records(records)

    # 按日期范围查询
    result = brave_starr_get_records(
        keyword="Claude", start_date="2024-01-12", end_date="2024-01-18"
    )

    assert result.total == 1
    assert result.records[0].record_date.isoformat() == "2024-01-15"


def test_get_records_limit():
    """测试查询条数限制."""
    # 添加多条记录 (使用不同日期，避免月份天数问题)
    records = [
        IndexRecordInput(
            keyword=f"Keyword{i}",
            index_value=i,
            record_date=f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
        )
        for i in range(50)
    ]
    brave_starr_add_records(records)

    # 限制返回 10 条
    result = brave_starr_get_records(limit=10)

    assert len(result.records) == 10
    assert result.total == 50


def test_get_records_ordering():
    """测试查询结果排序 (按日期倒序)."""
    # 添加不同日期的记录
    records = [
        IndexRecordInput(keyword="Claude", index_value=1000, record_date="2024-01-10"),
        IndexRecordInput(keyword="Claude", index_value=2000, record_date="2024-01-20"),
        IndexRecordInput(keyword="Claude", index_value=1500, record_date="2024-01-15"),
    ]
    brave_starr_add_records(records)

    result = brave_starr_get_records(keyword="Claude")

    # 验证按日期倒序
    dates = [r.record_date.isoformat() for r in result.records]
    assert dates == ["2024-01-20", "2024-01-15", "2024-01-10"]


def test_invalid_date_format():
    """测试无效日期格式处理."""
    records = [IndexRecordInput(keyword="Claude", index_value=1000, record_date="invalid-date")]

    result = brave_starr_add_records(records)

    assert result.success is False
    assert "日期格式错误" in result.message


def test_empty_records():
    """测试空记录列表."""
    result = brave_starr_add_records([])

    assert result.success is True
    assert result.inserted_count == 0


def test_main_http_transport_uses_public_run_api(monkeypatch):
    """测试 HTTP 模式使用 FastMCP 官方公开 run API."""
    monkeypatch.setattr(sys, "argv", ["brave-starr", "--transport", "http", "--host", "0.0.0.0", "--port", "9000"])

    init_db_called = False
    run_called_with: dict[str, object] = {}

    def fake_init_db() -> None:
        nonlocal init_db_called
        init_db_called = True

    def fake_run(*args, **kwargs) -> None:
        run_called_with["args"] = args
        run_called_with["kwargs"] = kwargs

    monkeypatch.setattr("brave_starr.server.init_db", fake_init_db)
    monkeypatch.setattr("brave_starr.server.mcp.run", fake_run)

    main()

    assert init_db_called is True
    assert run_called_with["args"] == ()
    assert run_called_with["kwargs"] == {
        "transport": "http",
        "host": "0.0.0.0",
        "port": 9000,
    }


def test_main_defaults_to_http_transport(monkeypatch):
    """测试默认启动方式为 HTTP Streamable."""
    monkeypatch.setattr(sys, "argv", ["brave-starr"])

    init_db_called = False
    run_called_with: dict[str, object] = {}

    def fake_init_db() -> None:
        nonlocal init_db_called
        init_db_called = True

    def fake_run(*args, **kwargs) -> None:
        run_called_with["args"] = args
        run_called_with["kwargs"] = kwargs

    monkeypatch.setattr("brave_starr.server.init_db", fake_init_db)
    monkeypatch.setattr("brave_starr.server.mcp.run", fake_run)

    main()

    assert init_db_called is True
    assert run_called_with["args"] == ()
    assert run_called_with["kwargs"] == {
        "transport": "http",
        "host": "0.0.0.0",
        "port": 8000,
    }


def test_server_instructions_describe_streamable_http_handshake():
    """测试 instructions 明确描述 Streamable HTTP 握手要求."""
    assert mcp.instructions == SERVER_INSTRUCTIONS
    assert "/mcp" in SERVER_INSTRUCTIONS
    assert "/health" in SERVER_INSTRUCTIONS
    assert "/mcp/health" in SERVER_INSTRUCTIONS
    assert "initialize" in SERVER_INSTRUCTIONS
    assert "mcp-session-id" in SERVER_INSTRUCTIONS
    assert "application/json, text/event-stream" in SERVER_INSTRUCTIONS
