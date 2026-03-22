"""Caminhos de dados e preferências (QSettings)."""

from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import QSettings

from stackradar.config.constants import DEFAULT_TECH_LIST

APP_ORG = "StackRadar"
APP_NAME = "StackRadar"
SETTINGS_TECH_LIST_KEY = "tech_list_json"
SETTINGS_GROQ_KEY = "groq_api_key"
SETTINGS_LLM_BACKEND = "llm_backend"
SETTINGS_OLLAMA_MODEL = "ollama_model"
SETTINGS_OLLAMA_BASE_URL = "ollama_base_url"


def data_dir() -> Path:
    base = Path.home() / ".stackradar"
    base.mkdir(parents=True, exist_ok=True)
    return base


def db_path() -> Path:
    return data_dir() / "vagas.db"


def chroma_path() -> Path:
    p = data_dir() / "chroma"
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_tech_list(settings: QSettings) -> list[str]:
    raw = settings.value(SETTINGS_TECH_LIST_KEY)
    if not raw or not isinstance(raw, str):
        return list(DEFAULT_TECH_LIST)
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
            return parsed
    except json.JSONDecodeError:
        pass
    return list(DEFAULT_TECH_LIST)


def save_tech_list(settings: QSettings, items: list[str]) -> None:
    settings.setValue(SETTINGS_TECH_LIST_KEY, json.dumps(items, ensure_ascii=False))
