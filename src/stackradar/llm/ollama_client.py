from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx

from stackradar.llm.http_stream_handle import HttpStreamHandle


def _base(base_url: str) -> str:
    return base_url.rstrip("/")


def ollama_runtime_status(
    base_url: str = "http://127.0.0.1:11434", timeout: float = 2.0
) -> tuple[bool, str]:
    """Retorna (ok, mensagem curta). Usa /api/tags na porta padrão."""
    try:
        r = httpx.get(f"{_base(base_url)}/api/tags", timeout=timeout)
        r.raise_for_status()
        data = r.json()
        models = data.get("models") if isinstance(data, dict) else None
        n = len(models) if isinstance(models, list) else 0
        return True, f"{n} modelo(s)"
    except httpx.HTTPError as e:
        return False, str(e)[:120]
    except Exception as e:
        return False, str(e)[:120]


def ollama_list_model_names(
    base_url: str = "http://127.0.0.1:11434", timeout: float = 5.0
) -> list[str]:
    r = httpx.get(f"{_base(base_url)}/api/tags", timeout=timeout)
    r.raise_for_status()
    data = r.json()
    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, list):
        return []
    names: list[str] = []
    for m in models:
        if isinstance(m, dict) and m.get("name"):
            names.append(str(m["name"]))
    return names


def ollama_chat(
    model: str,
    messages: list[dict[str, Any]],
    base_url: str = "http://127.0.0.1:11434",
    timeout: float = 300.0,
    cancellation_check: Callable[[], bool] | None = None,
    http_stream_handle: HttpStreamHandle | None = None,
) -> str:
    """
    POST /api/chat com stream=true. `http_stream_handle.force_close()` (outra thread)
    encerra o socket e costuma desbloquear `iter_lines` na hora.
    """
    if cancellation_check and cancellation_check():
        raise InterruptedError("Operação cancelada pelo usuário.")

    url = f"{_base(base_url)}/api/chat"
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    parts: list[str] = []

    with httpx.Client(timeout=timeout) as client:
        with client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            if http_stream_handle is not None:
                http_stream_handle.attach(response)
            try:
                try:
                    for line in response.iter_lines():
                        if cancellation_check and cancellation_check():
                            raise InterruptedError(
                                "Operação cancelada pelo usuário."
                            )
                        line = (line or "").strip()
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if data.get("done"):
                            break
                        msg = data.get("message")
                        if isinstance(msg, dict):
                            piece = msg.get("content")
                            if piece:
                                parts.append(str(piece))
                except Exception as e:
                    if cancellation_check and cancellation_check():
                        raise InterruptedError(
                            "Operação cancelada pelo usuário."
                        ) from e
                    raise
            finally:
                if http_stream_handle is not None:
                    http_stream_handle.detach()

    text = "".join(parts).strip()
    if text:
        return text

    if cancellation_check and cancellation_check():
        raise InterruptedError("Operação cancelada pelo usuário.")

    return _ollama_chat_non_streaming(model, messages, base_url, timeout)


def _ollama_chat_non_streaming(
    model: str,
    messages: list[dict[str, Any]],
    base_url: str,
    timeout: float,
) -> str:
    url = f"{_base(base_url)}/api/chat"
    payload = {"model": model, "messages": messages, "stream": False}
    r = httpx.post(url, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        return str(data)
    msg = data.get("message")
    if isinstance(msg, dict) and msg.get("content"):
        return str(msg["content"]).strip()
    if data.get("response"):
        return str(data["response"]).strip()
    return str(data)
