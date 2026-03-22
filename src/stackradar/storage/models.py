from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JobRecord:
    id: str
    title: str
    description: str
    url: str
    fetched_at: str
