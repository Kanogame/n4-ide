"""Панель для отображения метрик и графиков обучения.

Основной компонент для визуализации хода обучения нейронной сети,
включающий интерактивные графики и отображение текущих метрик.
"""

from typing import Optional

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from ide.domain.collectors import CollectorRepository
from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.panel_view import PanelView
from ide.presentation.components.metrics_panel.metrics_graph_widget import (
    MetricsGraphWidget,
)


class MetricsPanelView(QWidget):
    """Панель для отображения метрик обучения.

    Содержит:
    - Интерактивный график выбранной метрики
    - Отображение текущих значений всех метрик
    - Кнопки управления отображением

    Signals:
        metric_selected: Сигнал при выборе метрики для отображения.
    """

    # Сигнал при выборе метрики
    metric_selected = pyqtSignal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        metrics_storage: Optional[CollectorRepository] = None,
    ) -> None:
        """Инициализировать панель метрик.

        Args:
            parent: Родительский виджет.
            metrics_storage: Хранилище метрик (если None, создается новое).
        """
        super().__init__(parent)

        # Использовать переданное хранилище или создать новое
        self._metrics_storage = metrics_storage or CollectorRepository()

        # Основной layout панели
        layout = create_vertical_layout(self)

        # Создать главную панель
        self.main_content = PanelView("Метрики обучения")

        # Создать левую часть - график метрики
        self.metrics_graph = MetricsGraphWidget(self._metrics_storage)
        self.metrics_graph.metric_changed.connect(self.metric_selected.emit)
        self.main_content.add_widget(self.metrics_graph)

        layout.addWidget(self.main_content)

    def set_metrics_storage(self, storage: CollectorRepository) -> None:
        """Установить хранилище метрик и обновить график.

        Args:
            storage: Новое хранилище метрик для использования.
        """
        self._metrics_storage = storage
        self.metrics_graph._metrics_storage = storage
        self.metrics_graph.refresh()
