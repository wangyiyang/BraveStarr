#!/bin/bash
set -euo pipefail

echo "🦅 BraveStarr MCP Server"
echo "======================="
echo "📦 同步依赖..."
uv sync --locked

echo ""
echo "🚀 启动 MCP Streamable HTTP 服务..."
echo "   MCP Endpoint: http://localhost:8000/mcp"
echo "   Health Check: http://localhost:8000/health"
echo ""

exec uv run brave-starr --transport http --host 0.0.0.0 --port 8000
