from __future__ import annotations

import json
from pathlib import Path


def meta_path(data_dir: Path) -> Path:
    return data_dir / "rag_index_meta.json"


def read_job_count(data_dir: Path) -> int | None:
    p = meta_path(data_dir)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        n = data.get("sqlite_job_count")
        return int(n) if n is not None else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def write_job_count(data_dir: Path, count: int) -> None:
    p = meta_path(data_dir)
    p.write_text(
        json.dumps({"sqlite_job_count": count}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
