from __future__ import annotations

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from stackradar.config.settings import APP_NAME, APP_ORG
from stackradar.config.settings import db_path as default_db_path
from stackradar.ui.chat_tab import ChatTab
from stackradar.ui.dashboard_tab import DashboardTab
from stackradar.ui.theme import apply_black_theme
from stackradar.config.settings import chroma_path, data_dir
from stackradar.ui.title_bar import TitleBar
from stackradar.ui.workers import FetchJobsWorker, IndexJobsWorker


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("StackRadar")
        self.resize(1100, 720)
        
        # Remove a barra do sistema padrão para usar nossa barra minimalista
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        self._settings = QSettings(APP_ORG, APP_NAME)
        self._db_path = default_db_path()

        # Layout principal com a nossa title bar
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._title_bar = TitleBar(self)
        self._title_bar.minimize_requested.connect(self.showMinimized)
        self._title_bar.maximize_requested.connect(self._toggle_maximize)
        self._title_bar.close_requested.connect(self.close)
        
        lay.addWidget(self._title_bar)

        self._tabs = QTabWidget()
        self._dashboard = DashboardTab(self._db_path, self._settings)
        self._chat = ChatTab(self._db_path, self._settings)
        self._tabs.addTab(self._dashboard, "Dashboard")
        self._tabs.addTab(self._chat, "Chat IA")
        lay.addWidget(self._tabs)

        self.setCentralWidget(container)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        self._fetch_worker: FetchJobsWorker | None = None
        self._index_worker: IndexJobsWorker | None = None

        self._dashboard.fetch_requested.connect(self._start_fetch)

    def _toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _start_fetch(self) -> None:
        if self._fetch_worker and self._fetch_worker.isRunning():
            return
        self._dashboard.set_fetch_enabled(False)
        self._status.showMessage("Coletando vagas…")
        self._fetch_worker = FetchJobsWorker(self._db_path)
        self._fetch_worker.progress.connect(self._status.showMessage)
        self._fetch_worker.finished_ok.connect(self._on_fetch_ok)
        self._fetch_worker.failed.connect(self._on_fetch_failed)
        self._fetch_worker.finished.connect(self._on_fetch_finished_thread)
        self._fetch_worker.start()

    def _on_fetch_ok(self, n: int) -> None:
        self._status.showMessage(f"Concluído: {n} vagas processadas.", 8000)
        self._dashboard.reload_stats()
        self._start_index_jobs()
        QMessageBox.information(
            self,
            "Atualização",
            f"{n} vagas com 'software' no título foram salvas no banco local.",
        )

    def _on_fetch_failed(self, msg: str) -> None:
        self._status.showMessage("Falha na coleta.", 8000)
        QMessageBox.critical(self, "Erro na coleta", msg)

    def _on_fetch_finished_thread(self) -> None:
        self._dashboard.set_fetch_enabled(True)
        self._fetch_worker = None

    def _start_index_jobs(self) -> None:
        if self._index_worker and self._index_worker.isRunning():
            return
        self._index_worker = IndexJobsWorker(
            self._db_path, chroma_path(), data_dir()
        )
        self._index_worker.progress.connect(self._status.showMessage)
        self._index_worker.finished_ok.connect(self._on_index_ok)
        self._index_worker.failed.connect(self._on_index_failed)
        self._index_worker.finished.connect(self._on_index_finished)
        self._index_worker.start()

    def _on_index_ok(self, n_chunks: int) -> None:
        self._status.showMessage(
            f"Índice RAG atualizado ({n_chunks} trechos).", 10000
        )

    def _on_index_failed(self, msg: str) -> None:
        self._status.showMessage("Falha ao indexar para o chat.", 10000)
        QMessageBox.warning(
            self,
            "Indexação RAG",
            f"Não foi possível atualizar o Chroma:\n{msg}\n\n"
            "O chat ainda pode tentar indexar ao enviar a primeira pergunta.",
        )

    def _on_index_finished(self) -> None:
        self._index_worker = None
