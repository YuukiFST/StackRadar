"""Permite fechar o stream HTTP a partir de outra thread (ex.: botão Cancelar na UI)."""

from __future__ import annotations

import threading
from typing import Any


class HttpStreamHandle:
    """Referência thread-safe ao `httpx.Response` do stream ativo; `force_close()` interrompe leituras bloqueadas."""

    __slots__ = ("_lock", "_response")

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._response: Any = None

    def attach(self, response: Any) -> None:
        with self._lock:
            self._response = response

    def detach(self) -> None:
        with self._lock:
            self._response = None

    def force_close(self) -> None:
        with self._lock:
            r = self._response
        if r is not None:
            try:
                r.close()
            except Exception:
                pass
