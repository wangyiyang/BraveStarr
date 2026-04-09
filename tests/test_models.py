"""测试数据模型."""

from datetime import date, datetime

from brave_starr.models import (
    AddRecordsResponse,
    GetRecordsResponse,
    IndexRecord,
    IndexRecordInput,
)


def test_index_record_creation():
    """测试 IndexRecord 创建."""
    record = IndexRecord(
        id=1,
        keyword="Claude",
        index_value=1234567,
        change_percent=15.5,
        trend="↑",
        category="AI",
        record_date=date(2024, 1, 15),
        note="测试记录",
    )

    assert record.id == 1
    assert record.keyword == "Claude"
    assert record.index_value == 1234567
    assert record.change_percent == 15.5
    assert record.trend == "↑"
    assert record.category == "AI"
    assert record.record_date == date(2024, 1, 15)
    assert record.note == "测试记录"
    assert isinstance(record.created_at, datetime)


def test_index_record_input():
    """测试 IndexRecordInput 创建."""
    record = IndexRecordInput(
        keyword="Cursor",
        index_value=876543,
        change_percent=-3.2,
        trend="↓",
        category="开发工具",
        record_date="2024-01-15",
        note="测试输入",
    )

    assert record.keyword == "Cursor"
    assert record.index_value == 876543
    assert record.change_percent == -3.2
    assert record.trend == "↓"
    assert record.category == "开发工具"
    assert record.record_date == "2024-01-15"
    assert record.note == "测试输入"


def test_add_records_response():
    """测试 AddRecordsResponse."""
    response = AddRecordsResponse(success=True, inserted_count=5, message="成功插入 5 条记录")

    assert response.success is True
    assert response.inserted_count == 5
    assert response.message == "成功插入 5 条记录"


def test_get_records_response():
    """测试 GetRecordsResponse."""
    record = IndexRecord(id=1, keyword="Test", index_value=1000, record_date=date(2024, 1, 1))
    response = GetRecordsResponse(records=[record], total=1)

    assert len(response.records) == 1
    assert response.total == 1
    assert response.records[0].keyword == "Test"
