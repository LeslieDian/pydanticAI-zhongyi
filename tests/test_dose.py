"""剂量计算测试（手册 §7 + S7，★v1.1）。"""
from tcm_agent.safety.dose import fill_dose, _classify_toxicity
from tcm_agent.schemas import HerbPlan


def test_classify_toxicity():
    assert _classify_toxicity("附子") == "大毒"
    assert _classify_toxicity("桂枝") == "无毒"
    assert _classify_toxicity("生石膏") == "无毒"


def test_special_controlled_herb_locked():
    plan = HerbPlan(name="附子", role="君", dose_tier="常量")
    herb = fill_dose(plan, "桂枝汤")
    assert herb.toxicity == "大毒"
    assert herb.review_required is True
    assert herb.dose_source == "大毒锁定"


def test_normal_herb_dose_calculation():
    plan = HerbPlan(name="桂枝", role="君", dose_tier="常量", is_added=False)
    herb = fill_dose(plan, "桂枝汤")
    assert herb.role == "君"
    assert herb.toxicity == "无毒"
    assert herb.role_source == "图谱回填"
    assert 3.0 <= herb.dose_g <= 10.0


def test_added_herb_role_source():
    plan = HerbPlan(name="黄芪", role="臣", dose_tier="常量", is_added=True)
    herb = fill_dose(plan, "桂枝汤")
    assert herb.role_source == "LLM判定"


def test_mineral_herb_whitelist():
    plan = HerbPlan(name="生石膏", role="君", dose_tier="高", is_added=False)
    herb = fill_dose(plan, "白虎汤")
    assert herb.review_required is False