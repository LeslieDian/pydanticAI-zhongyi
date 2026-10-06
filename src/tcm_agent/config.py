"""常量与阈值（手册 §4 / §7 / §10 集中维护）。"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# 路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DICT_DIR = DATA_DIR / "dict"
INDEX_DIR = DATA_DIR / "index"
KNOWLEDGE_DIR = PROJECT_ROOT / "src" / "tcm_agent" / "knowledge"

# 阈值（与手册对齐）
RETRIEVAL_MIN_SCORE = float(os.getenv("RETRIEVAL_MIN_SCORE", "0.35"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.5"))
VERIFIER_RETRIES = int(os.getenv("VERIFIER_RETRIES", "3"))
PIPELINE_TIMEOUT_S = float(os.getenv("PIPELINE_TIMEOUT_S", "30"))
TRIAGE_TIMEOUT_S = float(os.getenv("TRIAGE_TIMEOUT_S", "3"))

# 模型
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "abab6.5s-chat")

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 数据
PG_DSN = os.getenv("PG_DSN", "postgresql://postgres:postgres@localhost:5432/tcm_agent")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# 召回参数
DENSE_TOP_K = 30
LEXICAL_TOP_K = 30
GRAPH_TOP_K = 10
RERANK_TOP_K = 5
RRF_K = 60

# 默认免责声明（手册 §8.3）
DEFAULT_DISCLAIMER = (
    "本输出由 AI 系统基于教材与药典规则生成，仅供执业中医师参考，不构成处方。"
    "任何临床决策须由具有资质的医师做出。"
)

# 毒性分级剂量系数（手册 §7 / S7 ★v1.1）
# 不设全局系数；按药典毒性三级分开
TIER_MULTIPLIER = {
    "无毒": {"低": 0.6, "常量": 1.0, "高": 1.4},
    "有毒": {"低": 0.8, "常量": 1.0, "高": 1.0},  # 高档不放大
    "大毒": {"低": 0.8, "常量": 1.0, "高": 1.0},  # 大毒：高档不开放，实际由 code 锁定
}

# 角色系数（手册 S7）
ROLE_MULTIPLIER = {
    "君": 1.0,
    "臣": 0.7,
    "佐": 0.5,
    "使": 0.3,
}

# V5.4 白名单：矿物/贝壳类允许君药大剂量（白虎汤生石膏等）
# 命中白名单的药材，"君药取高档" 不触发 ModelRetry
MINERAL_HERB_WHITELIST = {
    "生石膏", "煅石膏", "牡蛎", "龙骨", "龙齿",
    "珍珠母", "瓦楞子", "石决明", "海蛤壳", "海浮石",
    "磁石", "紫石英", "白石英", "阳起石", "代赭石",
}

# 特殊管控药材清单（直接走"大毒"通道：剂量锁定 + review_required=True）
SPECIAL_CONTROLLED_HERBS = {
    "附子", "川乌", "草乌", "马钱子", "细辛",
    "半夏", "巴豆", "甘遂", "大戟", "芫花", "天南星",
}

# 验证器总数（用于 confidence_score 分母）
VERIFIER_COUNT = 5
