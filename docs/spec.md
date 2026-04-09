# BraveStarr 需求规格

## 概述

本文档定义 BraveStarr MVP 的功能需求、数据模型和 MCP 工具接口规范。

## MCP 传输约束

BraveStarr 对外只提供 **MCP Streamable HTTP**。

- MCP 端点：`/mcp`
- 健康检查：`/health`
- 不支持：`/mcp/health`

### 握手前置条件

客户端必须先完成 `initialize`，再发送 `notifications/initialized`，之后才能稳定调用 `tools/list` 与 `tools/call`。

### 请求头要求

所有 `POST /mcp` 请求必须包含：

- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`

初始化之后的请求必须继续携带：

- `mcp-session-id`
- `mcp-protocol-version`

## 功能需求

### FR-01: 写入指数记录

**描述**：通过 MCP 工具批量写入微信指数记录到 SQLite 数据库。

**输入**：
- JSON 格式的记录数组
- 每条记录包含关键词、指数值、日期等字段

**输出**：
- 操作结果（成功/失败）
- 插入记录数量

**约束**：
- `keyword` 和 `record_date` 为必填字段
- 同一关键词同一天仅保留最新记录（覆盖策略）

### FR-02: 查询指数记录

**描述**：通过 MCP 工具按条件查询历史指数记录。

**输入**：
- 筛选条件：关键词、日期范围、分类
- 分页参数：`limit`

**输出**：
- 符合条件的记录列表
- 记录总数

**约束**：
- 默认按日期倒序排列
- 默认返回最近 100 条记录

## 数据模型

### 表：`index_records`

```sql
CREATE TABLE index_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    index_value INTEGER NOT NULL,
    change_percent REAL,
    trend TEXT,
    category TEXT,
    record_date DATE NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_keyword_date ON index_records(keyword, record_date);
CREATE INDEX idx_record_date ON index_records(record_date);
```

### 字段说明

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 自增主键 |
| keyword | TEXT | NOT NULL | 关键词 |
| index_value | INTEGER | NOT NULL | 微信指数值 |
| change_percent | REAL | | 日环比百分比（如 15.5 表示 +15.5%） |
| trend | TEXT | | 趋势符号：↑（上涨）、↓（下跌）、→（持平） |
| category | TEXT | | 分类标签 |
| record_date | DATE | NOT NULL | 记录日期（YYYY-MM-DD） |
| note | TEXT | | 备注信息 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

## MCP 工具接口规范

### Tool 1: `brave_starr_add_records`

**功能**：批量添加指数记录

**输入参数 Schema**：

```json
{
  "type": "object",
  "properties": {
    "records": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "keyword": { "type": "string" },
          "index_value": { "type": "integer" },
          "change_percent": { "type": "number" },
          "trend": { "type": "string", "enum": ["↑", "↓", "→"] },
          "category": { "type": "string" },
          "record_date": { "type": "string", "format": "date" },
          "note": { "type": "string" }
        },
        "required": ["keyword", "index_value", "record_date"]
      }
    }
  },
  "required": ["records"]
}
```

**返回值**：

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "inserted_count": { "type": "integer" },
    "message": { "type": "string" }
  }
}
```

### Tool 2: `brave_starr_get_records`

**功能**：查询历史指数记录

**输入参数 Schema**：

```json
{
  "type": "object",
  "properties": {
    "keyword": { "type": "string", "description": "按关键词筛选" },
    "start_date": { "type": "string", "format": "date", "description": "起始日期" },
    "end_date": { "type": "string", "format": "date", "description": "结束日期" },
    "category": { "type": "string", "description": "按分类筛选" },
    "limit": { "type": "integer", "default": 100, "description": "返回条数限制" }
  }
}
```

**返回值**：

```json
{
  "type": "object",
  "properties": {
    "records": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "keyword": { "type": "string" },
          "index_value": { "type": "integer" },
          "change_percent": { "type": "number" },
          "trend": { "type": "string" },
          "category": { "type": "string" },
          "record_date": { "type": "string" },
          "note": { "type": "string" },
          "created_at": { "type": "string" }
        }
      }
    },
    "total": { "type": "integer" }
  }
}
```

## 错误处理

以下错误优先视为 **协议接入错误**，不是业务工具错误。

### 错误码

| 错误码 | 说明 |
|--------|------|
| INVALID_INPUT | 输入参数格式错误 |
| MISSING_REQUIRED | 缺少必填字段 |
| DB_ERROR | 数据库操作失败 |

### 常见 HTTP 错误

| HTTP 状态 | 常见消息 | 根因 | 处理方式 |
|---|---|---|---|
| 404 | `Not Found` | 错把 `/mcp/health` 当健康检查端点 | 使用 `GET /health` |
| 406 | `Client must accept both application/json and text/event-stream` | `Accept` 请求头不完整 | 使用 `Accept: application/json, text/event-stream` |
| 400 | `Bad Request: Missing session ID` | 未先完成 `initialize`，或后续请求未带 `mcp-session-id` | 先握手，再复用 `mcp-session-id` |
| 400 | `Parse error` | 请求体不是合法 JSON | 修正序列化后的请求体 |

### 错误返回格式

```json
{
  "success": false,
  "error_code": "INVALID_INPUT",
  "message": "record_date must be in YYYY-MM-DD format"
}
```

## 非功能需求

### 性能

- 单次批量写入支持最多 100 条记录
- 查询响应时间 < 100ms（1000 条记录内）

### 可靠性

- 健康检查接口可用于容器与代理探活
- 握手失败时返回明确的协议级错误信息
