"""FastMCP 服务入口."""

from datetime import date
from textwrap import dedent
from typing import Optional

from fastmcp import FastMCP
from sqlalchemy import func
from sqlmodel import select
from starlette.requests import Request
from starlette.responses import JSONResponse

from brave_starr.database import get_session, init_db
from brave_starr.models import (
    AddRecordsResponse,
    GetRecordsResponse,
    IndexRecord,
    IndexRecordInput,
)

SERVER_INSTRUCTIONS = dedent(
    """
    BraveStarr 用于记录和查询微信指数数据。

    连接方式：
    - 仅支持 MCP Streamable HTTP
    - MCP 端点：`/mcp`
    - 健康检查：`/health`
    - `/mcp/health` 不是有效端点

    正确握手顺序：
    1. 先向 `/mcp` 发送 `initialize`
    2. 从响应头读取 `mcp-session-id`
    3. 发送 `notifications/initialized`
    4. 后续请求继续携带 `mcp-session-id` 与 `mcp-protocol-version`

    必需请求头：
    - `Content-Type: application/json`
    - `Accept: application/json, text/event-stream`

    可用工具：
    - `brave_starr_add_records`：批量添加或覆盖指数记录
    - `brave_starr_get_records`：按条件查询历史指数记录

    常见错误：
    - `404 /mcp/health`：请改用 `/health`
    - `406 Not Acceptable`：`Accept` 头缺少 `application/json` 或 `text/event-stream`
    - `400 Missing session ID`：未先完成 `initialize` 或未回传 `mcp-session-id`
    """
).strip()

# 创建 FastMCP 实例
mcp = FastMCP(
    name="BraveStarr",
    instructions=SERVER_INSTRUCTIONS,
)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(_: Request) -> JSONResponse:
    """容器与反向代理使用的健康检查."""
    return JSONResponse({"status": "healthy", "service": "brave-starr"})


@mcp.tool()
def brave_starr_add_records(records: list[IndexRecordInput]) -> AddRecordsResponse:
    """批量写入微信指数记录。

    适用场景：
    - 一次性新增多条记录
    - 用最新值覆盖同一 `keyword + record_date` 的旧记录

    输入要求：
    - 参数为 `records` 数组
    - `keyword`、`index_value`、`record_date` 必填
    - 单次最多 100 条

    返回语义：
    - `success=True` 表示本次批量处理完成
    - `inserted_count` 只统计新增，不统计覆盖
    - `message` 返回可直接展示给调用方的摘要信息
    """
    # 限制批量大小
    if len(records) > 100:
        return AddRecordsResponse(
            success=False, inserted_count=0, message="批量添加限制: 最多 100 条记录/次"
        )

    if not records:
        return AddRecordsResponse(success=True, inserted_count=0, message="没有需要添加的记录")

    try:
        with get_session() as session:
            inserted_count = 0

            for input_record in records:
                # 解析日期
                try:
                    record_date = date.fromisoformat(input_record.record_date)
                except ValueError:
                    return AddRecordsResponse(
                        success=False,
                        inserted_count=inserted_count,
                        message=f"日期格式错误: {input_record.record_date}, 请使用 YYYY-MM-DD 格式",
                    )

                # 检查是否已存在相同 keyword + record_date 的记录
                statement = select(IndexRecord).where(
                    IndexRecord.keyword == input_record.keyword,
                    IndexRecord.record_date == record_date,
                )
                existing = session.exec(statement).first()

                if existing:
                    # 更新现有记录
                    existing.index_value = input_record.index_value
                    existing.change_percent = input_record.change_percent
                    existing.trend = input_record.trend
                    existing.category = input_record.category
                    existing.note = input_record.note
                else:
                    # 创建新记录
                    new_record = IndexRecord(
                        keyword=input_record.keyword,
                        index_value=input_record.index_value,
                        change_percent=input_record.change_percent,
                        trend=input_record.trend,
                        category=input_record.category,
                        record_date=record_date,
                        note=input_record.note,
                    )
                    session.add(new_record)
                    inserted_count += 1

            session.commit()

            return AddRecordsResponse(
                success=True,
                inserted_count=inserted_count,
                message=f"成功处理 {len(records)} 条记录 (新增 {inserted_count} 条)",
            )

    except Exception as e:
        return AddRecordsResponse(
            success=False, inserted_count=0, message=f"数据库操作失败: {str(e)}"
        )


@mcp.tool()
def brave_starr_get_records(
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
) -> GetRecordsResponse:
    """查询微信指数历史记录。

    支持按关键词、日期范围、分类筛选。

    输入规则：
    - 所有筛选条件均可选
    - 日期格式必须为 `YYYY-MM-DD`
    - `limit` 默认 100

    返回语义：
    - `records` 为符合条件的记录列表
    - `total` 为未分页前的总数
    - 结果按 `record_date DESC` 排序
    """
    try:
        with get_session() as session:
            # 构建基础查询
            statement = select(IndexRecord)

            # 添加筛选条件
            if keyword:
                statement = statement.where(IndexRecord.keyword == keyword)

            if start_date:
                try:
                    start = date.fromisoformat(start_date)
                    statement = statement.where(IndexRecord.record_date >= start)
                except ValueError:
                    return GetRecordsResponse(records=[], total=0)

            if end_date:
                try:
                    end = date.fromisoformat(end_date)
                    statement = statement.where(IndexRecord.record_date <= end)
                except ValueError:
                    return GetRecordsResponse(records=[], total=0)

            if category:
                statement = statement.where(IndexRecord.category == category)

            # 计算总数
            count_statement = select(func.count()).select_from(statement.subquery())
            total = session.exec(count_statement).one()

            # 排序和分页 - 使用 SQLAlchemy desc() 函数，忽略 mypy 对 SQLModel 特殊属性的检查
            from sqlalchemy import desc

            statement = statement.order_by(desc(IndexRecord.record_date))  # type: ignore
            statement = statement.limit(limit)

            # 执行查询
            results = session.exec(statement).all()

            # 将会话内的 ORM 对象转换为响应模型（避免会话关闭后访问延迟加载属性）
            records = []
            for r in results:
                records.append(
                    IndexRecord(
                        id=r.id,
                        keyword=r.keyword,
                        index_value=r.index_value,
                        change_percent=r.change_percent,
                        trend=r.trend,
                        category=r.category,
                        record_date=r.record_date,
                        note=r.note,
                        created_at=r.created_at,
                    )
                )

            return GetRecordsResponse(records=records, total=total)

    except Exception:
        return GetRecordsResponse(records=[], total=0)


def main() -> None:
    """服务入口函数."""
    import argparse

    parser = argparse.ArgumentParser(description="BraveStarr MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="http",
        help="传输方式 (默认: http)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP 监听地址")
    parser.add_argument("--port", type=int, default=8000, help="HTTP 监听端口")
    args = parser.parse_args()

    # 初始化数据库
    init_db()

    # 运行 MCP 服务
    if args.transport == "stdio":
        mcp.run()
        return

    mcp.run(
        transport=args.transport,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    main()
