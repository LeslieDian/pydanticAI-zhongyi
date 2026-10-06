"""S7 安全闸门测试（手册 §8）。"""
from tcm_agent.safety.gate import (
    check_incompatibility, check_pregnancy,
    check_toxicity, check_pharmacopoeia_range, safety_gate,
)
from tcm_agent.schemas import Diagnosis, Herb, PatientInput, Prescription, Syndrome, Treatment


def test_shibafan_hit():
    assert len(check_incompatibility(["甘草", "甘遂"])) == 1


def test_shibafan_miss():
    assert check_incompatibility(["甘草", "桂枝"]) == []


def test_pregnancy_banned():
    hits = check_pregnancy(["巴豆", "桂枝"], pregnancy="是")
    assert any("巴豆" in h for h in hits)


def test_pregnancy_safe_when_not_pregnant():
    assert check_pregnancy(["巴豆"], pregnancy="否") == []


def test_toxicity_limit_exceeded():
    assert len(check_toxicity([("附子", 20.0)])) == 1


def test_toxicity_within_limit():
    assert check_toxicity([("附子", 10.0)]) == []


def test_pharmacopoeia_range_violation():
    assert len(check_pharmacopoeia_range([("桂枝", 30.0)])) == 1


def test_safety_gate_blocked():
    diag = Diagnosis(
        syndrome=Syndrome(name="X"), treatment=Treatment(principle="Y"),
        prescription=Prescription(
            base_formula="Z",
            herbs=[
                Herb(name="甘草", role="君", dose_g=6.0, dose_source="基础方常量"),
                Herb(name="甘遂", role="臣", dose_g=1.0, dose_source="基础方常量"),
            ],
        ),
    )
    inp = PatientInput(chief_complaint="x")
    v = safety_gate(diag, inp)
    assert v.passed is False
    assert "甘草" in v.reason


def test_safety_gate_passed():
    diag = Diagnosis(
        syndrome=Syndrome(name="风寒表实证"), treatment=Treatment(principle="辛温解表"),
        prescription=Prescription(
            base_formula="桂枝汤",
            herbs=[
                Herb(name="桂枝", role="君", dose_g=9.0, dose_source="基础方常量"),
                Herb(name="芍药", role="臣", dose_g=9.0, dose_source="基础方常量"),
            ],
        ),
    )
    inp = PatientInput(chief_complaint="x")
    assert safety_gate(diag, inp).passed is True