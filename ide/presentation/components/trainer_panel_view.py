from typing import Optional, Self

from PyQt6.QtWidgets import (
    QWidget,
    QSplitter,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt

from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.panel_view import PanelView
from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.components.trainer_panel.training_control import (
    TrainingControlWidget,
    TrainingConfig,
)
from ide.presentation.components.trainer_panel.training_log_reader import (
    TrainingLogReader,
)


class TrainerPanelView(QWidget):
    """Панель управления обучением нейронной сети.

    Компонент включает:
    - Конфигурацию параметров обучения (эпохи, батч, скорость обучения и т.д.)
    - Интерактивное логирование процесса обучения
    - Кнопки управления обучением (старт, пауза, остановка)

    Signals:
        training_started: Сигнал при нажатии кнопки старта обучения.
        training_paused: Сигнал при нажатии кнопки паузы.
        training_stopped: Сигнал при нажатии кнопки остановки.
    """

    # Сигнал при запуске обучения.
    training_started = pyqtSignal(TrainingConfig)

    # Сигнал при паузе обучения.
    training_paused = pyqtSignal()

    # Сигнал при остановке обучения.
    training_stopped = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать панель обучения.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        # Основной layout панели
        layout = create_vertical_layout(self)

        # Создать главную панель с тулбаром
        self.main_content = PanelView("Обучение модели")

        # Сплиттер для разделения конфигурации и логов
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("TrainerSplitter")
        splitter.setHandleWidth(10)

        # Добавляем растягивание
        splitter.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.main_content.add_widget(splitter)

        # Левая часть - конфигурация обучения
        self.create_config_widget()

        # Правая часть - логи обучения
        self.create_log_widget()

        splitter.addWidget(self.left_widget)
        splitter.addWidget(self.log_reader)

        # Установить соотношение размеров
        splitter.setSizes([1, 1])

        # Создать кнопки управления
        self.create_control_buttons()

        layout.addWidget(self.main_content)

    def create_config_widget(self: Self) -> None:
        """Создать левую панель с конфигурацией обучения.

        Содержит:
        - Выбор типа задачи
        - Количество эпох
        - Размер батча
        - Скорость обучения
        - Выбор оптимизатора
        """
        self.left_widget = QWidget()
        self.left_layout = create_vertical_layout(self.left_widget, 8)

        # Создать виджет управления обучением
        self.training_control = TrainingControlWidget()
        self.left_layout.addWidget(self.training_control)

        self.left_layout.addStretch()

    def create_log_widget(self: Self) -> None:
        """Создать правую панель с логированием обучения.

        Отображает вывод процесса обучения с поддержкой копирования.
        """
        self.log_reader = TrainingLogReader()

    def create_control_buttons(self: Self) -> None:
        """Создать кнопки управления процессом обучения.

        Включает:
        - Кнопка "Запустить" (синяя)
        - Кнопка "Пауза" (серая)
        - Кнопка "Остановить" (серая)
        """
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        # Кнопка запуска обучения
        self.start_button = Button("Запустить", ButtonStyle.ACCENT)
        self.start_button.clicked.connect(self._on_start_clicked)
        buttons_layout.addWidget(self.start_button)

        # Кнопка паузы
        self.pause_button = Button("Пауза", ButtonStyle.SECONDARY)
        self.pause_button.clicked.connect(self.training_paused.emit)
        buttons_layout.addWidget(self.pause_button)

        # Кнопка остановки
        self.stop_button = Button("Остановить", ButtonStyle.SECONDARY)
        self.stop_button.clicked.connect(self.training_stopped.emit)
        buttons_layout.addWidget(self.stop_button)

        self.main_content.add_layout(buttons_layout)

    def append_log(self, message: str) -> None:
        """Добавить сообщение в логи обучения.

        Args:
            message: Текст сообщения для добавления.
        """
        self.log_reader.append_log(message)

    def clear_logs(self) -> None:
        """Очистить все логи обучения."""
        self.log_reader._clear_logs()

    def get_current_config(self) -> TrainingConfig:
        """Получить текущую конфигурацию обучения.

        Returns:
            TrainingConfig с параметрами обучения.
        """
        return self.training_control.get_config()

    def set_training_enabled(self, enabled: bool) -> None:
        """Установить доступность кнопок обучения.

        Args:
            enabled: True если обучение может быть запущено, False иначе.
        """
        self.start_button.setEnabled(enabled)
        self.pause_button.setEnabled(not enabled)
        self.stop_button.setEnabled(not enabled)

    def _on_start_clicked(self: Self) -> None:
        """Обработчик нажатия кнопки запуска обучения."""
        config = self.get_current_config()
        self.training_started.emit(config)
        self.set_training_enabled(False)
