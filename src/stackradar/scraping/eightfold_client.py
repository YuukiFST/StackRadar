"""Cliente HTTP para a API pública pcsx do Eightfold (Mercado Libre)."""

from __future__ import annotations

from typing import Any, Callable, Iterator

import httpx

from stackradar.config.constants import (
    DEFAULT_SEARCH_QUERY,
    EIGHTFOLD_API_HOST,
    EIGHTFOLD_BUSINESS_DOMAIN,
    TITLE_MUST_CONTAIN,
)
from stackradar.scraping.normalize import strip_html

SearchProgress = Callable[[str], None]


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "User-Agent": "StackRadar/0.1 (+https://github.com; job research)",
        "Referer": f"https://{EIGHTFOLD_API_HOST}/careers",
    }


def _search_url() -> str:
    return f"https://{EIGHTFOLD_API_HOST}/api/pcsx/search"


def _details_url() -> str:
    return f"https://{EIGHTFOLD_API_HOST}/api/pcsx/position_details"


def fetch_search_page(client: httpx.Client, start: int) -> dict[str, Any]:
    params = {
        "domain": EIGHTFOLD_BUSINESS_DOMAIN,
        "query": DEFAULT_SEARCH_QUERY,
        "location": "",
        "start": str(start),
    }
    r = client.get(_search_url(), params=params, headers=_headers())
    r.raise_for_status()
    body = r.json()
    if not isinstance(body, dict):
        return {}
    data = body.get("data")
    return data if isinstance(data, dict) else {}


def iter_search_positions(client: httpx.Client) -> Iterator[dict[str, Any]]:
    start = 0
    while True:
        data = fetch_search_page(client, start)
        positions = data.get("positions") or []
        if not isinstance(positions, list) or not positions:
            break
        total = int(data.get("count") or 0)
        for p in positions:
            if isinstance(p, dict):
                yield p
        start += len(positions)
        if total and start >= total:
            break
        if len(positions) < 10:
            break


def title_passes_filter(title: str) -> bool:
    return TITLE_MUST_CONTAIN in title.casefold()


def fetch_position_details(
    client: httpx.Client, position_id: int, hl: str = "es"
) -> dict[str, Any]:
    params = {
        "position_id": str(position_id),
        "domain": EIGHTFOLD_BUSINESS_DOMAIN,
        "hl": hl,
    }
    r = client.get(_details_url(), params=params, headers=_headers())
    r.raise_for_status()
    body = r.json()
    if not isinstance(body, dict):
        return {}
    data = body.get("data")
    return data if isinstance(data, dict) else {}


def collect_jobs_with_details(
    client: httpx.Client,
    on_progress: SearchProgress | None = None,
) -> list[dict[str, Any]]:
    """Lista de dicts com chaves estáveis: id, title, description_plain, url."""
    results: list[dict[str, Any]] = []
    for summary in iter_search_positions(client):
        raw_id = summary.get("id")
        if raw_id is None:
            continue
        try:
            pid = int(raw_id)
        except (TypeError, ValueError):
            continue
        name = str(summary.get("name") or "").strip()
        if not title_passes_filter(name):
            continue
        if on_progress:
            on_progress(f"Detalhes da vaga {pid} ({name[:40]}…)")

        try:
            detail = fetch_position_details(client, pid)
        except httpx.HTTPError:
            detail = {}

        title = str(detail.get("name") or name).strip()
        if not title_passes_filter(title):
            continue

        jd = detail.get("jobDescription") or ""
        description = strip_html(str(jd)) if jd else ""
        url = str(detail.get("publicUrl") or "").strip()
        if not url:
            rel = str(detail.get("positionUrl") or summary.get("positionUrl") or "")
            if rel.startswith("/"):
                url = f"https://{EIGHTFOLD_API_HOST}{rel}"
            elif rel.startswith("http"):
                url = rel

        results.append(
            {
                "id": str(pid),
                "title": title,
                "description": description,
                "url": url,
            }
        )
    return results
