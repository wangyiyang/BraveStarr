# 🦅 BraveStarr

BraveStarr 是一个基于 `FastMCP` 与 `SQLite` 的微信指数记录服务，对外只提供 **MCP Streamable HTTP** 接入。

## 结论先说

- 正式 MCP 端点：`http://localhost:8000/mcp`
- 健康检查端点：`http://localhost:8000/health`
- 不存在的端点：`/mcp/health`
- 当前真实工具：`brave_starr_add_records`、`brave_starr_get_records`

## 快速开始

### 1. 安装依赖

```bash
cd ~/Documents/Github/BraveStarr
uv sync --locked
```

### 2. 启动服务

```bash
uv run brave-starr --transport http --host 0.0.0.0 --port 8000
```

也可以直接执行：

```bash
./start.sh
```

如果你更希望走 Docker：

```bash
make docker-restart
make docker-health
```

### 3. 验证服务可用

```bash
curl http://localhost:8000/health
```

预期返回：

```json
{"status":"healthy","service":"brave-starr"}
```

## MCP Streamable HTTP 握手

`/mcp` 不是普通 JSON API，必须遵循 MCP Streamable HTTP 握手。

### 请求头要求

所有 `POST /mcp` 请求都必须带：

```http
Content-Type: application/json
Accept: application/json, text/event-stream
```

初始化完成后的后续请求还必须带：

```http
mcp-session-id: <initialize 响应头返回的值>
mcp-protocol-version: 2025-11-25
```

### 正确时序

1. `POST /mcp` 发送 `initialize`
2. 从响应头读取 `mcp-session-id`
3. `POST /mcp` 发送 `notifications/initialized`
4. 后续再调用 `tools/list`、`tools/call`

### 初始化示例

```bash
curl -i http://localhost:8000/mcp \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  --data '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {},
      "clientInfo": {
        "name": "debug-client",
        "version": "0.1.0"
      }
    }
  }'
```

### 初始化后发送 `initialized`

```bash
curl -i http://localhost:8000/mcp \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'mcp-session-id: <SESSION_ID>' \
  -H 'mcp-protocol-version: 2025-11-25' \
  --data '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
    "params": {}
  }'
```

### 查看工具列表示例

```bash
curl -i http://localhost:8000/mcp \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'mcp-session-id: <SESSION_ID>' \
  -H 'mcp-protocol-version: 2025-11-25' \
  --data '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

## 可用工具

### `brave_starr_add_records`

批量写入微信指数记录。

- 输入字段：`keyword`、`index_value`、`record_date` 必填
- 支持字段：`change_percent`、`trend`、`category`、`note`
- 单次最多 100 条
- 相同 `keyword + record_date` 使用覆盖策略

示例参数：

```json
{
  "records": [
    {
      "keyword": "Claude",
      "index_value": 1234567,
      "change_percent": 15.5,
      "trend": "↑",
      "category": "AI编程",
      "record_date": "2026-04-09",
      "note": "样例数据"
    }
  ]
}
```

### `brave_starr_get_records`

按关键词、日期范围、分类查询历史记录。

- 可选参数：`keyword`、`start_date`、`end_date`、`category`
- `limit` 默认 `100`
- 结果按 `record_date DESC` 返回

示例参数：

```json
{
  "keyword": "Claude",
  "start_date": "2026-04-01",
  "end_date": "2026-04-09",
  "limit": 50
}
```

## 常见错误排查

| 现象 | 根因 | 正确做法 |
|---|---|---|
| `GET /mcp/health -> 404` | 健康检查路径写错 | 改用 `GET /health` |
| `POST /mcp -> 406 Not Acceptable` | `Accept` 头不完整 | 使用 `Accept: application/json, text/event-stream` |
| `POST /mcp -> 400 Missing session ID` | 未先完成 `initialize` | 先初始化，再回传 `mcp-session-id` |
| `POST /mcp -> 400 Parse error` | 请求体不是合法 JSON | 检查 JSON 序列化结果 |
| 工具名找不到 | 使用了旧文档里的工具名 | 改用 `brave_starr_add_records` / `brave_starr_get_records` |

## 项目结构

```text
BraveStarr/
├── src/brave_starr/
│   ├── server.py
│   ├── models.py
│   └── database.py
├── docs/
│   ├── spec.md
│   └── architecture.md
├── tests/
├── pyproject.toml
└── README.md
```

## 开发命令

```bash
uv sync --locked
uv run pytest
uv run brave-starr --transport http
```

## Makefile 快捷命令

```bash
make help
make docker-build
make docker-up
make docker-restart
make docker-logs
make docker-health
make docker-down
```
