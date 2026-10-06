"""评测体系（手册 §9）。"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from tcm_agent.safety.gate import check_incompatibility, check_pregnancy, check_toxicity, check_pharmacopoeia_range


@dataclass
class EvalCase:
    case_id: str
    chief_complaint: str
    symptoms: list
    expected_syndrome: str
    expected_formula: str
    expected_treatment: str
    ground_truth_dose_ranges: Optional[dict] = None


@dataclass
class EvalResult:
    case_id: str
    syndrome_match: bool
    formula_match: bool
    treatment_match: bool
    safety_pass: bool
    dose_in_range: bool
    rule_violations: list


def load_eval_dataset(path: str) -> list:
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [EvalCase(**c) for c in data]


def evaluate_safety(diag, pregnancy: str = "否") -> tuple:
    herbs = [h.name for h in diag.prescription.herbs]
    herbs_with_dose = [(h.name, h.dose_g) for h in diag.prescription.herbs]
    violations = []
    violations.extend(check_incompatibility(herbs))
    violations.extend(check_pregnancy(herbs, pregnancy))
    violations.extend(check_toxicity(herbs_with_dose))
    violations.extend(check_pharmacopoeia_range(herbs_with_dose))
    return len(violations) == 0, violations


def evaluate_diagnosis(case, diag) -> EvalResult:
    syn_match = diag.syndrome.name == case.expected_syndrome
    fml_match = diag.prescription.base_formula == case.expected_formula
    trt_match = diag.treatment.principle == case.expected_treatment
    safety_pass, violations = evaluate_safety(diag)
    dose_in_range = True
    if case.ground_truth_dose_ranges:
        for h in diag.prescription.herbs:
            rng = case.ground_truth_dose_ranges.get(h.name)
            if rng and not (rng[0] <= h.dose_g <= rng[1]):
                dose_in_range = False
                break
    return EvalResult(
        case_id=case.case_id,
        syndrome_match=syn_match,
        formula_match=fml_match,
        treatment_match=trt_match,
        safety_pass=safety_pass,
        dose_in_range=dose_in_range,
        rule_violations=violations,
    )


def aggregate_results(results: list) -> dict:
    n = len(results)
    if n == 0:
        return {}
    return {
        "total": n,
        "syndrome_accuracy": sum(r.syndrome_match for r in results) / n,
        "formula_accuracy": sum(r.formula_match for r in results) / n,
        "treatment_accuracy": sum(r.treatment_match for r in results) / n,
        "safety_pass_rate": sum(r.safety_pass for r in results) / n,
        "dose_in_range_rate": sum(r.dose_in_range for r in results) / n,
        "violations": [v for r in results for v in r.rule_violations],
    }
