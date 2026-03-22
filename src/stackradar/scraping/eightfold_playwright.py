"""Fallback Playwright se a API pcsx deixar de responder (esqueleto)."""

from __future__ import annotations

from typing import Any, Callable

SearchProgress = Callable[[str], None]


def fetch_jobs_via_browser(
    on_progress: SearchProgress | None = None,
) -> list[dict[str, Any]]:
    raise NotImplementedError(
        "Implemente captura via Playwright se /api/pcsx/search deixar de funcionar."
    )
