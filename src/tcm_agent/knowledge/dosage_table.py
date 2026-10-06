"""基础方剂量表（手册 §3 + §7）。

Phase 1 由图谱回填；Phase 0 用硬编码 5 个示范方剂跑通流程。
每个方剂 → {药名 → base_dose_g}。
"""
from __future__ import annotations

# 起步：5 个示范方剂（Phase 1 扩到 50+，Phase 3 扩到 200+）
DEMO_BASE_FORMULAS: dict[str, dict[str, float]] = {
    "桂枝汤": {"桂枝": 9.0, "芍药": 9.0, "甘草": 6.0, "生姜": 9.0, "大枣": 12.0},
    "麻黄汤": {"麻黄": 9.0, "桂枝": 6.0, "杏仁": 9.0, "甘草": 3.0},
    "白虎汤": {"生石膏": 30.0, "知母": 9.0, "甘草": 3.0, "粳米": 9.0},
    "四君子汤": {"人参": 9.0, "白术": 9.0, "茯苓": 9.0, "甘草": 6.0},
    "六味地黄丸": {"熟地黄": 24.0, "山茱萸": 12.0, "山药": 12.0, "泽泻": 9.0, "茯苓": 9.0, "丹皮": 9.0},
}


def get_base_dose(formula: str, herb: str) -> float | None:
    """查基础方常量剂量（克）。找不到返回 None。"""
    return DEMO_BASE_FORMULAS.get(formula, {}).get(herb)
