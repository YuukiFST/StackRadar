"""Padrões extras (regex) por rótulo da lista de tecnologias."""

from __future__ import annotations

import re

# Chave = rótulo exibido na UI; valores = regex adicionais (case-insensitive).
EXTRA_PATTERNS: dict[str, list[str]] = {
    "Go (Golang)": [r"golang", r"\bgo\b"],
    "Node.js": [r"node\.js", r"\bnode\b"],
    "JavaScript": [r"javascript", r"\bjs\b"],
    "APIs REST": [r"apis?\s+rest", r"\brest\b", r"api\s+rest"],
    "Microsserviços": [r"microsservi[cç]os", r"microservices", r"micro\s*servi[cç]os"],
    "Event Driven": [r"event[\s-]*driven", r"orientad[oa]s?\s+a\s+eventos"],
    "NoSQL": [r"no[\s-]*sql", r"\bnosql\b"],
    "Spring Boot": [r"spring\s*boot", r"\bspring\b"],
    "React": [r"\breact\b", r"reactjs"],
    "GPT": [r"\bgpt\b", r"chatgpt", r"openai"],
    "Gemini": [r"\bgemini\b", r"google\s+gemini"],
    "Claude": [r"\bclaude\b", r"anthropic"],
    "Copilot": [r"copilot", r"github\s+copilot"],
    "Cursor": [r"\bcursor\b"],
}


def regex_patterns_for_label(label: str) -> list[str]:
    """Regex para o rótulo + sinônimos; busca case-insensitive."""
    return [_flexible_label_regex(label), *EXTRA_PATTERNS.get(label, [])]


def _flexible_label_regex(label: str) -> str:
    cleaned = label.replace("(", " ").replace(")", " ")
    parts = [p for p in cleaned.split() if p]
    if not parts:
        return re.escape(label)
    inner = r"\s*".join(re.escape(p) for p in parts)
    return rf"(?i)(?<!\w){inner}(?!\w)"
