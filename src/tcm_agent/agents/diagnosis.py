"""主 Agent（手册 §14.2）。"""
from __future__ import annotations

from pydantic_ai import Agent

from tcm_agent.config import VERIFIER_RETRIES
from tcm_agent.models import build_model
from tcm_agent.schemas import Diagnosis
from tcm_agent.agents.verifiers import ALL_VERIFIERS


def build_diagnosis_agent(model_name: str = "minimax") -> Agent:
    agent = Agent(
        build_model(model_name),
        output_type=Diagnosis,
        retries=VERIFIER_RETRIES,
        instructions=(
            "你是中医辨证论治助手，服务对象是执业中医师，不是患者。\n"
            "1. 必须先查看提供的教材证据，任何结论都要有出处。\n"
            "2. 证据不足时，把证据缺口写进 missing_info，不要编造。\n"
            "3. 只给药名、君臣佐使和剂量档位，不要自己写克数（克数由代码计算）。\n"
            "4. reasoning 必须逐条引用所用证据。"
        ),
    )
    for verifier in ALL_VERIFIERS:
        agent.output_validator(verifier)
    return agent