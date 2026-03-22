from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from stackradar.config.constants import CHROMA_COLLECTION
from stackradar.rag.chunking import chunk_job_record
from stackradar.rag.index_meta import read_job_count, write_job_count
from stackradar.storage.database import JobRepository, init_db

if TYPE_CHECKING:
    pass


def _chromadb() -> Any:
    try:
        import chromadb
    except ImportError as e:
        raise ImportError(
            "Pacote 'chromadb' não encontrado. Instale com:\n"
            "  pip install \"chromadb>=0.5.13,<0.6\"\n"
            "Recomenda-se Python 3.11 ou 3.12 no Windows (há wheels prontos)."
        ) from e
    return chromadb


def _client(persist_dir: Path) -> Any:
    persist_dir.mkdir(parents=True, exist_ok=True)
    return _chromadb().PersistentClient(path=str(persist_dir))


def get_collection(persist_dir: Path) -> Any:
    client = _client(persist_dir)
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def delete_collection_if_exists(persist_dir: Path) -> None:
    try:
        client = _client(persist_dir)
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass


def rebuild_index(
    db_path: Path,
    chroma_path: Path,
    data_dir: Path,
    on_progress: Callable[[str], None] | None = None,
    cancellation_check: Callable[[], bool] | None = None,
) -> int:
    """Recria o índice Chroma a partir do SQLite. Retorna número de chunks."""
    from stackradar.rag.embedder import encode_texts

    init_db(db_path)
    repo = JobRepository(db_path)
    jobs = repo.iter_jobs()
    n_jobs = len(jobs)

    delete_collection_if_exists(chroma_path)

    if n_jobs == 0:
        write_job_count(data_dir, 0)
        return 0

    coll = get_collection(chroma_path)

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for job in jobs:
        if cancellation_check and cancellation_check():
            raise InterruptedError("Operação cancelada pelo usuário.")
        chunks = chunk_job_record(job)
        if not chunks:
            continue
        for i, chunk in enumerate(chunks):
            ids.append(f"{job.id}_{i}")
            documents.append(chunk)
            metadatas.append(
                {
                    "job_id": str(job.id),
                    "title": job.title[:500],
                    "url": job.url[:500],
                    "chunk_index": int(i),
                }
            )

    if not ids:
        write_job_count(data_dir, repo.count_jobs())
        return 0

    if on_progress:
        on_progress(f"Gerando embeddings ({len(documents)} trechos)…")

    embeddings = encode_texts(
        documents, batch_size=32, cancellation_check=cancellation_check
    )

    batch = 128
    for i in range(0, len(ids), batch):
        if cancellation_check and cancellation_check():
            raise InterruptedError("Operação cancelada pelo usuário.")
        if on_progress:
            on_progress(f"Gravando no Chroma {i + 1}–{min(i + batch, len(ids))}…")
        coll.upsert(
            ids=ids[i : i + batch],
            embeddings=embeddings[i : i + batch],
            documents=documents[i : i + batch],
            metadatas=metadatas[i : i + batch],
        )

    write_job_count(data_dir, repo.count_jobs())
    return len(ids)


def collection_chunk_count(persist_dir: Path) -> int:
    try:
        coll = get_collection(persist_dir)
        return int(coll.count())
    except Exception:
        return 0


def needs_reindex(db_path: Path, chroma_path: Path, data_dir: Path) -> bool:
    init_db(db_path)
    n = JobRepository(db_path).count_jobs()
    if n == 0:
        return collection_chunk_count(chroma_path) > 0

    meta_n = read_job_count(data_dir)
    chunks = collection_chunk_count(chroma_path)
    if chunks == 0:
        return True
    if meta_n is None or meta_n != n:
        return True
    return False


def ensure_index(
    db_path: Path,
    chroma_path: Path,
    data_dir: Path,
    on_progress: Callable[[str], None] | None = None,
    cancellation_check: Callable[[], bool] | None = None,
) -> None:
    if needs_reindex(db_path, chroma_path, data_dir):
        rebuild_index(
            db_path,
            chroma_path,
            data_dir,
            on_progress=on_progress,
            cancellation_check=cancellation_check,
        )
