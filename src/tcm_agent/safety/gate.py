"""S7 安全闸门（手册 S7）。

纯 Python 函数，**不经过 LLM**，命中即终止。
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

_RULES_CACHE: dict | None = None


def _load_rules() -> dict:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        path = Path(__file__).parent / "rules.yaml"
        _RULES_CACHE = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _RULES_CACHE


class SafetyVerdict(BaseModel):
    passed: bool
    reason: str = ""


def check_incompatibility(herbs: list[str]) -> list[str]:
    rules = _load_rules()
    herbs_set = set(herbs)
    hits: list[str] = []
    for key, conflicts in {**rules["shiba_fan"], **rules["shijiu_wei"]}.items():
        if key in herbs_set:
            for c in conflicts:
                if c in herbs_set:
                    hits.append(f"{key} ↔ {c}（配伍禁忌）")
    return hits


def check_pregnancy(herbs: list[str], pregnancy: str) -> list[str]:
    if pregnancy != "是":
        return []
    rules = _load_rules()
    hits: list[str] = []
    for h in herbs:
        if h in rules["pregnancy_banned"]:
            hits.append(f"{h}（妊娠禁用）")
        elif h in rules["pregnancy_cautious"]:
            hits.append(f"{h}（妊娠慎用）")
    return hits


def check_toxicity(herbs_with_dose: list[tuple[str, float]]) -> list[str]:
    rules = _load_rules()
    limits = rules["toxicity_limit_g"]
    hits: list[str] = []
    for h, d in herbs_with_dose:
        if h in limits and d > limits[h]:
            hits.append(f"{h} 剂量 {d}g 超上限 {limits[h]}g")
    return hits


def check_pharmacopoeia_range(herbs_with_dose: list[tuple[str, float]]) -> list[str]:
    rules = _load_rules()
    rng = rules["pharmacopoeia_range"]
    hits: list[str] = []
    for h, d in herbs_with_dose:
        if h in rng:
            lo, hi = rng[h]
            if d < lo or d > hi:
                hits.append(f"{h} 剂量 {d}g 越界 [{lo}, {hi}]")
    return hits


def safety_gate(diagnosis, patient_input) -> SafetyVerdict:
    herbs = [h.name for h in diagnosis.prescription.herbs]
    herbs_with_dose = [(h.name, h.dose_g) for h in diagnosis.prescription.herbs]

    for check, label in [
        (lambda: check_incompatibility(herbs), "配伍禁忌"),
        (lambda: check_pregnancy(herbs, patient_input.pregnancy), "妊娠禁忌"),
        (lambda: check_toxicity(herbs_with_dose), "毒性剂量"),
        (lambda: check_pharmacopoeia_range(herbs_with_dose), "药典区间"),
    ]:
        hits = check()
        if hits:
            return SafetyVerdict(passed=False, reason=f"{label}：{chr(59).join(hits)}")
    return SafetyVerdict(passed=True)