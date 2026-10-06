"""所有 Pydantic 模型，单一事实源（手册 §4）。

含 v1.1 增量：
- PatientInput.session_id / turn
- NormalizedFinding.match_method / match_score / needs_review
- Herb.role_source / toxicity / review_required
- Syndrome.out_of_graph_coverage
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .config import DEFAULT_DISCLAIMER

# ============ §4.1 输入侧 ============

class TongueSign(BaseModel):
    tongue_body: Literal["淡白", "淡红", "红", "绛", "紫暗", "胖大", "瘦薄", "齿痕"] | None = None
    tongue_coating: Literal["薄白", "白腻", "黄腻", "剥落", "少苔", "灰黑"] | None = None


class PulseSign(BaseModel):
    quality: list[str] = Field(default_factory=list)
    source: Literal["医师", "自诉", "缺失"] = "缺失"


class PatientInput(BaseModel):
    """四诊原始输入。"""

    age: int | None = None
    sex: Literal["男", "女", "未知"] = "未知"
    pregnancy: Literal["是", "否", "未知"] = "未知"
    chief_complaint: str
    symptoms: list[str] = Field(default_factory=list)
    duration: str | None = None
    history: list[str] = Field(default_factory=list)
    tongue: TongueSign = Field(default_factory=TongueSign)
    pulse: PulseSign = Field(default_factory=PulseSign)
    raw_text: str | None = None

    # ★v1.1：多轮会话字段（现在加上，成本为零，避免后期审计表迁移）
    session_id: str | None = None
    turn: int = 1


# ============ §4.2 分诊侧 ============

class TriageResult(BaseModel):
    level: Literal["red", "yellow", "green"]
    triggered_rules: list[str] = Field(default_factory=list)
    llm_escalation: str | None = None  # LLM 只能追加上调，不能下调
    advice: str = ""
    passed: bool  # level != "red"


# ============ §4.3 规范化侧 ============

class NormalizedFinding(BaseModel):
    raw: str
    canonical: str
    category: Literal["症状", "舌象", "脉象", "病史", "体征"]
    # ★v1.1：confidence 拆开 — 词典命中与向量匹配的"置信"是两个语义
    match_method: Literal["exact_dict", "vector_match", "unmatched"]
    match_score: float | None = None  # 仅 vector_match 时有值
    # ★v1.1：向量兜底且 match_score < 0.75 时置 True，进人工抽检队列
    needs_review: bool = False
    negated: bool = False  # "不 X" / "无 X" / "否认 X"


# ============ §4.4 主链输出侧（核心） ============

class HerbPlan(BaseModel):
    """LLM 只输出"意图"，不输出克数。"""

    name: str  # 规范药名
    role: Literal["君", "臣", "佐", "使"]
    dose_tier: Literal["常量", "低", "中", "高"] = "常量"
    processing: str | None = None  # 炮制，如"蜜炙"
    is_added: bool = True  # True=加减药，False=基础方原味


class Herb(BaseModel):
    """最终输出。dose_g 由 safety/dose.py 计算填充，LLM 无法直接写。"""

    name: str
    role: Literal["君", "臣", "佐", "使"]
    dose_g: float
    # ★v1.1：克数来源可审计
    dose_source: Literal["基础方常量", "档位折算", "图谱区间夹取", "大毒锁定"]
    processing: str | None = None
    # ★v1.1：基础方原味的 role 由图谱回填；加减药由 LLM 判定
    role_source: Literal["图谱回填", "LLM判定"] = "LLM判定"
    # ★v1.1：药典三级毒性分级，决定档位映射
    toxicity: Literal["无毒", "有毒", "大毒"] = "无毒"
    # ★v1.1：含"大毒"药材时置 True，强制人工复核标记
    review_required: bool = False


class Prescription(BaseModel):
    base_formula: str
    base_formula_source: str = ""  # ★图谱回填，LLM 不得填写
    source_ref: str | None = None  # 条文出处编号，图谱回填
    herbs: list[Herb] = Field(default_factory=list)
    modifications: list[str] = Field(default_factory=list)
    usage: str = ""
    course: str = ""


class Evidence(BaseModel):
    claim: str
    source_type: Literal["教材", "药典", "知识图谱", "医案", "方剂学"]
    source_ref: str
    snippet: str
    score: float  # rerank 分数


class Syndrome(BaseModel):
    name: str
    confidence_llm: float | None = None  # LLM 自评，仅展示，不参与控制
    confidence_score: float | None = None  # 代码计算，参与控制
    missing_info: list[str] = Field(default_factory=list)
    # ★v1.1：图谱覆盖外的证候标记，用于 V1 分级核验
    out_of_graph_coverage: bool = False


class Treatment(BaseModel):
    principle: str  # 治法，如"辛温解表"
    method: str = ""  # 具体治法


class Diagnosis(BaseModel):
    """一次调用的完整输出。"""

    syndrome: Syndrome
    treatment: Treatment
    prescription: Prescription
    reasoning: str = ""  # 输出时标注"AI 推理，非医师诊断"
    evidence: list[Evidence] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    disclaimer: str = DEFAULT_DISCLAIMER
    # 审计元数据
    run_id: str | None = None
    timestamp: str | None = None


# ============ 流水线结果 ============

class FinalOutput(BaseModel):
    """流水线最终输出。所有分支（拒诊/拒答/低置信/出方）都由此类型表达。"""

    status: Literal[
        "refused",                # 分诊拒诊（红旗）
        "insufficient_evidence",  # 拒答闸门（检索分数低）
        "low_confidence",         # 低置信（confidence_score < MIN_CONFIDENCE）
        "blocked",                # 安全闸门拒绝
        "ok",                     # 正常出方
    ]
    diagnosis: Diagnosis | None = None
    triage: TriageResult | None = None
    advice: str = ""  # 拒诊/拒答时给用户的指引
    reason: str = ""  # blocked 时记录被哪条规则拦下

    @classmethod
    def refused(cls, triage: TriageResult) -> "FinalOutput":
        return cls(status="refused", triage=triage, advice=triage.advice)

    @classmethod
    def insufficient(cls) -> "FinalOutput":
        return cls(
            status="insufficient_evidence",
            advice="现有资料不足以支撑可靠辨证，建议线下就诊。",
        )

    @classmethod
    def low(cls) -> "FinalOutput":
        return cls(
            status="low_confidence",
            advice="多源证据一致性不足，建议由医师面诊复核。",
        )

    @classmethod
    def blocked(cls, reason: str) -> "FinalOutput":
        return cls(status="blocked", reason=reason, advice=f"安全闸门拦截：{reason}")

    @classmethod
    def ok(cls, diag: Diagnosis) -> "FinalOutput":
        return cls(status="ok", diagnosis=diag)
