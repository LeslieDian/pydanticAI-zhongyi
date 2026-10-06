"""关键词检索（pg_jieba + tsvector）。

Phase 0 stub。"""
from __future__ import annotations

import logging

from ..schemas import NormalizedFinding

logger = logging.getLogger(__name__)


async def lexical_search(
    findings: list[NormalizedFinding],
    top_k: int = 30,
) -> list[dict]:
    if not findings:
        return []
    logger.debug("lexical_search stub")
    return []
