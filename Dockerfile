# BraveStarr FastMCP 服务 Docker 镜像
FROM python:3.11-slim

# 安装 uv
RUN pip install --no-cache-dir uv

# 设置工作目录
WORKDIR /app

# 复制项目文件（使用 uv.lock 锁定 FastMCP 版本，避免镜像构建时漂移）
COPY pyproject.toml uv.lock .python-version README.md ./
COPY src/ ./src/

# 同步依赖并安装当前项目
RUN uv sync --locked --no-dev

# 创建数据目录
RUN mkdir -p /app/data

# 暴露端口（MCP Streamable HTTP）
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV DATABASE_PATH=/app/data/brave_starr.db

# 启动命令（HTTP 传输）
CMD ["uv", "run", "brave-starr", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
