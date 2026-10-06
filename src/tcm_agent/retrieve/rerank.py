"""BGE-reranker-v2-m3 精排。"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Cross-encoder 重排。

    Phase 0 stub：按原序返回 top_k。
    Phase 1 接 BGE-reranker-v2-m3。
    """
    logger.debug("rerank stub: %d → %d", len(candidates), top_k)
    return candidates[:top_k]
