#!/bin/bash
set -euo pipefail

# Docker 容器测试脚本

echo "=== 启动 BraveStarr 容器 ==="
docker compose up -d

echo ""
echo "=== 等待服务就绪 ==="
sleep 3

echo ""
echo "=== 检查容器状态 ==="
docker compose ps

echo ""
echo "=== 查看容器日志 ==="
docker compose logs --tail=20

echo ""
echo "=== 检查数据库文件 ==="
docker compose exec -T brave-starr ls -la /app/data/

echo ""
echo "=== 容器信息 ==="
echo "数据卷挂载: brave-starr-data -> /app/data"
echo "如需查看 MCP 服务，需要交互式运行:"
echo "  docker run -it --rm -v brave-starr-data:/app/data brave-starr:latest"
