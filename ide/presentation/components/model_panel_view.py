from typing import Optional, Self
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal

from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.common.form_field import FormField

from ide.presentation.components.model_panel.editor import Editor
from ide.presentation.components.common.panel_view import PanelView, PanelToolbar


@dataclass(frozen=True)
class ModelInfo:
    """Неизменяемый снимок информации о модели.

    Attributes:
        backend: Имя вычислительного бекенда (по умолчанию "PyFloat").
        layer_count: Количество слоёв в модели.
        total_parameters: Общее количество параметров модели.
        code: Исходный код модели.
    """

    backend: str = "PyFloat"
    layer_count: int = 0
    total_parameters: int = 0
    code: str = ""


class ModelPanelView(QWidget):
    """Панель визуализации и редактирования модели нейронной сети.

    Компонент отображает редактор кода модели и позволяет выбрать
    вычислительный бекенд для выполнения.

    Signals:
        train_requested: Сигнал при нажатии на кнопку обучения.
        backend_changed: Сигнал при изменении выбранного бекенда.
    """

    # Сигнал при нажатии на кнопку обучения.
    train_requested = pyqtSignal()

    # Сигнал при изменении выбора вычислительного бекенда.
    backend_changed = pyqtSignal(str)

    def __init__(self: Self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать панель модели"""
        super().__init__(parent)

        self._current_model_info = ModelInfo()

        # Основной layout панели
        layout = create_vertical_layout(self)

        # Создать панель с тулбаром
        toolbar = self.create_toolbar()
        self.main_content = PanelView("Описание модели", toolbar)

        # Создать выбор бекенда
        self.create_backend_selector()

        # Создать редактор кода
        self.editor = Editor()
        self.main_content.add_widget(self.editor)

        # Создать кнопки управления
        self.create_buttons()

        layout.addWidget(self.main_content)

    def create_toolbar(self: Self) -> PanelToolbar:
        """Создать тулбар панели.

        Returns:
            Экземпляр PanelToolbar с кнопками действий.
        """
        return PanelToolbar()

    def create_backend_selector(self: Self) -> None:
        """Создать выпадающий список выбора вычислительного бекенда.

        Поддерживаемые бекенды: PyFloat, NumPy, PyTorch.
        Подключает сигнал изменения на backend_changed.
        """
        self.backend_combo = ComboBox()
        self.backend_combo.addItems(["PyFloat", "NumPy", "PyTorch"])
        self.backend_combo.value_changed.connect(self.backend_changed.emit)

        backend_field = FormField("Вычислительный бекенд", self.backend_combo)
        self.main_content.add_widget(backend_field)

    def create_buttons(self: Self) -> None:
        """Создать кнопки управления панели.

        Включает кнопку "Обучить" для запуска процесса обучения модели.
        """
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        self.train_button = Button("Обучить", ButtonStyle.ACCENT)
        self.train_button.clicked.connect(self.train_requested.emit)
        buttons_layout.addWidget(self.train_button)

        self.main_content.add_layout(buttons_layout)

    def get_selected_backend(self: Self) -> str:
        """Get currently selected backend.

        Returns:
            Backend name
        """
        return self.backend_combo.currentText()

    def get_current_model_info(self: Self) -> ModelInfo:
        """Get current model information.

        Returns:
            ModelInfo dataclass
        """
        return self._current_model_info

    def get_model_code(self: Self) -> str:
        """Получить исходный код модели из редактора.

        Returns:
            Текст кода модели.
        """
        return self.editor.get_model_code()
