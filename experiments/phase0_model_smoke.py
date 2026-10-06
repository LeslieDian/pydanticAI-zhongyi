"""Phase 0.2 模型能力验证（手册 Phase 0 DoD）。

DoD：定义最小 Diagnosis schema，用 MiniMax 跑 20 次，
**每次 type(result.output) is Diagnosis**；不通过则调 profile 或换模型。

运行方式：
    export MINIMAX_API_KEY=...
    python -m experiments.phase0_model_smoke

预期输出：
    - 20/20 通过：模型能力达标，进入 Phase 1
    - <18/20 通过：调整 prompt / 换 profile / 换模型
"""
from __future__ import annotations

import asyncio
import sys

from pydantic_ai import Agent

from src.tcm_agent.config import MINIMAX_MODEL
from src.tcm_agent.models import build_model
from src.tcm_agent.schemas import (
    Diagnosis,
    Evidence,
    Herb,
    HerbPlan,
    Prescription,
    Syndrome,
    Treatment,
)


MINIMAL_PROMPT = """请依据以下四诊，输出嵌套 Diagnosis JSON。

主诉：恶寒发热 3 天，头痛无汗。
舌：淡红、苔薄白。
脉：浮紧。

请使用最小数据集（基础方=麻黄汤）：
- syndrome.name = "风寒表实证"
- treatment.principle = "辛温解表"
- prescription.base_formula = "麻黄汤"
- prescription.herbs 输出 HerbPlan（name + role + dose_tier + is_added=False）"""


async def smoke_test(model_name: str = "minimax", n_runs: int = 20) -> int:
    print(f"🚀 Phase 0.2 模型能力验证：model={model_name}, runs={n_runs}")
    print(f"   模型标识：{MINIMAX_MODEL if model_name == 'minimax' else 'deepseek-chat'}")

    model = build_model(model_name)
    agent = Agent(
        model,
        output_type=Diagnosis,
        retries=2,
        instructions="你是中医辨证论治助手。严格按 JSON schema 输出。",
    )

    passed = 0
    failures: list[str] = []
    for i in range(n_runs):
        try:
            result = await agent.run(MINIMAL_PROMPT)
            assert isinstance(result.output, Diagnosis), \
                f"run {i+1}: 输出类型 {type(result.output).__name__} ≠ Diagnosis"
            # 验证嵌套字段也被正确填充
            d = result.output
            assert isinstance(d.syndrome, Syndrome)
            assert isinstance(d.treatment, Treatment)
            assert isinstance(d.prescription, Prescription)
            assert d.syndrome.name, "syndrome.name 为空"
            assert d.treatment.principle, "treatment.principle 为空"
            assert d.prescription.base_formula, "prescription.base_formula 为空"
            passed += 1
            print(f"  ✓ run {i+1:2d}: {d.syndrome.name} → {d.prescription.base_formula}")
        except Exception as e:
            failures.append(f"run {i+1}: {type(e).__name__}: {e}")
            print(f"  ✗ run {i+1:2d}: {type(e).__name__}: {str(e)[:100]}")

    print()
    print(f"📊 结果：{passed}/{n_runs} 通过")
    if passed >= 18:
        print("✅ 模型能力达标，进入 Phase 1")
        return 0
    print(f"❌ 通过率 {passed/n_runs*100:.0f}% < 90%，需调 profile / prompt / 换模型")
    print()
    print("失败样本：")
    for f in failures[:5]:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "minimax"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    sys.exit(asyncio.run(smoke_test(model, n)))
