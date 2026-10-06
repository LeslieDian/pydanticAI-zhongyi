"""剂量计算（手册 §7 + S7）。

★v1.1：按药典毒性三级分级映射，不设全局 TIER_MULTIPLIER。
"""
from __future__ import annotations

from pathlib import Path

import yaml

from tcm_agent.config import (
    MINERAL_HERB_WHITELIST,
    ROLE_MULTIPLIER,
    SPECIAL_CONTROLLED_HERBS,
    TIER_MULTIPLIER,
)
from tcm_agent.knowledge.dosage_table import get_base_dose
from tcm_agent.schemas import Herb, HerbPlan

_RULES_CACHE: dict | None = None


def _load_pharm() -> dict:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        path = Path(__file__).parent / "rules.yaml"
        _RULES_CACHE = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _RULES_CACHE


def _classify_toxicity(name: str) -> str:
    if name in SPECIAL_CONTROLLED_HERBS:
        return "大毒"
    toxic_keywords = ["毒", "附子", "乌头", "马钱", "巴豆", "天南星", "甘遂", "大戟", "芫花"]
    if any(k in name for k in toxic_keywords):
        return "有毒"
    return "无毒"


def fill_dose(plan: HerbPlan, base_formula: str) -> Herb:
    toxicity = _classify_toxicity(plan.name)

    if plan.name in SPECIAL_CONTROLLED_HERBS:
        pharm_lo = _load_pharm()["pharmacopoeia_range"].get(plan.name, [0, 0])[0]
        return Herb(
            name=plan.name, role="臣", dose_g=pharm_lo,
            dose_source="大毒锁定", processing=plan.processing,
            role_source="LLM判定" if plan.is_added else "图谱回填",
            toxicity="大毒", review_required=True,
        )

    base = get_base_dose(base_formula, plan.name)
    if base is None:
        pharm_rng = _load_pharm()["pharmacopoeia_range"].get(plan.name)
        base = (pharm_rng[0] + pharm_rng[1]) / 2.0 if pharm_rng else 9.0

    tier_mul = TIER_MULTIPLIER[toxicity][plan.dose_tier]
    role_mul = ROLE_MULTIPLIER[plan.role]
    final = base * tier_mul * role_mul

    pharm_rng = _load_pharm()["pharmacopoeia_range"].get(plan.name)
    if pharm_rng:
        final = max(pharm_rng[0], min(pharm_rng[1], final))

    return Herb(
        name=plan.name, role=plan.role, dose_g=round(final, 1),
        dose_source="基础方常量" if base == get_base_dose(base_formula, plan.name) else "档位折算",
        processing=plan.processing,
        role_source="LLM判定" if plan.is_added else "图谱回填",
        toxicity=toxicity,
        review_required=(plan.role == "君" and plan.dose_tier == "高" and plan.name not in MINERAL_HERB_WHITELIST),
    )


def fill_prescription_doses(prescription) -> None:
    new_herbs = []
    for h in prescription.herbs:
        if isinstance(h, Herb) and h.dose_g > 0:
            new_herbs.append(h)
            continue
        plan = h if isinstance(h, HerbPlan) else HerbPlan(**h.model_dump())
        new_herbs.append(fill_dose(plan, prescription.base_formula))
    prescription.herbs = new_herbs