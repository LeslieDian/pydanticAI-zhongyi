"""图谱查询（Neo4j Cypher）。"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def graph_search(syndrome_candidates: list[str], top_k: int = 10) -> list[dict]:
    """图谱多跳查询：症状→证候候选、证候→方剂。

    Phase 0 stub。
    """
    logger.debug("graph_search stub: %d candidates", len(syndrome_candidates))
    return []


async def has_path(syndrome: str, treatment: str, formula: str) -> bool:
    """验证 证候→治法→方剂 路径是否存在（V1 验证器）。"""
    # Phase 0 stub：图谱未建前一律 False → 触发 V1 分级
    logger.debug("has_path stub: %s→%s→%s", syndrome, treatment, formula)
    return False


async def is_syndrome_covered(syndrome: str) -> bool:
    """检查证候是否在图谱覆盖内（V1 分级核验）。"""
    # Phase 0 stub：图谱未建前一律 False（覆盖外）
    return False
