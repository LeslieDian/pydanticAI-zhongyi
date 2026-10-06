"""Schema 字段定稿测试（手册 §4）。"""
from tcm_agent.schemas import (
    Diagnosis,
    Evidence,
    Herb,
    HerbPlan,
    NormalizedFinding,
    PatientInput,
    Prescription,
    Syndrome,
    TongueSign,
    Treatment,
    TriageResult,
)


def test_patient_input_v11_fields():
    inp = PatientInput(
        chief_complaint="恶寒发热",
        session_id="s-001",
        turn=2,
    )
    assert inp.session_id == "s-001"
    assert inp.turn == 2
    assert inp.pulse.source == "缺失"


def test_normalized_finding_v11_fields():
    f = NormalizedFinding(
        raw="畏寒", canonical="恶寒", category="症状",
        match_method="exact_dict", match_score=1.0,
    )
    assert f.match_method == "exact_dict"
    assert f.match_score == 1.0


def test_herb_v11_fields():
    h = Herb(
        name="附子", role="君", dose_g=3.0, dose_source="大毒锁定",
        toxicity="大毒", review_required=True,
    )
    assert h.toxicity == "大毒"
    assert h.review_required is True


def test_diagnosis_construction():
    d = Diagnosis(
        syndrome=Syndrome(name="风寒表实证"),
        treatment=Treatment(principle="辛温解表"),
        prescription=Prescription(
            base_formula="麻黄汤",
            herbs=[Herb(name="麻黄", role="君", dose_g=9.0, dose_source="基础方常量")],
        ),
    )
    assert d.syndrome.name == "风寒表实证"
    assert len(d.prescription.herbs) == 1


def test_syndrome_out_of_graph_coverage():
    s = Syndrome(name="罕见证候", out_of_graph_coverage=True)
    assert s.out_of_graph_coverage is True