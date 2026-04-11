from typing import Optional, Set

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

from ide.domain.collectors import (
    get_metrics_for_task,
    get_metric_description,
    is_metric_applicable,
)
from ide.presentation.common.mixins import StyledMixin


class MetricsSelector(QWidget, StyledMixin):
    """Виджет для выбора активных метрик обучения.

    Отображает список доступных метрик для выбранного типа задачи
    с возможностью включения/отключения каждой метрики через checkbox.

    Автоматически обновляет доступные метрики при изменении типа задачи.

    Signals:
        metrics_changed: Сигнал при изменении набора активных метрик.
    """

    # Сигнал при изменении выбранных метрик
    metrics_changed = pyqtSignal(dict)  # Словарь {метрика: включена ли}

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать селектор метрик.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.setObjectName("MetricsSelector")

        # Применить стиль
        self._apply_style("metrics_selector.qss")

        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Заголовок
        title = QLabel("Метрики для отслеживания")
        title_font = QFont("Open Sans", 14)
        title_font.setWeight(QFont.Weight.Medium)
        title.setFont(title_font)
        title.setObjectName("MetricsSelectorTitle")
        layout.addWidget(title)

        # Контейнер для checkboxes
        self.checkboxes_layout = QVBoxLayout()
        self.checkboxes_layout.setContentsMargins(0, 0, 0, 0)
        self.checkboxes_layout.setSpacing(6)

        layout.addLayout(self.checkboxes_layout)
        layout.addStretch()

        # Словарь для хранения checkboxes
        self._metric_checkboxes: dict[str, QCheckBox] = {}

        # Текущий активный тип задачи
        self._current_task_type: str = "Классификация"

    def set_task_type(self, task_type: str) -> None:
        """Установить тип задачи и обновить доступные метрики.

        Args:
            task_type: Тип задачи (из PUBLIC_LOSS_MAPPING).
        """
        self._current_task_type = task_type
        self._update_metrics_for_task(task_type)

    def _update_metrics_for_task(self, task_type: str) -> None:
        """Обновить доступные метрики в зависимости от типа задачи.

        Args:
            task_type: Тип задачи.
        """
        available_metrics = get_metrics_for_task(task_type)

        # Обновить состояние и видимость checkboxes
        for metric_name, checkbox in self._metric_checkboxes.items():
            is_applicable = is_metric_applicable(metric_name, task_type)

            # Установить видимость
            checkbox.setVisible(is_applicable)
            checkbox.setEnabled(is_applicable)

            # Если метрика не применима, её отключить
            if not is_applicable:
                checkbox.setChecked(False)

        # Если нет видимых метрик, создать их
        if not any(cb.isVisible() for cb in self._metric_checkboxes.values()):
            self._populate_metrics(available_metrics)

    def _populate_metrics(self, metrics: Set[str]) -> None:
        """Заполнить виджет checkboxes для метрик.

        Args:
            metrics: Множество метрик для создания checkboxes.
        """
        # Очистить существующие checkboxes из layout
        while self.checkboxes_layout.count() > 0:
            item = self.checkboxes_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        # Очистить словарь checkboxes
        self._metric_checkboxes.clear()

        # Создать checkbox для каждой метрики
        for metric_name in sorted(metrics):
            checkbox = self._create_metric_checkbox(metric_name)
            self._metric_checkboxes[metric_name] = checkbox
            self.checkboxes_layout.addWidget(checkbox)

    def _create_metric_checkbox(self, metric_name: str) -> QCheckBox:
        """Создать checkbox для метрики с описанием.

        Args:
            metric_name: Имя метрики.

        Returns:
            QCheckBox для управления этой метрикой.
        """
        description = get_metric_description(metric_name)

        # Создать checkbox с именем и описанием
        checkbox = QCheckBox(f"{metric_name}: {description}")
        checkbox.setObjectName(f"MetricsCheckbox_{metric_name}")

        # Применить шрифт
        font = QFont("Open Sans", 12)
        checkbox.setFont(font)

        # Loss всегда включена
        if metric_name == "loss":
            checkbox.setChecked(True)
            checkbox.setEnabled(False)

        # Подключить сигнал для отслеживания изменений
        checkbox.stateChanged.connect(self._on_metrics_changed)

        return checkbox

    def _on_metrics_changed(self) -> None:
        """Обработчик при изменении выбранных метрик."""
        metrics_dict = self.get_selected_metrics()
        self.metrics_changed.emit(metrics_dict)

    def get_selected_metrics(self) -> dict[str, bool]:
        """Получить словарь выбранных метрик.

        Returns:
            Словарь {имя_метрики: включена_ли}.
        """
        return {
            metric_name: checkbox.isChecked()
            for metric_name, checkbox in self._metric_checkboxes.items()
        }

    def set_selected_metrics(self, metrics: dict[str, bool]) -> None:
        """Установить выбранные метрики.

        Args:
            metrics: Словарь {имя_метрики: включена_ли}.
        """
        for metric_name, is_checked in metrics.items():
            if metric_name in self._metric_checkboxes:
                checkbox = self._metric_checkboxes[metric_name]
                checkbox.blockSignals(True)
                checkbox.setChecked(is_checked)
                checkbox.blockSignals(False)

    def reset_to_defaults(self) -> None:
        """Сбросить метрики к значениям по умолчанию для текущего типа задачи."""
        available_metrics = get_metrics_for_task(self._current_task_type)
        default_metrics = {
            "loss": True,
            "accuracy": "accuracy" in available_metrics,
            "f1_score": False,
        }
        self.set_selected_metrics(default_metrics)
