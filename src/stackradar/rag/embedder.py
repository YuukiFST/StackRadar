from __future__ import annotations

from collections.abc import Callable
from typing import Any

from stackradar.config.constants import EMBEDDING_MODEL_NAME

_model: Any = None


def get_embedder() -> Any:
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def encode_texts(
    texts: list[str],
    batch_size: int = 32,
    cancellation_check: Callable[[], bool] | None = None,
) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedder()
    import numpy as np

    out: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        if cancellation_check and cancellation_check():
            raise InterruptedError("Operação cancelada pelo usuário.")
        batch = texts[i : i + batch_size]
        emb = model.encode(
            batch,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        out.extend(np.atleast_2d(emb).tolist())
    return out


def encode_query(text: str) -> list[float]:
    vecs = encode_texts([text], batch_size=1)
    return vecs[0] if vecs else []
