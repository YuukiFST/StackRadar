from __future__ import annotations

from pathlib import Path
from typing import Any

from stackradar.config.constants import RAG_TOP_K


def retrieve_contexts(
    chroma_path: Path,
    query: str,
    k: int = RAG_TOP_K,
) -> list[dict[str, Any]]:
    """Retorna trechos relevantes via Chroma + embeddings (requer chromadb + ST)."""
    from stackradar.rag.chroma_store import get_collection
    from stackradar.rag.embedder import encode_query

    if not query.strip():
        return []
    coll = get_collection(chroma_path)
    n = int(coll.count())
    if n == 0:
        return []
    qemb = encode_query(query)
    take = min(k, n)
    res = coll.query(
        query_embeddings=[qemb],
        n_results=take,
        include=["documents", "metadatas", "distances"],
    )
    out: list[dict[str, Any]] = []
    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        if not doc:
            continue
        m = meta or {}
        out.append(
            {
                "text": doc,
                "job_id": str(m.get("job_id", "")),
                "title": str(m.get("title", "")),
                "url": str(m.get("url", "")),
                "distance": float(dist) if dist is not None else None,
            }
        )
    return out
