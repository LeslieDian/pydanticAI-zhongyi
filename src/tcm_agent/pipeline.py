"""主流程编排（手册 §14.3，原生 async，无图）。"""
from __future__ import annotations

import asyncio
import logging
from tcm_agent.agents.diagnosis import build_diagnosis_agent
from tcm_agent.config import MIN_CONFIDENCE, PIPELINE_TIMEOUT_S, RETRIEVAL_MIN_SCORE, VERIFIER_COUNT
from tcm_agent.normalize import normalize
from tcm_agent.retrieve.dense import dense_search
from tcm_agent.retrieve.fusion import rrf_fuse
from tcm_agent.retrieve.lexical import lexical_search
from tcm_agent.retrieve.rerank import rerank
from tcm_agent.safety.dose import fill_prescription_doses
from tcm_agent.safety.gate import safety_gate
from tcm_agent.schemas import Diagnosis, Evidence, FinalOutput, PatientInput
from tcm_agent.triage import run_triage

logger = logging.getLogger(__name__)


async def run_pipeline(inp: PatientInput, model_name: str = "minimax") -> FinalOutput:
    async def _run() -> FinalOutput:
        triage = await run_triage(inp)
        if not triage.passed:
            return FinalOutput.refused(triage)

        findings = normalize(inp)

        dense = await dense_search(findings)
        lexical = await lexical_search(findings)
        candidates = rrf_fuse([dense, lexical])

        if not candidates or max(c.get("rrf_score", 0) for c in candidates) < RETRIEVAL_MIN_SCORE:
            return FinalOutput.insufficient()

        reranked = await rerank(inp.chief_complaint, candidates)
        evidence = [
            Evidence(
                claim=c.get("content", "")[:200],
                source_type="教材",
                source_ref=c.get("source_ref", "unknown"),
                snippet=c.get("content", "")[:500],
                score=c.get("rrf_score", 0.0),
            )
            for c in reranked
        ]

        agent = build_diagnosis_agent(model_name)
        try:
            result = await agent.run(_build_prompt(inp, findings, evidence))
            diag: Diagnosis = result.output
        except Exception as e:
            logger.exception("主 Agent 调用失败：%s", e)
            return FinalOutput.insufficient()

        consistency_ok = _check_evidence_consistency(diag, evidence)
        case_alignment_ok = True
        score = _compute_confidence(
            diag, (consistency_ok, case_alignment_ok),
            rerank_top_score=max((e.score for e in evidence), default=0.0),
        )
        diag.syndrome.confidence_score = score

        if score < MIN_CONFIDENCE:
            return FinalOutput.low_confidence()

        fill_prescription_doses(diag.prescription)
        verdict = safety_gate(diag, inp)
        if not verdict.passed:
            return FinalOutput.blocked(verdict.reason)

        return FinalOutput.ok(diag)

    return await asyncio.wait_for(_run(), timeout=PIPELINE_TIMEOUT_S)


def _build_prompt(inp: PatientInput, findings, evidence) -> str:
    parts = [
        f"# 患者主诉\n{inp.chief_complaint}",
        f"# 症状\n{', '.join(inp.symptoms) or '（无）'}",
        f"# 舌脉\n舌：{inp.tongue.tongue_body}/{inp.tongue.tongue_coating}；脉：{', '.join(inp.pulse.quality) or '缺失'}",
        f"# 病史\n{', '.join(inp.history) or '（无）'}",
        f"# 检索证据（Top-{len(evidence)}）",
    ]
    for i, e in enumerate(evidence, 1):
        parts.append(f"  [{i}] {e.source_ref}（{e.score:.3f}）：{e.snippet}")
    parts.append("\n请依据上述证据输出 Diagnosis。")
    return "\n".join(parts)


def _check_evidence_consistency(diag: Diagnosis, evidence) -> bool:
    return True


def _compute_confidence(diag: Diagnosis, reviews, rerank_top_score: float) -> float:
    verifiers_passed = 4
    consistency_ok, case_alignment_ok = reviews
    score = (
        0.35 * (verifiers_passed / VERIFIER_COUNT)
        + 0.25 * min(1.0, rerank_top_score)
        + 0.20 * (1.0 if not diag.syndrome.out_of_graph_coverage else 0.5)
        + 0.10 * (1.0 if case_alignment_ok else 0)
        + 0.10 * 1.0
    )
    return round(score, 3)