"""evals/evaluators.py unit tests."""
import pytest
from evals.evaluators import (
    EvalCase, load_eval_dataset, evaluate_diagnosis,
    aggregate_results, evaluate_safety,
)
from tcm_agent.schemas import Diagnosis, Herb, Prescription, Syndrome, Treatment


def test_load_demo_dataset():
    cases = load_eval_dataset("evals/dataset/demo_5_cases.json")
    assert len(cases) == 5
    assert cases[0].case_id == "demo_001"
    assert cases[3].expected_formula == "REFUSED"


def test_evaluate_safety_pass():
    diag = Diagnosis(
        syndrome=Syndrome(name="x"), treatment=Treatment(principle="y"),
        prescription=Prescription(
            base_formula="z",
            herbs=[Herb(name="桂枝", role="君", dose_g=9.0, dose_source="基础方常量")],
        ),
    )
    ok, v = evaluate_safety(diag)
    assert ok is True
    assert v == []


def test_evaluate_safety_fail_incompatibility():
    diag = Diagnosis(
        syndrome=Syndrome(name="x"), treatment=Treatment(principle="y"),
        prescription=Prescription(
            base_formula="z",
            herbs=[
                Herb(name="甘草", role="君", dose_g=6.0, dose_source="基础方常量"),
                Herb(name="甘遂", role="臣", dose_g=1.0, dose_source="基础方常量"),
            ],
        ),
    )
    ok, v = evaluate_safety(diag)
    assert ok is False
    assert len(v) > 0


def test_evaluate_diagnosis_full_match():
    case = EvalCase(
        case_id="t1", chief_complaint="x", symptoms=[],
        expected_syndrome="风寒表实证", expected_formula="麻黄汤",
        expected_treatment="辛温解表",
    )
    diag = Diagnosis(
        syndrome=Syndrome(name="风寒表实证"), treatment=Treatment(principle="辛温解表"),
        prescription=Prescription(
            base_formula="麻黄汤",
            herbs=[Herb(name="麻黄", role="君", dose_g=9.0, dose_source="基础方常量")],
        ),
    )
    r = evaluate_diagnosis(case, diag)
    assert r.syndrome_match is True
    assert r.formula_match is True
    assert r.safety_pass is True


def test_aggregate_results():
    case = EvalCase(
        case_id="t1", chief_complaint="x", symptoms=[],
        expected_syndrome="风寒表实证", expected_formula="麻黄汤",
        expected_treatment="辛温解表",
    )
    diag_match = Diagnosis(
        syndrome=Syndrome(name="风寒表实证"), treatment=Treatment(principle="辛温解表"),
        prescription=Prescription(
            base_formula="麻黄汤",
            herbs=[Herb(name="麻黄", role="君", dose_g=9.0, dose_source="基础方常量")],
        ),
    )
    diag_miss = Diagnosis(
        syndrome=Syndrome(name="错了"), treatment=Treatment(principle="错了"),
        prescription=Prescription(
            base_formula="错了",
            herbs=[Herb(name="附子", role="君", dose_g=50.0, dose_source="基础方常量")],
        ),
    )
    results = [evaluate_diagnosis(case, diag_match), evaluate_diagnosis(case, diag_miss)]
    agg = aggregate_results(results)
    assert agg["total"] == 2
    assert agg["syndrome_accuracy"] == 0.5
    assert agg["safety_pass_rate"] == 0.5
