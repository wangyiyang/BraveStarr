"""SQLModel 数据模型定义."""

from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class IndexRecord(SQLModel, table=True):
    """微信指数记录表."""

    __tablename__ = "index_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str = Field(index=True, description="关键词")
    index_value: int = Field(description="微信指数值")
    change_percent: Optional[float] = Field(default=None, description="日环比百分比")
    trend: Optional[str] = Field(default=None, description="趋势符号: ↑/↓/→")
    category: Optional[str] = Field(default=None, description="分类标签")
    record_date: date = Field(index=True, description="记录日期 (YYYY-MM-DD)")
    note: Optional[str] = Field(default=None, description="备注")
    created_at: datetime = Field(default_factory=datetime.now, description="记录创建时间")

    class Config:
        """Pydantic 配置."""

        json_schema_extra = {
            "example": {
                "keyword": "Claude",
                "index_value": 1234567,
                "change_percent": 15.5,
                "trend": "↑",
                "category": "AI",
                "record_date": "2024-01-15",
                "note": "测试记录",
            }
        }


class IndexRecordInput(SQLModel):
    """指数记录输入模型 (用于批量添加)."""

    keyword: str = Field(description="关键词")
    index_value: int = Field(description="微信指数值")
    change_percent: Optional[float] = Field(default=None, description="日环比百分比")
    trend: Optional[str] = Field(default=None, description="趋势符号: ↑/↓/→")
    category: Optional[str] = Field(default=None, description="分类标签")
    record_date: str = Field(description="记录日期 (YYYY-MM-DD)")
    note: Optional[str] = Field(default=None, description="备注")


class AddRecordsResponse(SQLModel):
    """批量添加记录响应."""

    success: bool = Field(description="操作是否成功")
    inserted_count: int = Field(description="插入记录数量")
    message: str = Field(description="操作结果消息")


class GetRecordsResponse(SQLModel):
    """查询记录响应."""

    records: list[IndexRecord] = Field(description="记录列表")
    total: int = Field(description="符合条件的记录总数")
