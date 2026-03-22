from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from stackradar.rag.chunking import chunk_job_record
from stackradar.storage.database import JobRepository, init_db

_SMALL_TALK = frozenset(
    {
        "oi",
        "olá",
        "ola",
        "hey",
        "hi",
        "hello",
        "eae",
        "opa",
        "bom",
        "boa",
        "valeu",
        "obrigado",
        "obrigada",
        "thanks",
    }
)


def is_small_talk(query: str) -> bool:
    t = query.strip().lower()
    if not t:
        return True
    if len(t) <= 3:
        return True
    words = t.split()
    if len(words) <= 3 and all(w in _SMALL_TALK or len(w) <= 3 for w in words):
        return True
    if t in _SMALL_TALK:
        return True
    return False


_STOP = frozenset(
    """
    a o os as de da do das dos em um uma uns unas e é que por para com sem se
    na no nas nos ao aos à às pelo pela pelos pelas como mas ou seja the of to in
    is are was were be been being an and or for on at from with into
    """.split()
)


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[\w#+.]+", text.lower(), flags=re.UNICODE)
    return {w for w in words if len(w) > 2 and w not in _STOP}


def retrieve_diverse_contexts(db_path: Path, k: int = 10) -> list[dict[str, Any]]:
    """Um trecho por vaga (ordem do banco), para saudações ou fallback sem keywords."""
    init_db(db_path)
    repo = JobRepository(db_path)
    out: list[dict[str, Any]] = []
    for job in repo.iter_jobs():
        if len(out) >= k:
            break
        chunks = chunk_job_record(job)
        if not chunks:
            continue
        chunk = chunks[0]
        out.append(
            {
                "text": chunk[:4000],
                "job_id": job.id,
                "title": job.title,
                "url": job.url,
                "distance": None,
            }
        )
    return out


def retrieve_keyword_contexts(
    db_path: Path,
    query: str,
    k: int = 8,
) -> list[dict[str, Any]]:
    """
    RAG leve: pontua trechos por sobreposição de tokens com a pergunta.
    Não exige chromadb nem sentence-transformers (útil no Python 3.14 / Windows).
    """
    if not query.strip():
        return []
    init_db(db_path)
    repo = JobRepository(db_path)
    qw = _tokens(query)
    if not qw:
        return retrieve_diverse_contexts(db_path, k=k)

    scored: list[tuple[int, str, str, str, str]] = []
    for job in repo.iter_jobs():
        title_l = job.title.lower()
        for chunk in chunk_job_record(job):
            blob = chunk.lower()
            sc = sum(1 for w in qw if w in blob)
            sc += sum(2 for w in qw if w in title_l)
            if sc > 0:
                scored.append((sc, chunk, job.id, job.title, job.url))

    scored.sort(key=lambda x: -x[0])
    out: list[dict[str, Any]] = []
    for sc, chunk, jid, title, url in scored[:k]:
        out.append(
            {
                "text": chunk[:4000],
                "job_id": jid,
                "title": title,
                "url": url,
                "distance": None,
            }
        )
    return out
