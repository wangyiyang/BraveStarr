# 🦅 BraveStarr

BraveStarr 是一个基于 `FastMCP`、`SQLModel` 与 `SQLite` 的微信指数记录服务，对外只提供 **MCP Streamable HTTP** 接入。

## 结论

- 正式 MCP 端点：`http://localhost:8000/mcp`
- 健康检查端点：`http://localhost:8000/health`
- 当前公开工具：`brave_starr_add_records`、`brave_starr_get_records`
- 旧版 `web_server.py` 仪表盘路径已移除，仓库仅保留 MCP 服务实现

## 特性

- 基于 `FastMCP` 提供标准 MCP Streamable HTTP 接口
- 使用 SQLite 持久化，默认零额外基础设施
- 支持批量写入与按条件查询微信指数记录
- 兼容容器部署与本地开发，数据库路径可通过环境变量覆写

## 快速开始

### 1. 安装依赖

```bash
uv sync --locked
```

### 2. 启动服务

```bash
uv run brave-starr --transport http --host 0.0.0.0 --port 8000
```

或直接使用脚本：

```bash
./start.sh
```

如果希望通过 Docker 运行：

```bash
make docker-restart
make docker-health
```

### 3. 验证服务

```bash
curl http://localhost:8000/health
```

预期返回：

```json
{"status":"healthy","service":"brave-starr"}
```

## 配置

### 数据库路径

- 推荐变量：`BRAVE_STARR_DB_PATH`
- 兼容变量：`DATABASE_PATH`
- 默认路径：`./data/brave_starr.db`

示例：

```bash
export BRAVE_STARR_DB_PATH=/tmp/brave_starr.db
uv run brave-starr --transport http
```

## MCP Streamable HTTP 握手

`/mcp` 不是普通 JSON API，必须遵循 MCP Streamable HTTP 握手。

### 请求头要求

所有 `POST /mcp` 请求都必须带：

```http
Content-Type: application/json
Accept: application/json, text/event-stream
```

初始化后的后续请求还必须带：

```http
mcp-session-id: <initialize 响应头返回的值>
mcp-protocol-version: 2025-11-25
```

### 正确时序

1. `POST /mcp` 发送 `initialize`
2. 从响应头读取 `mcp-session-id`
3. `POST /mcp` 发送 `notifications/initialized`
4. 再调用 `tools/list`、`tools/call`

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

## 可用工具

### `brave_starr_add_records`

批量写入微信指数记录。

- 必填字段：`keyword`、`index_value`、`record_date`
- 可选字段：`change_percent`、`trend`、`category`、`note`
- 单次最多 100 条
- 相同 `keyword + record_date` 使用覆盖策略

### `brave_starr_get_records`

按关键词、日期范围、分类查询历史记录。

- 可选参数：`keyword`、`start_date`、`end_date`、`category`
- `limit` 默认 `100`
- 结果按 `record_date DESC` 返回

## 常见错误排查

| 现象 | 根因 | 正确做法 |
|---|---|---|
| `GET /mcp/health -> 404` | 健康检查路径写错 | 改用 `GET /health` |
| `POST /mcp -> 406 Not Acceptable` | `Accept` 头不完整 | 使用 `Accept: application/json, text/event-stream` |
| `POST /mcp -> 400 Missing session ID` | 未先完成 `initialize` | 先初始化，再回传 `mcp-session-id` |
| `POST /mcp -> 400 Parse error` | 请求体不是合法 JSON | 检查 JSON 序列化结果 |
| 工具名找不到 | 使用了旧文档里的工具名 | 改用 `brave_starr_add_records` / `brave_starr_get_records` |

## 开发

```bash
uv sync --locked
uv run pytest
uv run ruff check src tests
uv run brave-starr --transport http
```

可选 Makefile 命令：

```bash
make help
make install
make test
make lint
make run
```

## 仓库结构

```text
BraveStarr/
├── src/brave_starr/
│   ├── server.py
│   ├── models.py
│   └── database.py
├── docs/
├── tests/
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── pyproject.toml
└── README.md
```

## 开源协作说明

- 许可证见 `LICENSE`，当前采用 `MIT`
- 贡献流程见 `CONTRIBUTING.md`
- 社区行为准则见 `CODE_OF_CONDUCT.md`
- 安全漏洞披露流程见 `SECURITY.md`
