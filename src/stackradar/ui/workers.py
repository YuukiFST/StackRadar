from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from stackradar.llm.http_stream_handle import HttpStreamHandle
from stackradar.scraping.service import fetch_and_persist_jobs
from stackradar.storage.database import JobRepository, init_db


def _merge_contexts(primary: list, extra: list, cap: int = 14) -> list:
    seen: set[tuple[str, str]] = set()
    out: list[Any] = []
    for c in primary + extra:
        jid = str(c.get("job_id", ""))
        t = (c.get("text") or "")[:240]
        key = (jid, t)
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
        if len(out) >= cap:
            break
    return out


class FetchJobsWorker(QThread):
    finished_ok = pyqtSignal(int)
    failed = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, db_path: Path, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._db_path = db_path

    def run(self) -> None:
        try:
            init_db(self._db_path)
            repo = JobRepository(self._db_path)

            def on_progress(msg: str) -> None:
                self.progress.emit(msg)

            n = fetch_and_persist_jobs(repo, on_progress=on_progress)
            self.finished_ok.emit(n)
        except Exception as e:
            self.failed.emit(str(e))


class IndexJobsWorker(QThread):
    """Reconstrói o índice Chroma após nova coleta (opcional se chromadb instalado)."""

    finished_ok = pyqtSignal(int)
    failed = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(
        self,
        db_path: Path,
        chroma_path: Path,
        data_dir: Path,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._chroma_path = chroma_path
        self._data_dir = data_dir

    def run(self) -> None:
        try:
            from stackradar.rag.chroma_store import rebuild_index

            def on_progress(msg: str) -> None:
                self.progress.emit(msg)

            n = rebuild_index(
                self._db_path,
                self._chroma_path,
                self._data_dir,
                on_progress=on_progress,
                cancellation_check=self.isInterruptionRequested,
            )
            self.finished_ok.emit(n)
        except InterruptedError:
            self.progress.emit("Indexação cancelada.")
            self.finished_ok.emit(0)
        except ImportError:
            self.progress.emit(
                "Chroma não instalado — chat usará busca por palavras-chave."
            )
            self.finished_ok.emit(0)
        except Exception as e:
            self.failed.emit(str(e))


class ChatOllamaRagWorker(QThread):
    """RAG + Ollama. Agregado de tecnologias + trechos; Chroma opcional."""

    reply = pyqtSignal(str)
    failed = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(
        self,
        db_path: Path,
        chroma_path: Path,
        data_dir: Path,
        model: str,
        base_url: str,
        question: str,
        tech_list: list[str],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._chroma_path = chroma_path
        self._data_dir = data_dir
        self._model = model.strip()
        self._base_url = base_url.strip() or "http://127.0.0.1:11434"
        self._question = question.strip()
        self._tech_list = list(tech_list)
        self._http_stream = HttpStreamHandle()

    def force_close_http(self) -> None:
        self._http_stream.force_close()

    def _cancel(self) -> None:
        if self.isInterruptionRequested():
            raise InterruptedError("Operação cancelada pelo usuário.")

    def run(self) -> None:
        try:
            from stackradar.llm.ollama_client import ollama_chat
            from stackradar.llm.prompts import SYSTEM_RAG, build_rag_user_content
            from stackradar.rag.aggregate_context import build_tech_aggregate_text
            from stackradar.rag.keyword_retrieve import (
                is_small_talk,
                retrieve_diverse_contexts,
                retrieve_keyword_contexts,
            )
            from stackradar.storage.database import JobRepository, init_db

            init_db(self._db_path)
            self._cancel()
            repo = JobRepository(self._db_path)
            jobs = repo.iter_jobs()
            if not jobs:
                self.failed.emit(
                    "Não há vagas no banco. Use o Dashboard para atualizar as vagas primeiro."
                )
                return

            aggregate = (
                build_tech_aggregate_text(jobs, self._tech_list)
                if self._tech_list
                else ""
            )

            ctx: list = []
            try:
                from stackradar.rag.chroma_store import ensure_index
                from stackradar.rag.retriever import retrieve_contexts

                self.progress.emit("Sincronizando índice RAG (Chroma)…")
                self._cancel()
                ensure_index(
                    self._db_path,
                    self._chroma_path,
                    self._data_dir,
                    on_progress=self.progress.emit,
                    cancellation_check=self.isInterruptionRequested,
                )
                self._cancel()
                self.progress.emit("Buscando trechos (embeddings)…")
                ctx = retrieve_contexts(self._chroma_path, self._question)
            except ImportError:
                pass
            except Exception as e:
                self.progress.emit(f"Chroma indisponível ({e}); usando busca por texto…")

            self._cancel()
            if not ctx:
                self.progress.emit("Selecionando trechos (busca por palavras-chave)…")
                ctx = retrieve_keyword_contexts(self._db_path, self._question)

            diverse = retrieve_diverse_contexts(self._db_path, k=12)
            if is_small_talk(self._question):
                ctx = _merge_contexts(diverse, ctx, cap=12)
            elif len(ctx) < 6:
                ctx = _merge_contexts(ctx, diverse, cap=14)

            if not ctx:
                ctx = diverse

            if not ctx:
                self.failed.emit("Não foi possível montar contexto a partir das vagas.")
                return

            self._cancel()
            self.progress.emit(
                "Aguardando o Ollama gerar a resposta (modelos grandes podem levar vários minutos)…"
            )
            user_content = build_rag_user_content(
                self._question,
                ctx,
                aggregate_block=aggregate or None,
            )
            messages = [
                {"role": "system", "content": SYSTEM_RAG},
                {"role": "user", "content": user_content},
            ]
            text = ollama_chat(
                self._model,
                messages,
                base_url=self._base_url,
                timeout=600.0,
                cancellation_check=self.isInterruptionRequested,
                http_stream_handle=self._http_stream,
            )
            self.reply.emit(text)
        except InterruptedError as e:
            self.failed.emit(str(e))
        except Exception as e:
            self.failed.emit(str(e))

