from PyQt6.QtCore import Qt
import ast
from PyQt6.QtGui import QColor, QFont
from typing import Self, Optional

from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtWidgets import QFrame, QWidget

from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.common.mixins import StyledMixin


class Editor(QFrame, StyledMixin):
    def __init__(self: Self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._apply_style("editor.qss")

        self.main_content = create_vertical_layout(self)
        self.create_editor()

    def create_editor(self: Self) -> None:
        """Создать редактор кода Python с подсветкой синтаксиса.

        Настраивает подсветку синтаксиса, нумерацию строк, отступы
        и проверку синтаксиса при изменении текста.
        """

        self.wrapper = QFrame()
        self.wrapper.setObjectName("Wrapper")

        self.editor = QsciScintilla(self.wrapper)
        self.editor.setObjectName("Editor")

        background = QColor("#fff")
        line_number_fg = QColor("#D6D6D6")

        # Font
        font = QFont("Droid Sans Mono", 14)
        self.editor.setFont(font)

        self.editor.setMarginsBackgroundColor(background)
        self.editor.setMarginsForegroundColor(line_number_fg)

        self.editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.editor.setMarginWidth(0, 40)
        self.editor.setMarginLineNumbers(0, True)
        self.editor.setMarginsFont(font)

        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)

        lexer.setColor(QColor("#333333"), QsciLexerPython.Default)
        lexer.setColor(QColor("#0077AA"), QsciLexerPython.Keyword)
        lexer.setColor(QColor("#AA3731"), QsciLexerPython.ClassName)
        lexer.setColor(QColor("#795E26"), QsciLexerPython.FunctionMethodName)
        lexer.setColor(QColor("#6A3955"), QsciLexerPython.Comment)

        lexer.setPaper(background, QsciLexerPython.Default)
        lexer.setPaper(background, QsciLexerPython.Keyword)
        lexer.setPaper(background, QsciLexerPython.Comment)

        self.editor.setLexer(lexer)

        self.editor.setCaretForegroundColor(QColor("#000000"))
        self.editor.setSelectionBackgroundColor(QColor("#ADD6FF"))

        self.editor.setIndentationGuides(True)
        self.editor.setIndentationsUseTabs(False)
        self.editor.setIndentationWidth(4)
        self.editor.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)

        self.editor.setText(self._default_template())
        self.editor.textChanged.connect(self._check_syntax)

        self.main_content.addWidget(self.editor)

    @staticmethod
    def _default_template() -> str:
        """Получить шаблон кода модели по умолчанию.

        Returns:
            Строка с кодом шаблона класса модели.
        """

        return """class MyModel(Model[PyFloat]):
    def __init__(self) -> None:
        self.backend = PyFloat
        self.model = Sequential(
            DenseLayer(2, 12, self.backend, Relu),
            DenseLayer(12, 2, self.backend, NonOp),
            SoftmaxLayer(self.backend),
        )

    def forward_pass(self, x: Tensor[PyFloat]) -> Tensor[PyFloat]:
        return self.model.forward_pass(x)

    def parameters(self):
        return self.model.parameters()
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

    def get_model_code(self) -> str:
        """Получить исходный код модели из редактора.

        Returns:
            Текст кода модели.
        """
        return self.editor.text()
