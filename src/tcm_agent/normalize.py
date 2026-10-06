"""S2 术语规范化（手册 S2）。"""
from __future__ import annotations

import re

from tcm_agent.schemas import NormalizedFinding, PatientInput

SYNONYM_DICT: dict[str, str] = {
    "畏寒": "恶寒",
    "怕冷": "恶寒",
    "手足不温": "恶寒",
    "恶寒": "恶寒",
    "发热": "发热",
    "发烧": "发热",
    "身热": "发热",
    "自汗": "自汗",
    "盗汗": "盗汗",
    "无汗": "无汗",
    "不出汗": "无汗",
    "舌红": "舌红",
    "舌淡": "舌淡",
    "苔黄": "苔黄",
    "苔白": "苔白",
    "胃脘痛": "胃痛",
    "肚子痛": "腹痛",
    "拉肚子": "腹泻",
    "不恶寒": "NOT_恶寒",
    "无恶寒": "NOT_恶寒",
    "否认恶寒": "NOT_恶寒",
}

_NEGATION_RE = re.compile(r"^(不|无|否认|未)(?!.*不)")


def _detect_negation(raw: str):
    m = _NEGATION_RE.match(raw)
    return (raw[1:], True) if m else (raw, False)


def _lookup_dict(text: str):
    return SYNONYM_DICT.get(text)


def normalize(patient):
    findings = []
    raw = patient.chief_complaint.strip()
    text, negated = _detect_negation(raw)
    canonical = _lookup_dict(text)
    if canonical is None:
        canonical, mm, ms, nr = text, "unmatched", None, True
    else:
        mm, ms, nr = "exact_dict", 1.0, False
    findings.append(NormalizedFinding(
        raw=raw, canonical=canonical, category="症状",
        match_method=mm, match_score=ms, needs_review=nr, negated=negated,
    ))
    for s in patient.symptoms:
        s = s.strip()
        if not s:
            continue
        text, negated = _detect_negation(s)
        canonical = _lookup_dict(text)
        if canonical is None:
            canonical, mm, ms, nr = text, "unmatched", None, True
        else:
            mm, ms, nr = "exact_dict", 1.0, False
        findings.append(NormalizedFinding(
            raw=s, canonical=canonical, category="症状",
            match_method=mm, match_score=ms, needs_review=nr, negated=negated,
        ))
    return findings
