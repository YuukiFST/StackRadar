from __future__ import annotations

from stackradar.analytics.tech_counter import count_technologies_in_jobs
from stackradar.storage.models import JobRecord


def build_tech_aggregate_text(
    jobs: list[JobRecord],
    tech_list: list[str],
) -> str:
    """
    Mesma métrica do gráfico do Dashboard: por vaga, cada tecnologia conta no máx. 1 vez.
    """
    if not jobs or not tech_list:
        return ""
    counts = count_technologies_in_jobs(jobs, tech_list)
    ranked = [(t, c) for t, c in counts.items() if c > 0]
    ranked.sort(key=lambda x: -x[1])
    if not ranked:
        return ""
    lines = [
        f"{i + 1}. {name}: {n} vagas (≥1 menção no título ou descrição)"
        for i, (name, n) in enumerate(ranked)
    ]
    return (
        "=== Frequência de tecnologias (TODAS as vagas no banco; mesma regra do gráfico) ===\n"
        + "\n".join(lines)
    )
