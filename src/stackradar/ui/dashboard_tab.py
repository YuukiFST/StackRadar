from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from stackradar.analytics.tech_counter import count_technologies_in_jobs
from stackradar.config.constants import DEFAULT_TECH_LIST
from stackradar.config.settings import load_tech_list, save_tech_list
from stackradar.storage.database import JobRepository, init_db
from stackradar.ui.chart_widget import TechBarChartWidget


class DashboardTab(QWidget):
    fetch_requested = pyqtSignal()

    def __init__(self, db_path: Path, settings: QSettings, parent: QWidget | None = None):
        super().__init__(parent)
        self._db_path = db_path
        self._settings = settings

        # Stat cards minimalistas
        total_card, self._status_total = self._make_stat_card("Vagas no banco")
        updated_card, self._status_updated = self._make_stat_card("Última atualização")

        stat_row = QHBoxLayout()
        stat_row.setSpacing(8)
        stat_row.addWidget(total_card, stretch=1)
        stat_row.addWidget(updated_card, stretch=1)

        self._refresh_btn = QPushButton("Atualizar vagas")
        self._refresh_btn.setObjectName("PrimaryButton")
        self._refresh_btn.clicked.connect(self.fetch_requested.emit)

        top_layout = QVBoxLayout()
        top_layout.setSpacing(12)
        top_layout.addLayout(stat_row)

        btn_lay = QHBoxLayout()
        btn_lay.addWidget(self._refresh_btn)
        btn_lay.addStretch()
        top_layout.addLayout(btn_lay)

        self._tech_list = QListWidget()
        self._load_tech_list_widget()

        add_btn = QPushButton("Adicionar tecnologia")
        add_btn.clicked.connect(self._add_tech)
        rm_btn = QPushButton("Remover selecionada")
        rm_btn.clicked.connect(self._remove_tech)
        reset_btn = QPushButton("Restaurar padrão")
        reset_btn.clicked.connect(self._reset_techs)
        save_btn = QPushButton("Aplicar lista ao gráfico")
        save_btn.clicked.connect(self._save_techs_and_refresh)

        tech_row = QHBoxLayout()
        tech_row.setSpacing(8)
        tech_row.addWidget(self._tech_list, stretch=1)
        
        btns = QVBoxLayout()
        btns.setSpacing(8)
        
        for b in (add_btn, rm_btn, reset_btn, save_btn):
            b.setMinimumHeight(28)
            btns.addWidget(b)
            
        btns.addStretch()
        tech_row.addLayout(btns)

        self._chart = TechBarChartWidget()

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)
        
        layout.addLayout(top_layout)
        
        content_row = QHBoxLayout()
        content_row.setSpacing(12)
        
        left_panel = QVBoxLayout()
        left_panel.setSpacing(4)
        list_lbl = QLabel("Tecnologias monitoradas")
        left_panel.addWidget(list_lbl)
        left_panel.addLayout(tech_row)
        
        content_row.addLayout(left_panel, stretch=1)
        content_row.addWidget(self._chart, stretch=2)
        
        layout.addLayout(content_row, stretch=1)

        self.reload_stats()

    def _make_stat_card(self, label: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("StatCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(4)
        lb = QLabel(label)
        lb.setObjectName("StatLabel")
        val = QLabel("—")
        val.setObjectName("StatValue")
        v.addWidget(lb)
        v.addWidget(val)
        return card, val

    def _load_tech_list_widget(self) -> None:
        self._tech_list.clear()
        for t in load_tech_list(self._settings):
            self._tech_list.addItem(t)

    def _add_tech(self) -> None:
        text, ok = QInputDialog.getText(self, "Nova tecnologia", "Nome:")
        if ok and text.strip():
            self._tech_list.addItem(text.strip())

    def _remove_tech(self) -> None:
        row = self._tech_list.currentRow()
        if row >= 0:
            self._tech_list.takeItem(row)

    def _reset_techs(self) -> None:
        self._tech_list.clear()
        for t in DEFAULT_TECH_LIST:
            self._tech_list.addItem(t)

    def _save_techs_and_refresh(self) -> None:
        items = [self._tech_list.item(i).text() for i in range(self._tech_list.count())]
        if not items:
            QMessageBox.warning(self, "Lista vazia", "Adicione ao menos uma tecnologia.")
            return
        save_tech_list(self._settings, items)
        self.reload_stats()

    def reload_stats(self) -> None:
        init_db(self._db_path)
        repo = JobRepository(self._db_path)
        n = repo.count_jobs()
        last = repo.get_meta("last_fetch_at")
        self._status_total.setText(str(n))
        
        last_str = "—"
        if last:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last)
                last_str = dt.strftime("%d/%m/%Y %H:%M:%S")
            except Exception:
                last_str = str(last)
                
        self._status_updated.setText(last_str)
        jobs = repo.iter_jobs()
        techs = load_tech_list(self._settings)
        counts = count_technologies_in_jobs(jobs, techs)
        self._chart.plot_counts(counts, title="Top Tecnologias")

    def set_fetch_enabled(self, enabled: bool) -> None:
        self._refresh_btn.setEnabled(enabled)

