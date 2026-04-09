# Repository Guidelines

## Project Structure & Module Organization

BraveStarr is a Python 3.11+ FastMCP service. Core application code lives in `src/brave_starr/`:

- `server.py` — MCP entrypoint, tool registration, and HTTP transport startup
- `database.py` — SQLite engine, session handling, and database path resolution
- `models.py` — SQLModel data models and response schemas

Tests live in `tests/` and mirror the runtime modules (`test_server.py`, `test_database.py`, `test_models.py`). Reference docs live in `docs/` (`architecture.md`, `spec.md`). Root scripts such as `start.sh`, `run_mcp.sh`, `Makefile`, `Dockerfile`, and `docker-compose.yml` support local and container workflows.

## Build, Test, and Development Commands

Use `uv` for dependency management.

- `uv sync --locked` — install locked dependencies
- `uv run brave-starr --transport http --host 0.0.0.0 --port 8000` — run locally
- `./start.sh` — sync dependencies and start the MCP HTTP service
- `uv run pytest` — run the full test suite
- `uv run ruff check src tests` — run lint checks
- `uv run ruff format src tests` — format source and test files
- `make docker-restart && make docker-health` — rebuild the Docker service and verify health

## Coding Style & Naming Conventions

Follow existing Python style: 4-space indentation, type hints on public functions, and focused modules. Keep implementations simple and avoid duplicate logic. Use `snake_case` for functions, variables, and test names; use `PascalCase` for SQLModel classes. Prefer small functions over large monolithic handlers. If a file approaches 500 lines, split responsibilities.

## Testing Guidelines

Pytest is the standard test framework. Add or update tests for every behavior change, especially around MCP routing, tool behavior, and database configuration. Name tests `test_<behavior>`. Run targeted tests first, for example: `uv run pytest tests/test_server.py`.

## Commit & Pull Request Guidelines

Git history uses Conventional Commit style, e.g. `feat: add BraveStarr MCP HTTP service` and `chore: initialize repository`. Continue using prefixes such as `feat:`, `fix:`, `chore:`, and `docs:`. Open PRs from a branch off `main`; do not commit directly to `main`. PRs should include purpose, key changes, verification results, and linked issues when applicable.

## Security & Configuration Tips

Do not commit local databases, secrets, or `.env` files. Prefer `BRAVE_STARR_DB_PATH` to override the default SQLite location; `DATABASE_PATH` remains for backward compatibility.
