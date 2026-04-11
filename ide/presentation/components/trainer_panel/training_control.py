from typing import Optional

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from ide.domain.optimizer import OPTIMIZER_REGISTRY
from ide.domain.loss import PUBLIC_LOSS_MAPPING
from ide.domain.training.models import TrainingConfig

from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.common.spinbox import SpinBox
from ide.presentation.components.common.double_spinbox import DoubleSpinBox
from ide.presentation.components.common.form_field import FormField
from ide.presentation.components.common.metrics_selector import MetricsSelector


class TrainingControlWidget(QWidget):
    """Компонент для управления параметрами обучения модели.

    Позволяет выбрать:
    - Тип задачи (классификация, регрессия)
    - Количество эпох
    - Размер батча
    - Скорость обучения
    - Оптимизатор
    - Метрики для отслеживания

    Signals:
        config_changed: Сигнал при изменении любого параметра конфигурации.
    """

    # Сигнал при изменении конфигурации обучения.
    config_changed = pyqtSignal(TrainingConfig)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать виджет управления обучением.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        layout = create_vertical_layout(self, 12)

        # Выбор типа задачи
        self.task_combo = ComboBox()
        self.task_combo.addItems(list(PUBLIC_LOSS_MAPPING.keys()))
        self.task_combo.value_changed.connect(self._on_task_changed)
        task_field = FormField("Тип задачи", self.task_combo)
        layout.addWidget(task_field)

        # Количество эпох
        self.epochs_spinbox = SpinBox(min=1, max=10000, step=1)
        self.epochs_spinbox.setValue(50)
        self.epochs_spinbox.value_changed.connect(self._on_config_changed)
        epochs_field = FormField("Количество эпох", self.epochs_spinbox)
        layout.addWidget(epochs_field)

        # Размер батча
        self.batch_size_spinbox = SpinBox(min=1, max=512, step=1)
        self.batch_size_spinbox.setValue(32)
        self.batch_size_spinbox.value_changed.connect(self._on_config_changed)
        batch_field = FormField("Размер батча", self.batch_size_spinbox)
        layout.addWidget(batch_field)

        # Learning rate
        self.learning_rate_spinbox = DoubleSpinBox(
            min=0.00001,
            max=1.0,
            step=0.00001,
        )
        self.learning_rate_spinbox.setValue(0.001)
        self.learning_rate_spinbox.value_changed.connect(self._on_config_changed)
        lr_field = FormField("Learning rate", self.learning_rate_spinbox)
        layout.addWidget(lr_field)

        # Выбор оптимизатора
        self.optimizer_combo = ComboBox()
        self.optimizer_combo.addItems(list(OPTIMIZER_REGISTRY.keys()))
        self.optimizer_combo.value_changed.connect(self._on_config_changed)
        optimizer_field = FormField("Оптимизатор", self.optimizer_combo)
        layout.addWidget(optimizer_field)

        # Селектор метрик для отслеживания
        self.metrics_selector = MetricsSelector()
        self.metrics_selector.metrics_changed.connect(self._on_metrics_changed)
        layout.addWidget(self.metrics_selector)

        layout.addStretch()

        # Инициализировать конфигурацию
        self._current_config = TrainingConfig()

        # Инициализировать метрики в зависимости от типа задачи
        self._update_metrics_for_task()

    def get_config(self) -> TrainingConfig:
        """Получить текущую конфигурацию обучения.

        Returns:
            TrainingConfig с текущими параметрами.
        """
        return TrainingConfig(
            task_type=self.task_combo.currentText(),
            epochs=self.epochs_spinbox.value(),
            batch_size=self.batch_size_spinbox.value(),
            learning_rate=self.learning_rate_spinbox.value(),
            optimizer=self.optimizer_combo.currentText(),
            metrics=self.metrics_selector.get_selected_metrics(),
        )

    def set_config(self, config: TrainingConfig) -> None:
        """Установить конфигурацию обучения.

        Args:
            config: TrainingConfig для установки.
        """
        self._current_config = config

        # Блокировать сигналы при обновлении
        self.task_combo.blockSignals(True)
        self.epochs_spinbox.blockSignals(True)
        self.batch_size_spinbox.blockSignals(True)
        self.learning_rate_spinbox.blockSignals(True)
        self.optimizer_combo.blockSignals(True)
        self.metrics_selector.metrics_changed.disconnect()

        # Обновить значения
        index = self.task_combo.findText(config.task_type)
        if index >= 0:
            self.task_combo.setCurrentIndex(index)

        self.epochs_spinbox.setValue(config.epochs)
        self.batch_size_spinbox.setValue(config.batch_size)
        self.learning_rate_spinbox.setValue(config.learning_rate)

        opt_index = self.optimizer_combo.findText(config.optimizer)
        if opt_index >= 0:
            self.optimizer_combo.setCurrentIndex(opt_index)

        # Обновить метрики
        self._update_metrics_for_task()
        if config.metrics:
            self.metrics_selector.set_selected_metrics(config.metrics)

        # Разблокировать сигналы
        self.task_combo.blockSignals(False)
        self.epochs_spinbox.blockSignals(False)
        self.batch_size_spinbox.blockSignals(False)
        self.learning_rate_spinbox.blockSignals(False)
        self.optimizer_combo.blockSignals(False)
        self.metrics_selector.metrics_changed.connect(self._on_metrics_changed)

    def _on_config_changed(self) -> None:
        """Обработчик при изменении любого параметра конфигурации."""
        self._current_config = self.get_config()
        self.config_changed.emit(self._current_config)

    def _on_task_changed(self) -> None:
        """Обработчик при изменении типа задачи.

        Обновляет доступные метрики и эмитирует сигнал конфигурации.
        """
        self._update_metrics_for_task()
        self._on_config_changed()

    def _update_metrics_for_task(self) -> None:
        """Обновить доступные метрики при изменении типа задачи.

        Вызывается при изменении выбранного типа задачи для обновления
        списка доступных метрик в селекторе метрик.
        """
        current_task = self.task_combo.currentText()
        self.metrics_selector.set_task_type(current_task)

    def _on_metrics_changed(self, metrics: dict[str, bool]) -> None:
        """Обработчик при изменении выбранных метрик.

        Args:
            metrics: Словарь выбранных метрик.
        """
        self._current_config = self.get_config()
        self.config_changed.emit(self._current_config)
