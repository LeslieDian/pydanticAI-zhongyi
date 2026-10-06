"""S1 分诊测试（手册 §5 S1）。"""
import pytest
from tcm_agent.schemas import PatientInput
from tcm_agent.triage import run_triage, _match_redflags


def test_redflag_match():
    inp = PatientInput(chief_complaint="剧烈胸痛 2 小时", symptoms=["大汗淋漓"])
    assert "cardiac_emergency" in _match_redflags(inp)


def test_no_redflag_match():
    inp = PatientInput(chief_complaint="恶寒发热 3 天", symptoms=["头痛", "无汗"])
    assert _match_redflags(inp) == []


@pytest.mark.asyncio
async def test_triage_red_passes_false():
    inp = PatientInput(chief_complaint="剧烈胸痛", symptoms=["大汗淋漓", "胸闷压榨感"])
    r = await run_triage(inp)
    assert r.level == "red" and r.passed is False
    assert "就医" in r.advice or "急救" in r.advice


@pytest.mark.asyncio
async def test_triage_green_passes_true():
    inp = PatientInput(chief_complaint="恶寒发热 3 天", symptoms=["头痛", "无汗"])
    r = await run_triage(inp)
    assert r.passed is True and r.level in ("green", "yellow")