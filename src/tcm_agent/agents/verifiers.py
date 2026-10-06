"""5 个验证器（手册 §5 S5，★v1.1 新增 V5）。"""
from __future__ import annotations

from pydantic_ai import ModelRetry

from tcm_agent.config import MINERAL_HERB_WHITELIST
from tcm_agent.retrieve.graph import has_path, is_syndrome_covered
from tcm_agent.safety.gate import check_incompatibility
from tcm_agent.safety.dose import _load_pharm
from tcm_agent.schemas import Diagnosis


async def v1_graph_path(diag: Diagnosis) -> Diagnosis:
    syndrome = diag.syndrome.name
    principle = diag.treatment.principle
    formula = diag.prescription.base_formula

    if await has_path(syndrome, principle, formula):
        return diag

    covered = await is_syndrome_covered(syndrome)
    if not covered:
        diag.syndrome.out_of_graph_coverage = True
        return diag

    raise ModelRetry(
        f"图谱中存在证候 {syndrome} 但无 {principle} → {formula} 路径。"
        f"若确超出图谱覆盖范围，请改从检索证据中选择有明确出处的方剂，"
        f"并在 missing_info 中说明。"
    )


async def v2_incompatibility(diag: Diagnosis) -> Diagnosis:
    herbs = [h.name for h in diag.prescription.herbs]
    hits = check_incompatibility(herbs)
    if hits:
        raise ModelRetry(f"配伍违规：{chr(59).join(hits)}。请替换后重新组方。")
    return diag


async def v3_dose_tier(diag: Diagnosis) -> Diagnosis:
    pharm = _load_pharm()["pharmacopoeia_range"]
    for h in diag.prescription.herbs:
        rng = pharm.get(h.name)
        if rng and (h.dose_g < rng[0] or h.dose_g > rng[1]):
            raise ModelRetry(
                f"{h.name} 剂量 {h.dose_g}g 越界 [{rng[0]}, {rng[1]}]，请调整。"
            )
    return diag


async def v4_source_backfill(diag: Diagnosis) -> Diagnosis:
    return diag


async def v5_role_assignment(diag: Diagnosis) -> Diagnosis:
    herbs = diag.prescription.herbs
    jun_count = sum(1 for h in herbs if h.role == "君")
    if jun_count < 1 or jun_count > 2:
        raise ModelRetry(
            f"君臣佐使分配异常：君药数量为 {jun_count}（应在 1–2 之间）。"
        )

    for h in herbs:
        if h.role_source == "LLM判定" and h.role == "君":
            h.review_required = True

    for h in herbs:
        if h.role == "君" and h.name not in MINERAL_HERB_WHITELIST and h.dose_g < 6.0:
            raise ModelRetry(
                f"{h.name} 为君药但剂量 {h.dose_g}g 过低（白名单外矿物/贝壳类君药应 ≥6g）。"
            )

    return diag


ALL_VERIFIERS = [v1_graph_path, v2_incompatibility, v3_dose_tier, v4_source_backfill, v5_role_assignment]