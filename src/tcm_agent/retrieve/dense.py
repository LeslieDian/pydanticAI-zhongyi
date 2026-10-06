"""稠密检索（pgvector HNSW）。

Phase 0 stub：未连库时返回空；Phase 1 接 BGE-M3 + pgvector。
"""
from __future__ import annotations

import logging

from ..schemas import NormalizedFinding

logger = logging.getLogger(__name__)


async def dense_search(
    findings: list[NormalizedFinding],
    top_k: int = 30,
) -> list[dict]:
    """返回 [{chunk_id, content, source_ref, score}]."""
    if not findings:
        return []
    # Phase 0 stub：不连库，返回空
    logger.debug("dense_search stub: %d findings, top_k=%d", len(findings), top_k)
    return []
