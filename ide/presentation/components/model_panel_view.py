from ide.presentation.components.common.panel_view import PanelView, PanelToolbar

import ast

from PyQt6.Qsci import QsciScintilla, QsciLexerPython

from typing import Optional, Self
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QColor

from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.containers import FormField


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

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать панель модели.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        self._current_model_info = ModelInfo()

        # Основной layout панели
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создать панель с тулбаром
        toolbar = self.create_toolbar()
        self.main_content = PanelView("Описание модели", toolbar)

        # Создать выбор бекенда
        self.create_backend_selector()

        # Создать редактор кода
        self.create_editor()

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

    def create_editor(self: Self) -> None:
        """Создать редактор кода Python с подсветкой синтаксиса.

        Настраивает подсветку синтаксиса, нумерацию строк, отступы
        и проверку синтаксиса при изменении текста.
        """
        self.editor = QsciScintilla()
        font = QFont("JetBrains Mono", 11)

        self.editor.setFont(font)
        self.editor.setMarginType(
            0,
            QsciScintilla.MarginType.NumberMargin,
        )
        self.editor.setMarginWidth(0, "00000")

        # Установить подсветку синтаксиса Python
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.editor.setLexer(lexer)

        # Настроить отступы и автоматическое выравнивание
        self.editor.setAutoIndent(True)
        self.editor.setIndentationWidth(4)
        self.editor.setTabWidth(4)

        # Установить шаблон по умолчанию
        self.editor.setText(self._default_template())
        self.editor.textChanged.connect(self._check_syntax)

        self.main_content.add_widget(self.editor)

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

    def set_model_info(self, info: ModelInfo) -> None:
        """Update model view with new information.

        Args:
            info: ModelInfo dataclass with model metadata
        """
        self._current_model_info = info

        # Update backend selector
        if info.backend in ["PyFloat", "NumPy", "PyTorch"]:
            index = self.backend_combo.findText(info.backend)
            if index >= 0:
                self.backend_combo.blockSignals(True)
                self.backend_combo.setCurrentIndex(index)
                self.backend_combo.blockSignals(False)

    def get_selected_backend(self) -> str:
        """Get currently selected backend.

        Returns:
            Backend name
        """
        return self.backend_combo.currentText()

    def get_current_model_info(self) -> ModelInfo:
        """Get current model information.

        Returns:
            ModelInfo dataclass
        """
        return self._current_model_info

    @staticmethod
    def _default_template() -> str:
        """Получить шаблон кода модели по умолчанию.

        Returns:
            Строка с кодом шаблона класса модели.
        """
        return """from typing import TypeVar
from n4.nn import Model
from n4 import Value

T = TypeVar("T")


class MyModel(Model[T]):

    def __init__(self):
        super().__init__()

    def forward(self, x: Value):

        w = Value(2.0)
        b = Value(1.0)

        y = w * x + b

        return y
"""

    def _check_syntax(self) -> bool:
        """Проверить синтаксис кода Python и выделить ошибки.

        Использует ast.parse() для проверки корректности синтаксиса.
        При обнаружении ошибок выделяет соответствующую строку
        красным фоном в редакторе.

        Returns:
            True если синтаксис корректен, False иначе.
        """
        code = self.editor.text()

        try:
            ast.parse(code)
            self.editor.markerDeleteAll()
            return True

        except SyntaxError as e:
            line = e.lineno - 1 if e.lineno else 0

            marker = self.editor.markerDefine(QsciScintilla.MarkerSymbol.Background)

            self.editor.setMarkerBackgroundColor(
                QColor("#ff6b6b"),
                marker,
            )

            self.editor.markerAdd(line, marker)
            return False
