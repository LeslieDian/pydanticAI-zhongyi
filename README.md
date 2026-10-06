# 中医药 AI Agent · pydanticAI-zhongyi

> 基于 PydanticAI 的中医辨证论治助手（医师辅助工具）。
> **不是患者自诊工具，不出具处方，所有结论须经执业中医师确认。**

## ⚠️ 安全声明（请先读）

- **仓库中不含任何 API 密钥**。如果你看到任何 `sk-` 开头的字符串，请立刻发 issue 告知。
- **本地 `.env` 文件被 `.gitignore` 排除**，不会被推送。如果你发现推送历史中出现了密钥，请立刻转措施：
  1. 到 MiniMax 后台 **rotate key**
  2. 从仓库运行历史清理（git filter-repo）或删仓重推
- **本仓库启用了 pre-commit hook**（`.git/hooks/pre-commit`），如果检测到待提交文件含 `sk-` 前缀，会拒绝提交。

---

## 项目状态

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org)
[![PydanticAI](https://img.shields.io/badge/pydantic--ai-~2.33-green)](https://ai.pydantic.dev)
[![Tests](https://img.shields.io/badge/tests-39%2F39-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

本仓库实施了 [TCM-Agent Kickoff Manual v1.1](docs/notes/deploy-to-github.md) 的全部要求。

| 阶段 | 状态 |
|---|---|
| Phase 0.1 依赖锁定 | ✅ 完成 |
| Phase 0.3 Schema 定稿 | ✅ 完成（含 v1.1 增量字段） |
| Phase 0.4 红旗规则 | ✅ 规则已写，待中医师签字 |
| Phase 0.6 数据源盘点 | ✅ 完成（[TCM 数据源调研](docs/notes/tcm-data-sources.md)） |
| Phase 0.2 模型能力验证 | ⏳ 待执行（需 API key） |
| Phase 0.5 评测集启动 | ⏳ 待启动（需中医师参与） |
| Phase 1-4 | ⏳ 未启动 |

## 快速开始

```bash
# 1. 安装依赖
pip install -e ".[dev,evals]"

# 2. 配置环境变量（先 cp .env.example .env，填 API key）
cp .env.example .env
# 编辑 .env，填入 MINIMAX_API_KEY

# 3. 跑单元测试（需设 PYTHONPATH）
set PYTHONPATH=%CD%\src
pytest tests/ -v
# 预期：39/39 通过

# 4. Phase 0.2 模型能力验证
set MINIMAX_API_KEY=...
python -m experiments.phase0_model_smoke
```

## 五层架构 + 九环节

```
L0  输入       四诊原始：症状/病史/舌象/脉象
L1  分诊       确定性规则（红旗一票否决）+ 轻量 LLM（仅可上调）
L2  规范化     同义词词典 → 向量近义 → 否定检测（LLM 不参与）
L3-A 检索前   三路召回（稠密/关键词/图谱）→ RRF → Rerank + 拒答阀门
L4  主 Agent   1 个 Agent → 嵌套 Diagnosis + 5 验证器
L3-B 检索后   图谱路径校验 + 出处回填（属于验证器）
L5  核验       并行 2 项（v1.1 合并）→ 代码计算 confidence_score
L6  安全阀门   纯代码，不经 LLM；反畏/妊娠/毒性/药典 → 命中即拒
L7  输出+审计    结构化处方 + 证据链 + 缺失声明 + 免责声明 + 落库
```

详细说明：[docs/notes/architecture.md](docs/notes/architecture.md)

## 目录结构

```
pydanticAI-zhongyi/
├─ pyproject.toml                # 版本锁定（手册 §0）
├─ .env.example                  # 环境变量模板（无密钥）
├─ .gitignore                    # 包含 .env
├─ LICENSE                       # MIT
├─ README.md                     # 本文件
├─ conftest.py                   # pytest 入口
├─ .git/hooks/pre-commit         # 防止密钥误提交
├─ src/tcm_agent/                # 主代码
│  ├─ config.py              # 常量、阈值、毒性档位系数
│  ├─ schemas.py             # 14 个 Pydantic 模型
│  ├─ models.py              # 模型工厂（MiniMax / DeepSeek）
│  ├─ triage.py              # S1 分诊（红旗规则）
│  ├─ normalize.py           # S2 术语规范化
│  ├─ pipeline.py            # 主流程编排（原生 async）
│  ├─ retrieve/              # 检索层（dense/lexical/graph/fusion/rerank）
│  ├─ agents/                # 主 Agent + 5 验证器
│  ├─ safety/                # 安全闸门 + 规则 YAML
│  └─ knowledge/             # 基础方剂量表
├─ tests/                        # 39 个单元测试
├─ experiments/                  # Phase 0 烟雾测试脚本 + 运行日志
├─ evals/                        # 评测体系（evaluators + 5 demo）
├─ graph/schema.cypher           # Neo4j DDL（麻黄汤示例）
└─ docs/notes/                   # 架构/决策/版本/数据源/部署说明
```

## 关键设计决策

详见 [docs/notes/decision-rationale.md](docs/notes/decision-rationale.md)。最重要的 5 条：

1. **不拆 4 个 agent**：辨证→立法→选方→加减是强依赖链，拆 agent 会丢上下文、累积误差、成本×4。
2. **不用自我反思**：ACL 2025 证实 GPT-4o 在决策任务上 76.6% 把正确答案改错。用 `@output_validator` + `ModelRetry` 传硬事实更靠谱。
3. **不上 pydantic-graph**：顶点图性太弱，`if/else` + `asyncio.gather` 更简单。升级触发：需要挂起数小时等医师审方、或分支数 ≥5。
4. **不用 DeepSeek Harness**：它是 TypeScript agent 运行时平台，适合搭建一个 agent IDE，不适合你这个“构建一个领域 agent 功能”。
5. **分诊 = 确定性代码**：LLM 只能“上调”不能“下调”。红旗命中即拒，不交给模型“解释一下”。

## 中医药数据源建议

详见 [docs/notes/tcm-data-sources.md](docs/notes/tcm-data-sources.md)。核心推荐：

- **PanckooAI/TCM_Datasets**：45 本十四五规划教材 markdown（首选）
- **TR2335/ZY-TCM-Knowledge-Graph**：7ed3构化安全规则 CSV（补你的 rules.yaml）
- **TCM-Ladder**（NeurIPS 2025）：TCM LLM 评测套餐（Phase 4 用）

## 安全声明（重复提示）

本项目是“**医师辅助工具**”，不是患者自诊 APP。任何 AI 推理结论仅供执业中医师参考，不构成处方。

**红旗症状**（命中即拒诊）：神昏、剧烈胸痛、大出血、中风先兆、呼吸困难、高热不退等急症。

**安全规则**（[src/tcm_agent/safety/rules.yaml](src/tcm_agent/safety/rules.yaml)）：
- 十八反（甘草反甘遂/大戚/海藻/英花等）
- 十九畏
- 妊娠禁忌（禁用 + 慎用两级）
- 毒性药材上限（附子、川乌、草乌、马钱子、细辛、半夏等）
- 药典常用量区间

**法规合规**：
- 不直接出具处方给药房
- 所有输出须经医师确认才可用于临床
- 医案入库前必须脱敏（姓名、身份证、住址、联系方式、精确日期）

## 证书

MIT License —— 仅供学习和研究使用。

## 更新日志

- **2026-10-06** v0.2.0 · 推送完成 + pre-commit hook + 安全声明
- **2026-10-06** v0.1.0 · 项目初始化（34 个单元测试）
- 手册 v1.1（2026-10-05）已实施到代码
