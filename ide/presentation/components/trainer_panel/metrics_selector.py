from ide.presentation.common.layouts import create_vertical_layout
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

from ide.domain.collectors import (
    get_collectors_for_task,
    get_collector_description,
    is_collector_applicable,
    get_collector_registry,
)
from ide.presentation.common.mixins import FontMixin, StyledMixin


class MetricsSelector(QFrame, StyledMixin, FontMixin):
    """Виджет для выбора активных сборщиков при обучении.

    Отображает список доступных сборщиков для выбранного типа задачи
    с возможностью включения/отключения каждого сборщика через checkbox.

    Автоматически обновляет доступные сборщики при изменении типа задачи
    и синхронизируется с глобальным реестром сборщиков.

    Signals:
        metrics_changed: Сигнал при изменении набора активных сборщиков.
    """

    # Сигнал при изменении выбранных сборщиков
    metrics_changed = pyqtSignal(dict)  # Словарь {сборщик: включен ли}

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать селектор сборщиков.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("metrics_selector.qss")
        self._apply_font()

        self.setObjectName("MetricsSelector")

        # Основной layout
        layout = create_vertical_layout(self, 8)

        # Заголовок
        title = QLabel("Сборщики для отслеживания")
        title_font = QFont("Open Sans", 14)
        title_font.setWeight(QFont.Weight.Normal)
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
        self._collector_checkboxes: dict[str, QCheckBox] = {}

        # Текущий активный тип задачи
        self._current_task_type: str = "Классификация"

        # Инициализировать все доступные сборщики из реестра
        self._populate_all_collectors()

    def _populate_all_collectors(self) -> None:
        """Заполнить виджет checkboxes для всех доступных сборщиков из реестра.

        Загружает все зарегистрированные в системе сборщики и создает
        checkbox для каждого. Видимость и доступность определяются типом задачи.
        """
        # Получить реестр и все доступные сборщики
        registry = get_collector_registry()
        all_collectors = registry.list_metrics()

        # Создать checkbox для каждого сборщика
        for collector_name in sorted(all_collectors):
            checkbox = self._create_collector_checkbox(collector_name)
            self._collector_checkboxes[collector_name] = checkbox
            self.checkboxes_layout.addWidget(checkbox)

        # Обновить видимость для текущего типа задачи
        self._update_collectors_for_task(self._current_task_type)

    def set_task_type(self, task_type: str) -> None:
        """Установить тип задачи и обновить доступные сборщики.

        Args:
            task_type: Тип задачи (из PUBLIC_LOSS_MAPPING).
        """
        self._current_task_type = task_type
        self._update_collectors_for_task(task_type)

    def _update_collectors_for_task(self, task_type: str) -> None:
        """Обновить доступные сборщики в зависимости от типа задачи.

        Args:
            task_type: Тип задачи.
        """
        # Обновить состояние и видимость checkboxes
        for collector_name, checkbox in self._collector_checkboxes.items():
            is_applicable = is_collector_applicable(collector_name, task_type)

            # Установить видимость
            checkbox.setVisible(is_applicable)
            checkbox.setEnabled(is_applicable)

            # Если сборщик не применим, его отключить
            if not is_applicable:
                checkbox.setChecked(False)

    def _create_collector_checkbox(self, collector_name: str) -> QCheckBox:
        """Создать checkbox для сборщика с описанием.

        Args:
            collector_name: Имя сборщика.

        Returns:
            QCheckBox для управления этим сборщиком.
        """
        description = get_collector_description(collector_name)

        # Создать checkbox с именем и описанием
        checkbox = QCheckBox(f"{collector_name}: {description}")
        checkbox.setObjectName(f"CollectorCheckbox_{collector_name}")

        # Применить шрифт
        font = QFont("Open Sans", 12)
        checkbox.setFont(font)

        # Loss всегда включена
        if collector_name == "loss":
            checkbox.setChecked(True)
            checkbox.setEnabled(False)

        # Подключить сигнал для отслеживания изменений
        checkbox.stateChanged.connect(self._on_collectors_changed)

        return checkbox

    def _on_collectors_changed(self) -> None:
        """Обработчик при изменении выбранных сборщиков."""
        collectors_dict = self.get_selected_metrics()
        self.metrics_changed.emit(collectors_dict)

    def get_selected_metrics(self) -> dict[str, bool]:
        """Получить словарь выбранных сборщиков.

        Returns:
            Словарь {имя_сборщика: включен_ли}.
        """
        return {
            collector_name: checkbox.isChecked()
            for collector_name, checkbox in self._collector_checkboxes.items()
        }

    def set_selected_metrics(self, collectors: dict[str, bool]) -> None:
        """Установить выбранные сборщики.

        Args:
            collectors: Словарь {имя_сборщика: включен_ли}.
        """
        for collector_name, is_checked in collectors.items():
            if collector_name in self._collector_checkboxes:
                checkbox = self._collector_checkboxes[collector_name]
                checkbox.blockSignals(True)
                checkbox.setChecked(is_checked)
                checkbox.blockSignals(False)

    def reset_to_defaults(self) -> None:
        """Сбросить сборщики к значениям по умолчанию для текущего типа задачи."""
        available_collectors = get_collectors_for_task(self._current_task_type)
        default_collectors = {
            "loss": True,
            "accuracy": "accuracy" in available_collectors,
            "f1_score": False,
        }
        self.set_selected_metrics(default_collectors)
