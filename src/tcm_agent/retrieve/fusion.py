"""RRF 融合（手册 §6.4）。"""
from __future__ import annotations


def rrf_fuse(
    routes: list[list[dict]],
    top_k: int = 30,
    k: int = 60,
) -> list[dict]:
    """Reciprocal Rank Fusion。

    score(doc) = Σ 1 / (k + rank_in_route(doc))
    """
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    for route in routes:
        for rank, item in enumerate(route):
            doc_id = item.get("chunk_id") or item.get("source_ref") or str(item)
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
            items[doc_id] = item
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    out = []
    for doc_id, score in ranked:
        item = dict(items[doc_id])
        item["rrf_score"] = score
        out.append(item)
    return out
