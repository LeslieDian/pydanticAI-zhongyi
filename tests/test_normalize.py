"""S2 规范化测试（手册 S2）。"""
from tcm_agent.normalize import normalize
from tcm_agent.schemas import PatientInput


def test_synonym_match_symptom_list():
    inp = PatientInput(chief_complaint="x", symptoms=["畏寒", "怕冷"])
    fs = normalize(inp)
    assert any(f.raw == "畏寒" and f.canonical == "恶寒" for f in fs)
    assert any(f.raw == "怕冷" and f.canonical == "恶寒" for f in fs)


def test_negation_detection():
    fs = normalize(PatientInput(chief_complaint="不恶寒"))
    assert fs[0].negated is True


def test_unmatched_keeps_raw():
    fs = normalize(PatientInput(chief_complaint="某个未登录的怪症状"))
    assert fs[0].match_method == "unmatched" and fs[0].needs_review is True
    assert fs[0].canonical == "某个未登录的怪症状"


def test_exact_match_high_score():
    fs = normalize(PatientInput(chief_complaint="恶寒"))
    assert fs[0].match_method == "exact_dict" and fs[0].match_score == 1.0