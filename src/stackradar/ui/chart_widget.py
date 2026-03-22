from __future__ import annotations

import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QSizePolicy, QWidget

from stackradar.ui import theme
from stackradar.ui.fonts import configure_matplotlib_font, matplotlib_font_candidates

class TechBarChartWidget(QWidget):
    """Gráfico de barras estritamente preto e hacker/matrix."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        configure_matplotlib_font()
        mpl.rcParams["font.family"] = matplotlib_font_candidates()

        self._figure = Figure(figsize=(5, 4), layout="constrained", facecolor=theme.BG)
        self._canvas = FigureCanvasQTAgg(self._figure)
        self._canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        from PyQt6.QtWidgets import QVBoxLayout

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._canvas)
        self._ax = self._figure.add_subplot(111)

    def plot_counts(self, counts: dict[str, int], title: str = "") -> None:
        self._ax.clear()

        # Fundo do gráfico (axes) idêntico ao painel preto
        self._ax.set_facecolor(theme.BG)
        self._figure.patch.set_facecolor(theme.BG)

        for spine in self._ax.spines.values():
            spine.set_color(theme.BORDER)
            
        self._ax.spines["top"].set_visible(False)
        self._ax.spines["right"].set_visible(False)
        self._ax.spines["left"].set_visible(False)
        self._ax.spines["bottom"].set_color(theme.BORDER)
        
        self._ax.tick_params(colors=theme.TEXT_MUTED, which="both", length=0, pad=8)
        self._ax.xaxis.label.set_color(theme.TEXT_MUTED)
        self._ax.title.set_color(theme.TEXT)

        items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        items = [x for x in items if x[1] > 0][:15]

        labels = [k for k, v in items]
        values = [v for k, v in items]
        
        if not values:
            self._ax.text(
                0.5, 0.5, "Sem dados", ha="center", va="center", color=theme.TEXT_MUTED, fontsize=9
            )
            self._ax.set_axis_off()
        else:
            y = np.arange(len(labels))
            
            bars = self._ax.barh(
                y,
                values,
                height=0.6,
                color=theme.TEXT_MUTED,
                edgecolor="none",
                alpha=1.0,
                zorder=3,
            )
            
            # Barras com listras zebra minimalistas
            for i, bar in enumerate(bars):
                bar.set_color(theme.TEXT_MUTED if i % 2 == 0 else theme.TEXT)
                
            self._ax.bar_label(bars, color=theme.TEXT_MUTED, padding=6, fontsize=9)
            
            self._ax.set_yticks(y)
            self._ax.set_yticklabels(labels, fontsize=9, color=theme.TEXT)
            self._ax.invert_yaxis()
            self._ax.set_xlabel("Vagas (Top 15)", fontsize=9, color=theme.TEXT_MUTED, labelpad=8)
            
            self._ax.xaxis.grid(True, color=theme.BORDER, linestyle=":", linewidth=1, alpha=0.5)
            self._ax.set_axisbelow(True)
            self._ax.set_xlim(left=0)

        if title:
            self._ax.set_title(title, fontsize=10, fontweight="normal", pad=8, color=theme.TEXT, loc="left")
            
        self._canvas.draw()
