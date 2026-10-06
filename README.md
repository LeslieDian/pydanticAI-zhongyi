# 中医药 AI Agent - pydanticAI-zhongyi

> 基于 PydanticAI 的中医辨证论治助手（医师辅助工具）。
> **不是患者自诊工具，不出具处方，所有结论须经执业医师确认。**

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org)
[![PydanticAI](https://img.shields.io/badge/pydantic--ai-~2.33-green)](https://ai.pydantic.dev)
[![Tests](https://img.shields.io/badge/tests-34%2F34-brightgreen)]()

## 文档索引

| 文件 | 内容 |
|---|---|
| [README.md](README.md) | 本文件：项目总览 + 流程图 + Phase 0-4 步骤 + 实验记录 |
| [docs/notes/architecture.md](docs/notes/architecture.md) | 五层架构与九环节详解 |
| [docs/notes/version-lock.md](docs/notes/version-lock.md) | 版本锁定与 pydantic-graph 2.x 持久化删除的事实 |
| [docs/notes/decision-rationale.md](docs/notes/decision-rationale.md) | 关键 ADR 决策依据（含 DeepSeek Harness 弃选理由） |
| [experiments/runs/](experiments/runs/) | 实验运行日志（测试结果、smoke test 输出等） |

> **配套外部文档**（不在仓库内）：
> - 选型报告 `TCM-Agent-Stack-Report.md`
> - 架构蓝图 `TCM-Agent-Project-Blueprint.md`
> - 开工手册 v1.1 `TCM-Agent-Kickoff-Manual.md`

---

## 项目定位

**医师辅助工具**，不是患者自诊 APP。任何 AI 推理结论仅供执业医师参考，不构成处方。

三层合规防护（顺序不可颠倒）：

1. **分诊拒诊**（主链之前）：红旗症状必须确定性拦截，不交给 LLM
2. **验证回路**（生成之中）：5 个验证器带硬事实纠错
3. **安全闸门**（输出之前）：十八反十九畏 / 妊娠禁忌 / 毒性剂量 / 药典区间，一票否决

---

## 五层架构 + 九环节

```
L0 输入         四诊原始：症状/病史/舌象/脉象
L1 分诊         确定性规则（红旗一票否决）+ 轻量 LLM（仅可上调）
L2 规范化       同义词词典 → 向量近义 → 否定检测（LLM 不参与）
L3-A 检索前     三路召回（稠密/关键词/图谱）→ RRF → Rerank + 拒答闸门
L4 主 Agent     1 个 Agent → 嵌套 Diagnosis + 5 验证器 + ModelRetry
L3-B 检索后     图谱路径校验 + 出处回填（属于验证器）
L5 核验         并行 2 项（v1.1 合并）→ 代码计算 confidence_score
L6 安全闸门     纯代码，不经 LLM；反畏/妊娠/毒性/药典 → 命中即拒
L7 输出+审计    结构化处方 + 证据链 + 缺失声明 + 免责声明 + 落库
```

详细说明：[docs/notes/architecture.md](docs/notes/architecture.md)

---

## 快速开始

### 1. 安装依赖

```bash
pip install -e ".[dev,evals]"
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 MINIMAX_API_KEY（或 DEEPSEEK_API_KEY）
```

### 3. 跑单元测试

```bash
set PYTHONPATH=%CD%\src
pytest tests/ -v
```

**当前状态：34/34 通过**（详见 [实验记录](#实验记录)）

### 4. Phase 0 模型能力验证

```bash
set MINIMAX_API_KEY=...
python -m experiments.phase0_model_smoke
# 预期：20/20 通过 → 模型能力达标，进入 Phase 1
```

---

## 目录结构

```
pydanticAI-zhongyi/
+- pyproject.toml                # 版本锁定（手册 0）
+- .env.example                  # 环境变量模板
+- README.md                     # 本文件
+- src/tcm_agent/
|  +- config.py                  # 常量、阈值、毒性档位系数
|  +- schemas.py                 # 所有 Pydantic 模型（单一事实源）
|  +- models.py                  # 模型工厂（MiniMax / DeepSeek）
|  +- triage.py                  # S1 分诊（红旗规则）
|  +- normalize.py               # S2 术语规范化
|  +- pipeline.py                # 主流程编排（原生 async，无图）
|  +- retrieve/
|  |  +- dense.py                # pgvector 稠密检索
|  |  +- lexical.py              # pg_jieba + tsvector 关键词
|  |  +- graph.py                # Neo4j 多跳查询
|  |  +- fusion.py               # RRF 融合
|  |  +- rerank.py               # BGE-reranker-v2-m3
|  +- agents/
|  |  +- diagnosis.py            # 主 Agent 工厂
|  |  +- verifiers.py            # 5 个验证器（V1-V5）
|  +- safety/
|  |  +- rules.yaml              # 十八反/十九畏/妊娠/毒性/药典
|  |  +- redflags.yaml           # 红旗词表
|  |  +- gate.py                 # S7 安全闸门
|  |  +- dose.py                 # 剂量计算（按毒性三级分级）
|  +- knowledge/
|     +- dosage_table.py         # 基础方剂量表
+- tests/                        # 单元测试（34 个全过）
+- experiments/
|  +- phase0_model_smoke.py      # Phase 0.2 模型能力验证
|  +- runs/                      # 实验运行日志
+- data/                         # 教材/药典/医案/索引（本地缓存）
+- graph/
|  +- schema.cypher             # Neo4j DDL（Phase 3）
+- docs/notes/                   # 架构/决策/版本说明
```

---

## Phase 0-4 实施步骤

每个 Phase 都有明确的 DoD（完成标准），来源于 `TCM-Agent-Kickoff-Manual.md`。

### Phase 0 - 开工前置（1-2 周）必须先做

| # | 任务 | DoD | 当前状态 |
|---|---|---|---|
| 0.1 | 依赖锁定 | pyproject.toml 固定版本 | 已完成 |
| 0.2 | **模型能力验证** | MiniMax 跑 20 次，每次 type(result.output) is Diagnosis | 待执行（需 API key） |
| 0.3 | Schema 定稿 | schemas.py 评审通过 | 已完成（含 v1.1 字段） |
| 0.4 | 红旗规则表 v0 | 中医师签字确认 | 规则已写，待签字 |
| 0.5 | **评测集启动** | 联系 1-2 位中医师 | 待启动 |
| 0.6 | 数据源盘点 | 教材/药典/条文 版权与格式确认 | 待启动 |

**0.2 不过，后面全部白搭** —— 国产模型能否稳定输出嵌套 schema 是第一个未知数。

### Phase 1 - 主链打通（2-3 周）

- [ ] 术语词典 v1（>=500 条同义词）：当前 21 条起步
- [ ] pgvector 接入 + 教材分块入库
- [ ] 主 Agent 跑通嵌套 Diagnosis
- [ ] 5 个验证器（含 V5）人为构造违规案例拦截测试
- [ ] 剂量计算模块完整测试
- [ ] 端到端骨架 pipeline.py 跑通假医案

### Phase 2 - 安全与分诊（1-2 周）

- [ ] 分诊规则引擎 + 话术：30 个红旗样本漏检率 0
- [ ] 安全闸门：构造 50 个违规处方拦截率 100%
- [ ] 毒性分级剂量表：含大毒药材处方必须 review_required=True
- [ ] V5 角色校验：构造 3 类反例拦截率 100%
- [ ] 审计落库
- [ ] 免责声明与合规文案（法务确认）

### Phase 3 - 检索增强（2-3 周）

- [ ] Neo4j 小图谱（200 证候 / 200 方剂）
- [ ] 三路混合 + RRF + rerank
- [ ] 拒答阈值标定（正样本 P25 + 负样本误纳率 <= 10%）
- [ ] V1 分级核验上线
- [ ] 相似医案召回 + 注入 prompt

### Phase 4 - 评测与收口（2 周+）

- [ ] 评测集完成（>=50 标注医案）
- [ ] 全量回归跑通
- [ ] 错误分析与迭代
- [ ] 上线前合规文书

---

## 实验记录

### 实验 #1 - 单元测试套件（2026-10-06）

**目标**：验证核心逻辑正确性

**命令**：`pytest tests/ -v`

**结果**：

| 测试文件 | 用例数 | 通过 |
|---|---|---|
| test_dose.py | 5 | 5/5 |
| test_normalize.py | 4 | 4/4 |
| test_safety.py | 9 | 9/9 |
| test_schemas.py | 5 | 5/5 |
| test_triage.py | 4 | 4/4 |
| test_verifiers.py | 7 | 7/7 |
| **合计** | **34** | **34/34 通过** |

**覆盖的核心能力**：
- V1-V5 验证器全部正确触发 ModelRetry 或放行
- 大毒药材（附子）剂量锁定 + review_required=True
- 矿物类白名单（生石膏）君药大剂量不误报
- 十八反 / 十九畏 / 妊娠禁忌 / 毒性剂量 / 药典区间全部命中
- 红旗词规则匹配 + LLM-only-up 语义

**已知遗留问题**：
1. 整串"畏寒发热 3 天"无法被词典整串匹配（Phase 1 加 jieba 分词解决）
2. pydantic-ai 在 import 时读 [tool.logfire] 段，要求 pyproject.toml 无 BOM
3. pydantic-graph 2.x 已删除持久化（[docs/notes/version-lock.md](docs/notes/version-lock.md)）

**详细日志**：[experiments/runs/test_run.log](experiments/runs/test_run.log)

---

### 实验 #2 - Phase 0.2 模型能力验证（待执行）

**目标**：用 MiniMax 跑 20 次最小 Diagnosis schema，断言 type(result.output) is Diagnosis

**前置**：.env 填入 MINIMAX_API_KEY

**命令**：`python -m experiments.phase0_model_smoke`

**DoD**：
- >=18/20 通过 → 模型能力达标，进入 Phase 1
- <18/20 通过 → 调整 prompt / 换 profile / 换模型

**结果**：待执行

---

## 关键设计决策

### 为什么是 PydanticAI 而不是 DeepSeek Harness？

| 维度 | PydanticAI | DeepSeek Harness |
|---|---|---|
| 定位 | Python agent **开发框架** | TypeScript agent **运行时平台**（类似 Claude Code 内核） |
| 结构化输出 | **核心特性**（output_type + 自动重试） | 非核心，需手写解析 |
| 验证回路 | **声明式**（@output_validator + ModelRetry） | 需手写事件监听 + 重试逻辑 |
| 多模型切换 | 改一行 model= | 改 provider + 适配 |
| 语言 | Python（与本项目 FastAPI / pgvector / Neo4j 一致） | TypeScript/Node |

**结论**：你的项目是"构建一个特定领域的 agent **功能**"，不是"构建一个 agent **平台**"。**选 PydanticAI**。

详细对比：[docs/notes/decision-rationale.md](docs/notes/decision-rationale.md)

---

### 为什么不拆 4 个 Agent？

辨证 → 立法 → 选方 → 加减化裁 是**强依赖链**，不是并行。拆成 4 个 agent 的代价：

1. 上下文在传递中被压缩（选方看不到舌脉细节）
2. 误差累积且不可回溯
3. 成本和延迟 ×4

**正解**：1 个 Agent 一次调用输出嵌套 Diagnosis，依赖关系由 schema 自身表达。

---

### 为什么不用自我反思？

ACL 2025 主会论文实测：无条件"让模型再想想"会让准确率下降 2%-21%，GPT-4o 在决策任务上 76.6% 的概率把正确答案改错。

**正解**：用 @output_validator + ModelRetry，反馈里带的是图谱路径、药典数值、规则 id——**模型无法反驳的客观事实**。

---

## 安全声明

本项目是**医师辅助工具**，不是患者自诊 APP。任何 AI 推理结论仅供执业医师参考，不构成处方。

**红旗症状**（命中即拒诊）：神昏、剧烈胸痛、大出血、中风先兆、呼吸困难、高热不退等急症。

**安全规则**（[src/tcm_agent/safety/rules.yaml](src/tcm_agent/safety/rules.yaml)）：
- 十八反（甘草反甘遂/大戟/海藻/芫花等）
- 十九畏
- 妊娠禁忌（禁用 + 慎用两级）
- 毒性药材上限（附子、川乌、草乌、马钱子、细辛、半夏等）
- 药典常用量区间

**法规合规**：
- 不直接出具处方给药房
- 所有输出须经医师确认才可用于临床
- 医案入库前必须脱敏（姓名、身份证、住址、联系方式、精确日期）

---

## 许可证

MIT License —— 仅供学习和研究使用。

---

## 更新日志

- **2026-10-06** v0.1.0 · 项目初始化 + Phase 0.1/0.3 完成（34 个单元测试通过）
- 配套手册 v1.1（2026-10-05）已实施到代码
