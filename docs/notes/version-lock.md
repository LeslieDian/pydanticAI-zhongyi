# 版本锁定与已知坑

## 锁定值

| 组件 | 版本 | 说明 |
|---|---|---|
| Python | >= 3.12 | pydantic-graph 2.x 要求 |
| pydantic-ai | ~= 2.33 | v2 已稳定 2026-06-23 |
| pydantic-graph | == 同版本线 | 精确互锁，不能单独升 |

## 两个必须知道的事实

### 1. pydantic-ai 与 pydantic-graph 共用版本线

`pydantic-ai-slim` 精确 pin `pydantic-graph==`，升一个必升另一个。

### 2. pydantic-graph 2.x 删除了整个 persistence 包

- `FileStatePersistence` / `SimpleStatePersistence` / `BaseStatePersistence` 全没了
- `run(persistence=...)` 不存在
- `mermaid` 模块也删了

**持久化替代方案**：
- Pydantic AI Harness 的 `StepPersistence`
- 外包给 Temporal / DBOS / Prefect / Restate

## BOM 陷阱

pydantic-ai 在 import 时会读 `pyproject.toml` 的 `[tool.logfire]` 段。如果文件带 BOM（`\xef\xbb\xbf`），tomllib 解析失败，导致整个 pydantic_ai 包无法 import。

**解决**：所有 Python 源码和配置文件必须 UTF-8 无 BOM 保存。

## DeepSeek API

文档 base_url：`https://api.deepseek.com`（不是 anthropic 那个）。

模型名变化：
- `deepseek-v4-flash` 已弃用，统一走 `deepseek-flash`
- `deepseek-v4-pro` 是当前主力

## OpenAIProvider profile 坑

OpenAIProvider 会按 OpenAI 模型名推断 profile。如果用 MiniMax（不是 OpenAI 模型），结构化输出/工具调用可能异常。

**解决**：显式传 `profile=...`，或者用 MiniMax 的内置 provider（如果 PydanticAI 支持）。
