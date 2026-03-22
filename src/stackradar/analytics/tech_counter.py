from __future__ import annotations

import re

from stackradar.analytics.synonyms import regex_patterns_for_label
from stackradar.storage.models import JobRecord


def _compile_tech_patterns(tech_list: list[str]) -> dict[str, list[re.Pattern[str]]]:
    out: dict[str, list[re.Pattern[str]]] = {}
    for tech in tech_list:
        pats: list[re.Pattern[str]] = []
        for src in regex_patterns_for_label(tech):
            try:
                pats.append(re.compile(src, re.IGNORECASE))
            except re.error:
                continue
        out[tech] = pats
    return out


def job_matches_tech(text: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(p.search(text) for p in patterns)


def count_technologies_in_jobs(
    jobs: list[JobRecord], tech_list: list[str]
) -> dict[str, int]:
    compiled = _compile_tech_patterns(tech_list)
    counts = {t: 0 for t in tech_list}
    for job in jobs:
        blob = f"{job.title}\n{job.description}"
        matched: set[str] = set()
        for tech, pats in compiled.items():
            if not pats:
                continue
            if job_matches_tech(blob, pats):
                matched.add(tech)
        for tech in matched:
            counts[tech] += 1
    return counts
