SHELL := /bin/bash

COMPOSE := docker compose
SERVICE := brave-starr
HEALTH_URL := http://localhost:8000/health

.PHONY: help install test lint format run \
	docker-build docker-up docker-down docker-restart docker-logs docker-ps \
	docker-health docker-shell docker-clean

help:
	@echo "可用命令:"
	@echo "  make install         - 同步 Python 依赖"
	@echo "  make test            - 运行测试"
	@echo "  make lint            - 运行 Ruff 检查"
	@echo "  make format          - 运行 Ruff 格式化"
	@echo "  make run             - 本地启动 MCP HTTP 服务"
	@echo "  make docker-build    - 构建 Docker 镜像"
	@echo "  make docker-up       - 启动 Docker 服务"
	@echo "  make docker-down     - 停止 Docker 服务"
	@echo "  make docker-restart  - 重建并重启 Docker 服务"
	@echo "  make docker-logs     - 查看容器日志"
	@echo "  make docker-ps       - 查看容器状态"
	@echo "  make docker-health   - 检查健康状态"
	@echo "  make docker-shell    - 进入容器 Shell"
	@echo "  make docker-clean    - 停止服务并删除未使用镜像"

install:
	uv sync --locked

test:
	uv run pytest

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

run:
	uv run brave-starr --transport http --host 0.0.0.0 --port 8000

docker-build:
	$(COMPOSE) build

docker-up:
	$(COMPOSE) up -d

docker-down:
	$(COMPOSE) down

docker-restart:
	$(COMPOSE) up -d --build --force-recreate

docker-logs:
	$(COMPOSE) logs -f --tail=100

docker-ps:
	$(COMPOSE) ps

docker-health:
	@echo "检查 $(HEALTH_URL)"
	@curl -fsS $(HEALTH_URL) && echo

docker-shell:
	$(COMPOSE) exec $(SERVICE) /bin/bash

docker-clean:
	$(COMPOSE) down --remove-orphans
	docker image prune -f
