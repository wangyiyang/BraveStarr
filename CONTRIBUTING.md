# Contributing to BraveStarr

感谢你关注 BraveStarr。

## 结论

- 所有开发都基于 `main` 之外的分支进行
- 依赖管理统一使用 `uv`
- 提交前至少运行 `uv run pytest`

## 本地开发

```bash
uv sync --locked
uv run pytest
uv run brave-starr --transport http
```

## 提交流程

1. 从 `main` 拉出功能分支
2. 保持改动聚焦，避免顺手修无关问题
3. 补充或更新测试、README、相关文档
4. 提交 Pull Request，并说明目的、方案、验证结果

## 代码约定

- Python 版本：`3.11+`
- 包管理：`uv`
- 代码风格：`uv run ruff format src tests`
- 静态检查：`uv run ruff check src tests`

## 文档约定

- 对外说明优先写清楚目的、背景、改动点、验证结果
- 如果变更了端点、环境变量、运行方式，请同步更新 `README.md`

## 许可证

本项目采用 `MIT` 许可证，具体见 `LICENSE`。
