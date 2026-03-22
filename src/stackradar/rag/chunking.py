from __future__ import annotations

from stackradar.config.constants import CHUNK_OVERLAP, CHUNK_SIZE
from stackradar.storage.models import JobRecord


def chunk_job_record(job: JobRecord) -> list[str]:
    """Divide título + descrição em blocos para embedding."""
    title = (job.title or "").strip()
    desc = (job.description or "").strip()
    body = f"{title}\n\n{desc}".strip() if desc else title
    if not body:
        return []
    if len(body) <= CHUNK_SIZE:
        return [body]
    chunks: list[str] = []
    start = 0
    while start < len(body):
        end = min(start + CHUNK_SIZE, len(body))
        chunks.append(body[start:end])
        if end >= len(body):
            break
        start = end - CHUNK_OVERLAP
        if start < 0:
            start = 0
    return chunks
