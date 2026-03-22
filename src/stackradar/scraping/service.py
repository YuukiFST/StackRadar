from __future__ import annotations

import httpx

from stackradar.scraping.eightfold_client import SearchProgress, collect_jobs_with_details
from stackradar.storage.database import JobRepository, utc_now_iso
from stackradar.storage.models import JobRecord


def fetch_and_persist_jobs(
    repo: JobRepository,
    on_progress: SearchProgress | None = None,
) -> int:
    """Coleta vagas (título com 'software'), grava SQLite e atualiza last_fetch_at."""
    with httpx.Client(timeout=90.0, follow_redirects=True) as client:
        raw = collect_jobs_with_details(client, on_progress=on_progress)

    ts = utc_now_iso()
    for item in raw:
        job = JobRecord(
            id=item["id"],
            title=item["title"],
            description=item.get("description") or "",
            url=item.get("url") or "",
            fetched_at=ts,
        )
        repo.upsert_job(job)

    repo.set_meta("last_fetch_at", ts)
    return len(raw)
