"""S1 分诊（手册 S1）。"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

import yaml

from tcm_agent.config import TRIAGE_TIMEOUT_S
from tcm_agent.schemas import PatientInput, TriageResult

_RULES_CACHE: list | None = None


def _load_redflags() -> list[dict]:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        path = Path(__file__).parent / "safety" / "redflags.yaml"
        _RULES_CACHE = yaml.safe_load(path.read_text(encoding="utf-8"))["redflags"]
    return _RULES_CACHE


def _match_redflags(patient: PatientInput) -> list[str]:
    triggered: list[str] = []
    haystack = " ".join([
        patient.chief_complaint, *patient.symptoms, *patient.history, patient.raw_text or "",
    ])
    for rule in _load_redflags():
        for pat in rule["patterns"]:
            if re.search(pat, haystack):
                triggered.append(rule["id"])
                break
    return triggered


async def run_triage(patient: PatientInput) -> TriageResult:
    triggered = _match_redflags(patient)
    if triggered:
        return TriageResult(
            level="red", triggered_rules=triggered,
            advice="检测到红旗症状，建议立即就医或拨打急救电话。本系统不出具处方。",
            passed=False,
        )

    try:
        await asyncio.wait_for(_maybe_llm_escalate(patient), timeout=TRIAGE_TIMEOUT_S)
        escalation = None
    except (asyncio.TimeoutError, Exception):
        escalation = None

    return TriageResult(
        level="yellow" if escalation else "green",
        triggered_rules=[], llm_escalation=escalation,
        advice="", passed=True,
    )


async def _maybe_llm_escalate(patient: PatientInput) -> str | None:
    return None