"""5 个验证器测试（手册 §5 S5）。"""
import pytest
from pydantic_ai import ModelRetry
from tcm_agent.agents.verifiers import v1_graph_path, v2_incompatibility, v3_dose_tier, v5_role_assignment
from tcm_agent.schemas import Diagnosis, Herb, Prescription, Syndrome, Treatment


def _diag(**kw):
    d = dict(
        syndrome=Syndrome(name="风寒表实证"),
        treatment=Treatment(principle="辛温解表"),
        prescription=Prescription(
            base_formula="麻黄汤",
            herbs=[
                Herb(name="麻黄", role="君", dose_g=9.0, dose_source="基础方常量"),
                Herb(name="桂枝", role="臣", dose_g=6.0, dose_source="基础方常量"),
                Herb(name="杏仁", role="佐", dose_g=9.0, dose_source="基础方常量"),
                Herb(name="甘草", role="使", dose_g=3.0, dose_source="基础方常量"),
            ],
        ),
    )
    d.update(kw)
    return Diagnosis(**d)


@pytest.mark.asyncio
async def test_v1_graph_path_stub_returns_diag():
    d = _diag()
    r = await v1_graph_path(d)
    assert r.syndrome.out_of_graph_coverage is True


@pytest.mark.asyncio
async def test_v2_incompatibility_clean():
    assert await v2_incompatibility(_diag()) is not None


@pytest.mark.asyncio
async def test_v2_incompatibility_hit():
    d = _diag(prescription=Prescription(
        base_formula="X",
        herbs=[
            Herb(name="甘草", role="君", dose_g=6.0, dose_source="基础方常量"),
            Herb(name="甘遂", role="臣", dose_g=1.0, dose_source="基础方常量"),
        ],
    ))
    with pytest.raises(ModelRetry) as exc:
        await v2_incompatibility(d)
    assert "甘草" in str(exc.value)


@pytest.mark.asyncio
async def test_v3_dose_in_range():
    assert await v3_dose_tier(_diag()) is not None


@pytest.mark.asyncio
async def test_v3_dose_out_of_range():
    d = _diag(prescription=Prescription(
        base_formula="X",
        herbs=[Herb(name="桂枝", role="君", dose_g=50.0, dose_source="基础方常量")],
    ))
    with pytest.raises(ModelRetry):
        await v3_dose_tier(d)


@pytest.mark.asyncio
async def test_v5_jun_count_valid():
    assert await v5_role_assignment(_diag()) is not None


@pytest.mark.asyncio
async def test_v5_too_many_jun():
    d = _diag(prescription=Prescription(
        base_formula="X",
        herbs=[
            Herb(name="麻黄", role="君", dose_g=9.0, dose_source="基础方常量"),
            Herb(name="桂枝", role="君", dose_g=6.0, dose_source="基础方常量"),
            Herb(name="石膏", role="君", dose_g=20.0, dose_source="基础方常量"),
        ],
    ))
    with pytest.raises(ModelRetry) as exc:
        await v5_role_assignment(d)
    assert "君药数量" in str(exc.value)