from __future__ import annotations

import html
from pathlib import Path

from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from stackradar.config.constants import OLLAMA_DEFAULT_BASE_URL, OLLAMA_DEFAULT_MODEL
from stackradar.config.settings import (
    SETTINGS_GROQ_KEY,
    SETTINGS_LLM_BACKEND,
    SETTINGS_OLLAMA_BASE_URL,
    SETTINGS_OLLAMA_MODEL,
    chroma_path,
    data_dir,
    load_tech_list,
)
from stackradar.llm.ollama_client import (
    ollama_list_model_names,
    ollama_runtime_status,
)
from stackradar.ui.workers import ChatOllamaRagWorker


class ChatTab(QWidget):
    def __init__(
        self,
        db_path: Path,
        settings: QSettings,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._settings = settings
        self._db_path = db_path
        self._chroma_path = chroma_path()
        self._data_path = data_dir()

        self._backend = QComboBox()
        self._backend.addItem("Ollama (local)", userData="ollama")
        self._backend.addItem("Groq API", userData="groq")
        stored = self._settings.value(SETTINGS_LLM_BACKEND, "ollama")
        idx = 1 if stored == "groq" else 0
        self._backend.setCurrentIndex(idx)
        self._backend.currentIndexChanged.connect(self._persist_backend)

        self._ollama_url = QLineEdit()
        self._ollama_url.setPlaceholderText(OLLAMA_DEFAULT_BASE_URL)
        saved_url = str(self._settings.value(SETTINGS_OLLAMA_BASE_URL, "") or "").strip()
        self._ollama_url.setText(saved_url)
        self._ollama_url.editingFinished.connect(self._persist_ollama_settings)

        self._ollama_model = QComboBox()
        self._ollama_model.setEditable(True)
        self._ollama_model.setMinimumWidth(220)
        self._ollama_model.currentTextChanged.connect(self._persist_ollama_model)
        self._ollama_model.lineEdit().editingFinished.connect(self._persist_ollama_model)
        _m = str(
            self._settings.value(SETTINGS_OLLAMA_MODEL, OLLAMA_DEFAULT_MODEL)
            or OLLAMA_DEFAULT_MODEL
        )
        self._ollama_model.addItem(_m)

        self._groq_key = QLineEdit()
        self._groq_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._groq_key.setText(str(self._settings.value(SETTINGS_GROQ_KEY, "") or ""))
        self._groq_key.editingFinished.connect(self._persist_groq_key)

        self._ollama_status = QLabel("Ollama: verificando…")

        form = QFormLayout()
        form.setSpacing(8)
        form.setContentsMargins(8, 8, 8, 8)
        form.addRow("Provedor:", self._backend)
        form.addRow("URL do Ollama:", self._ollama_url)
        form.addRow("Modelo Ollama:", self._ollama_model)
        form.addRow("Groq API key:", self._groq_key)
        form.addRow(self._ollama_status)

        opts = QGroupBox("Configurações da Inteligência Artificial")
        opts.setLayout(form)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setAcceptRichText(True)
        self._log.setHtml(
            "<span style='font-size: 11pt; color: #ffffff;'><b>Bem-vindo ao Chat do StackRadar!</b></span><br/><br/>"
            "Com <b style='color:#a78bfa;'>Ollama</b> e vagas no banco, o assistente usa trechos das descrições como contexto. "
            "Se <b style='color:#ffffff;'>chromadb</b> e <b style='color:#ffffff;'>sentence-transformers</b> estiverem instalados "
            "(<code style='color:#ffcc00;'>uv sync --extra rag</code>), "
            "a busca é semântica; caso contrário, usa <b style='color:#ffffff;'>busca por palavras-chave</b> (sem pacotes extras).<br/><br/>"
        )

        self._input = QLineEdit()
        self._input.setPlaceholderText("Faça uma pergunta sobre as vagas monitoradas…")

        self._send_btn = QPushButton("Enviar")
        self._send_btn.setObjectName("PrimaryButton")
        self._send_btn.clicked.connect(self._on_chat_primary_action)
        self._input.returnPressed.connect(self._on_chat_primary_action)

        self._phase = QLabel("")
        self._phase.setVisible(False)
        self._phase.setWordWrap(True)
        self._phase.setStyleSheet(
            "color: #c4b5fd; padding: 6px 4px; font-weight: 600; font-size: 11pt;"
        )

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setTextVisible(False)
        self._progress.setMaximumHeight(5)
        self._progress.setVisible(False)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self._input, stretch=1)
        row.addWidget(self._send_btn)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(opts)
        layout.addWidget(self._log, stretch=1)
        layout.addWidget(self._phase)
        layout.addWidget(self._progress)
        layout.addLayout(row)

        self._chat_worker: ChatOllamaRagWorker | None = None

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_ollama)
        self._timer.start(10_000)
        self._refresh_ollama()

    def _ollama_base_resolved(self) -> str:
        u = self._ollama_url.text().strip()
        return u if u else OLLAMA_DEFAULT_BASE_URL

    def _persist_backend(self) -> None:
        data = self._backend.currentData()
        self._settings.setValue(SETTINGS_LLM_BACKEND, data)

    def _persist_groq_key(self) -> None:
        self._settings.setValue(SETTINGS_GROQ_KEY, self._groq_key.text().strip())

    def _persist_ollama_settings(self) -> None:
        self._settings.setValue(
            SETTINGS_OLLAMA_BASE_URL, self._ollama_url.text().strip()
        )

    def _persist_ollama_model(self) -> None:
        self._settings.setValue(SETTINGS_OLLAMA_MODEL, self._ollama_model.currentText().strip())

    def _refresh_ollama(self) -> None:
        base = self._ollama_base_resolved()
        ok, detail = ollama_runtime_status(base_url=base)
        if ok:
            self._ollama_status.setText(f"Ollama: disponível ({detail})")
            self._ollama_status.setStyleSheet("color: #33ff33;")
            try:
                names = ollama_list_model_names(base_url=base)
                self._repopulate_models(names)
            except Exception:
                pass
        else:
            self._ollama_status.setText(f"Ollama: indisponível ({detail})")
            self._ollama_status.setStyleSheet("color: #ff3333;")

    def _repopulate_models(self, names: list[str]) -> None:
        if not names:
            return
        saved = str(
            self._settings.value(SETTINGS_OLLAMA_MODEL, OLLAMA_DEFAULT_MODEL) or ""
        ).strip()
        self._ollama_model.blockSignals(True)
        self._ollama_model.clear()
        for n in names:
            self._ollama_model.addItem(n)
        pick = saved if saved in names else names[0]
        idx = self._ollama_model.findText(pick)
        if idx >= 0:
            self._ollama_model.setCurrentIndex(idx)
        else:
            self._ollama_model.insertItem(0, pick)
            self._ollama_model.setCurrentIndex(0)
        self._ollama_model.blockSignals(False)

    def _append_html(self, fragment: str) -> None:
        self._log.moveCursor(QTextCursor.MoveOperation.End)
        self._log.insertHtml(fragment)
        self._log.insertHtml("<br/>")
        self._log.moveCursor(QTextCursor.MoveOperation.End)

    def _set_busy(self, busy: bool) -> None:
        self._input.setEnabled(not busy)
        if busy:
            self._send_btn.setText("Cancelar")
            self._send_btn.setEnabled(True)
        else:
            self._send_btn.setText("Enviar")
            self._send_btn.setEnabled(True)

    def _on_chat_primary_action(self) -> None:
        if self._chat_worker is not None and self._chat_worker.isRunning():
            self._chat_worker.force_close_http()
            self._chat_worker.requestInterruption()
            self._phase.setVisible(True)
            self._phase.setText("Cancelando…")
            self._send_btn.setEnabled(False)
            return
        self._submit_chat_message()

    def _submit_chat_message(self) -> None:
        text = self._input.text().strip()
        if not text:
            return

        backend = self._backend.currentData()
        if backend == "groq":
            self._append_html(f"<b>Você:</b> {html.escape(text)}")
            self._input.clear()
            self._append_html(
                "<b>Sistema:</b> Chat com Groq ainda não está integrado nesta versão. "
                "Selecione <b>Ollama (local)</b> para usar RAG."
            )
            return

        model = self._ollama_model.currentText().strip()
        if not model:
            QMessageBox.warning(self, "Modelo", "Escolha ou digite o nome do modelo Ollama.")
            return

        self._append_html(f"<b>Você:</b> {html.escape(text)}")
        self._input.clear()
        self._set_busy(True)
        self._phase.setVisible(True)
        self._progress.setVisible(True)
        self._phase.setText("Preparando contexto e RAG…")

        self._chat_worker = ChatOllamaRagWorker(
            self._db_path,
            self._chroma_path,
            self._data_path,
            model=model,
            base_url=self._ollama_base_resolved(),
            question=text,
            tech_list=load_tech_list(self._settings),
        )
        self._chat_worker.progress.connect(self._on_chat_progress)
        self._chat_worker.reply.connect(self._on_chat_reply)
        self._chat_worker.failed.connect(self._on_chat_failed)
        self._chat_worker.finished.connect(self._on_chat_finished)
        self._chat_worker.start()

    def _on_chat_progress(self, msg: str) -> None:
        self._phase.setText(msg)
        self._ollama_status.setText(f"Ollama: {msg}")
        self._ollama_status.setStyleSheet("color: #a78bfa;")

    def _hide_chat_activity(self) -> None:
        self._phase.setVisible(False)
        self._progress.setVisible(False)
        self._phase.setText("")

    def _on_chat_reply(self, reply: str) -> None:
        self._hide_chat_activity()
        import re
        
        # Limpar tokens especiais (ChatML, Llama3, etc.)
        clean_reply = re.sub(r'<\|.*?\|>', '', reply)
        clean_reply = clean_reply.replace('user', '').strip() if clean_reply.endswith('user') else clean_reply.strip()
        
        parsed = html.escape(clean_reply)
        parsed = re.sub(r'\*\*(.*?)\*\*', r'<b style="color:#ffffff;">\1</b>', parsed)
        parsed = re.sub(r'\*(.*?)\*', r'<i style="color:#dddddd;">\1</i>', parsed)
        parsed = re.sub(r'`(.*?)`', r'<code style="color:#ffcc00;">\1</code>', parsed)
        parsed = parsed.replace('\n', '<br/>')
        
        self._append_html(f"<br/><b style='color:#a78bfa;'>Assistente:</b><br/>{parsed}<br/>")

    def _on_chat_failed(self, msg: str) -> None:
        self._hide_chat_activity()
        if "cancelad" in msg.lower():
            self._append_html(
                f"<br/><i style='color:#a1a1aa;'>{html.escape(msg)}</i><br/>"
            )
        else:
            self._append_html(
                f"<br/><b style='color:#ff3333;'>Erro:</b> {html.escape(msg)}<br/>"
            )

    def _on_chat_finished(self) -> None:
        self._set_busy(False)
        self._hide_chat_activity()
        self._chat_worker = None
        self._refresh_ollama()
