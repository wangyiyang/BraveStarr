# BraveStarr 架构设计

## 概述

BraveStarr 采用简化的三层架构，通过 FastMCP 提供 **MCP Streamable HTTP** 服务，数据持久化于 SQLite。

## 系统架构

```text
┌─────────────┐     MCP      ┌─────────────┐
│  MCP Client │ ◄──────────► │  FastMCP    │
│ (HTTP/SSE)  │              │  (Python)   │
└─────────────┘              └──────┬──────┘
                                    │
                              ┌─────▼─────┐
                              │  SQLite   │
                              │  (数据层)  │
                              └───────────┘
```

## 组件说明

### MCP Client（客户端）

- 通过 `POST /mcp` 发起 `initialize`
- 从响应头保存 `mcp-session-id`
- 完成 `notifications/initialized` 后再调用工具

### FastMCP（服务层）

- MCP 协议服务端
- 提供 `brave_starr_add_records` 和 `brave_starr_get_records` 工具
- 负责输入验证、业务逻辑与查询编排
- 暴露 `GET /health` 健康检查

### SQLite（数据层）

- 文件数据库，无需额外部署
- 存储 `index_records` 表
- 支持索引优化查询性能

## 交互流程

### 握手流程

```text
1. Client -> POST /mcp : initialize
2. Server -> 返回 SSE 响应头与 mcp-session-id
3. Client -> POST /mcp : notifications/initialized
4. Client -> POST /mcp : tools/list / tools/call
```

### 写入流程

```text
1. 客户端整理微信指数数据
2. 调用 brave_starr_add_records
3. FastMCP 验证数据格式
4. 写入 SQLite
5. 返回新增数量与结果摘要
```

### 查询流程

```text
1. 客户端调用 brave_starr_get_records
2. FastMCP 构建查询条件
3. 从 SQLite 查询数据
4. 返回记录列表与总数
```

## 目录结构

```text
BraveStarr/
├── README.md
├── docs/
│   ├── spec.md
│   └── architecture.md
├── src/
│   └── brave_starr/
│       ├── __init__.py
│       ├── server.py
│       ├── models.py
│       └── database.py
├── data/
│   └── brave_starr.db
├── pyproject.toml
└── tests/
```

## 技术决策

### 为什么选择 FastMCP？

- 原生支持 MCP Tool 定义
- 对 Python 生态友好
- 能直接提供 Streamable HTTP 传输

### 为什么选择 SQLite？

- 零配置，无需独立数据库服务
- 文件存储，便于备份与迁移
- 性能足以支撑 MVP 体量

### 为什么选择 uv？

- 依赖解析快
- 配合 `pyproject.toml` 更一致
- 能避免 `requirements.txt` 与源码实现漂移

## 部署方式

### 本地开发

```bash
uv sync
uv run brave-starr --transport http
```

### MCP 接入地址

```text
http://<host>:8000/mcp
```

### 健康检查

```text
http://<host>:8000/health
```

## 扩展性

MVP 阶段保持简单，后续可扩展：

- 数据分析：集成 Pandas 进行趋势分析
- 数据源：支持自动抓取微信指数 API
- 鉴权：为 MCP HTTP 接口增加访问控制
