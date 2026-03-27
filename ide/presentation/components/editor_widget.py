import ast
import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QToolBar,
    QFileDialog,
    QLabel,
    QComboBox,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QAction, QIcon, QColor
from PyQt6.Qsci import QsciScintilla, QsciLexerPython


class EditorWidget(QWidget):
    """Редактор Python-кода с подсветкой синтаксиса на базе QScintilla."""

    run_requested = pyqtSignal(str)  # Сигнал: код готов к выполнению
    debug_requested = pyqtSignal(str)  # Сигнал: запрос отладки

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        # Панель инструментов
        self.toolbar = QToolBar()
        icon_path = os.path.join("assets", "icons")

        run_action = QAction(
            QIcon(os.path.join(icon_path, "run.svg")),
            "Run Training",
            self,
        )

        debug_action = QAction(
            QIcon(os.path.join(icon_path, "debug.svg")),
            "Debug Gradients",
            self,
        )

        save_action = QAction(
            QIcon(os.path.join(icon_path, "save.svg")),
            "Save Script",
            self,
        )

        load_action = QAction(
            QIcon(os.path.join(icon_path, "load.svg")),
            "Load Script",
            self,
        )

        run_action.triggered.connect(self._run_clicked)
        debug_action.triggered.connect(self._debug_clicked)
        save_action.triggered.connect(self._save_file)
        load_action.triggered.connect(self._load_file)

        self.toolbar.addAction(run_action)
        self.toolbar.addAction(debug_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(load_action)

        layout.addWidget(self.toolbar)

        # Селектор вычислительного backend
        backend_layout = QHBoxLayout()
        backend_layout.addWidget(QLabel("Backend"))

        self.backend_selector = QComboBox()
        self.backend_selector.addItems(
            [
                "float",
                "numpy",
                "torch",
            ]
        )

        backend_layout.addWidget(self.backend_selector)
        backend_layout.addStretch()
        layout.addLayout(backend_layout)

        # Редактор кода
        self.editor = QsciScintilla()
        font = QFont("JetBrains Mono", 11)

        self.editor.setFont(font)
        self.editor.setMarginType(
            0,
            QsciScintilla.MarginType.NumberMargin,
        )
        self.editor.setMarginWidth(0, "00000")

        # Установка подсветки синтаксиса Python
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.editor.setLexer(lexer)

        # Настройки отступов
        self.editor.setAutoIndent(True)
        self.editor.setIndentationWidth(4)
        self.editor.setTabWidth(4)

        self.editor.setText(self._default_template())
        self.editor.textChanged.connect(self._check_syntax)

        layout.addWidget(self.editor)

    def get_code(self) -> str:
        """Получить текст кода из редактора."""
        return self.editor.text()

    def get_backend(self) -> str:
        """Получить выбранный backend."""
        return self.backend_selector.currentText()

    def set_code(self, code: str) -> None:
        """Установить текст кода в редактор."""
        self.editor.setText(code)

    def _run_clicked(self) -> None:
        """Обработчик клика кнопки запуска."""
        if self._check_syntax():
            self.run_requested.emit(self.get_code())

    def _debug_clicked(self) -> None:
        """Обработчик клика кнопки отладки."""
        if self._check_syntax():
            self.debug_requested.emit(self.get_code())

    def _save_file(self) -> None:
        """Сохранить код в файл."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save script",
            "",
            "Python Files (*.py)",
        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.text())

    def _load_file(self) -> None:
        """Загрузить код из файла."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open script",
            "",
            "Python Files (*.py)",
        )

        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            self.editor.setText(f.read())

    def _check_syntax(self) -> bool:
        """Проверить синтаксис Python кода и выделить ошибки."""
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

    @staticmethod
    def _default_template() -> str:
        """Получить шаблон кода по умолчанию."""
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
