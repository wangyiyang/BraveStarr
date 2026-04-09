# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BraveStarr is a WeChat Index (微信指数) recording and query service based on FastMCP. It exposes MCP tools over Streamable HTTP and stores data in SQLite.

## Tech Stack

- **Python**: 3.11+
- **Package Manager**: uv
- **MCP Framework**: FastMCP
- **ORM**: SQLModel
- **Database**: SQLite

## Common Commands

```bash
# Install dependencies
uv sync

# Run the MCP server (Streamable HTTP)
uv run brave-starr --transport http

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

## Architecture

Three-layer architecture:

```text
┌─────────────┐     MCP      ┌─────────────┐
│  MCP Client │ ◄──────────► │  FastMCP    │
│ (HTTP/SSE)  │              │  (Python)   │
└─────────────┘              └──────┬──────┘
                                    │
                              ┌─────▼─────┐
                              │  SQLite   │
                              │ (SQLModel)│
                              └───────────┘
```

### Key Components

- **src/brave_starr/server.py**: FastMCP server entry point, registers MCP tools
- **src/brave_starr/models.py**: SQLModel schema
- **src/brave_starr/database.py**: DB connection and session management
- **data/brave_starr.db**: SQLite database file

### MCP Tools

1. **brave_starr_add_records**: Batch insert index records
2. **brave_starr_get_records**: Query historical records with filters

## Directory Structure

```text
BraveStarr/
├── src/brave_starr/
│   ├── __init__.py
│   ├── server.py
│   ├── models.py
│   └── database.py
├── data/
├── docs/
├── tests/
├── pyproject.toml
└── README.md
```

## MCP Configuration

Public MCP endpoint:

```text
http://localhost:8000/mcp
```

Handshake requirements:

1. Send `initialize`
2. Save `mcp-session-id` from response headers
3. Send `notifications/initialized`
4. Include `mcp-session-id` and `mcp-protocol-version` on subsequent requests

## Development Workflow

1. Model changes: Edit `src/brave_starr/models.py`
2. New MCP tools: Register in `src/brave_starr/server.py` with `@mcp.tool()`
3. Database queries: Use SQLModel sessions in `src/brave_starr/database.py`
4. Tests: Place in `tests/`

## References

- Detailed specs: `docs/spec.md`
- Architecture: `docs/architecture.md`
