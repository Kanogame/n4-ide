from typing import Optional
from dataclasses import dataclass, field

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.common.spinbox import SpinBox
from ide.presentation.components.common.double_spinbox import DoubleSpinBox
from ide.presentation.components.containers import FormField


@dataclass(frozen=True)
class TrainingConfig:
    """Неизменяемая конфигурация параметров обучения.

    Attributes:
        task_type: Тип задачи обучения (классификация, регрессия и т.д.).
        epochs: Количество эпох обучения.
        batch_size: Размер батча для обучения.
        learning_rate: Скорость обучения (learning rate).
        optimizer: Выбранный оптимизатор (SGD, Adam и т.д.).
        metrics: Словарь активных метрик.
    """

    task_type: str = "Классификация"
    epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: str = "Adam"
    metrics: dict[str, bool] = field(
        default_factory=lambda: {"loss": True, "accuracy": True}
    )


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
        self.task_combo.addItems(
            [
                "Классификация",
                "Регрессия",
                "Кластеризация",
            ]
        )
        self.task_combo.value_changed.connect(self._on_config_changed)
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

        # Скорость обучения
        self.learning_rate_spinbox = DoubleSpinBox(
            min=0.00001,
            max=1.0,
            step=0.00001,
        )
        self.learning_rate_spinbox.setValue(0.001)
        self.learning_rate_spinbox.value_changed.connect(self._on_config_changed)
        lr_field = FormField("Скорость обучения", self.learning_rate_spinbox)
        layout.addWidget(lr_field)

        # Выбор оптимизатора
        self.optimizer_combo = ComboBox()
        self.optimizer_combo.addItems(
            [
                "Adam",
                "SGD",
                "RMSprop",
                "Adamax",
            ]
        )
        self.optimizer_combo.value_changed.connect(self._on_config_changed)
        optimizer_field = FormField("Оптимизатор", self.optimizer_combo)
        layout.addWidget(optimizer_field)

        layout.addStretch()

        # Инициализировать конфигурацию
        self._current_config = TrainingConfig()

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

        # Разблокировать сигналы
        self.task_combo.blockSignals(False)
        self.epochs_spinbox.blockSignals(False)
        self.batch_size_spinbox.blockSignals(False)
        self.learning_rate_spinbox.blockSignals(False)
        self.optimizer_combo.blockSignals(False)

    def _on_config_changed(self) -> None:
        """Обработчик при изменении любого параметра конфигурации."""
        self._current_config = self.get_config()
        self.config_changed.emit(self._current_config)
