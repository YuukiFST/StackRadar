from __future__ import annotations

from typing import Any

SYSTEM_RAG = """Você é o assistente do StackRadar. Responda em português com clareza.

Regras:
- Se a mensagem do usuário incluir a seção "Frequência de tecnologias", ela foi calculada sobre **todas** as vagas no banco (igual ao gráfico do app). Para perguntas sobre ranking, "top N", "mais usada" ou frequência de linguagens/frameworks, **use essa seção como fonte principal** e não a contradiga com base só em trechos parciais.
- Os trechos de vagas são complementares (ex.: exemplos, requisitos textuais).
- Se faltar a seção agregada e a resposta não estiver nos trechos, diga que não há dados suficientes.
- Cite títulos de vagas ou IDs quando ajudar.
- Seja objetivo; use listas curtas quando fizer sentido.
"""


def build_rag_user_content(
    question: str,
    contexts: list[dict[str, Any]],
    aggregate_block: str | None = None,
) -> str:
    blocks: list[str] = [f"Pergunta do usuário:\n{question.strip()}", ""]

    if aggregate_block and aggregate_block.strip():
        blocks.append(aggregate_block.strip())
        blocks.append("")

    blocks.append("Trechos das vagas (amostra):")
    for i, ctx in enumerate(contexts, 1):
        title = ctx.get("title") or "(sem título)"
        jid = ctx.get("job_id") or "?"
        url = ctx.get("url") or ""
        text = (ctx.get("text") or "").strip()
        line = f"\n--- Trecho {i} | Vaga: {title} | id={jid}"
        if url:
            line += f" | {url}"
        line += f"\n{text}\n"
        blocks.append(line)
    return "\n".join(blocks)
