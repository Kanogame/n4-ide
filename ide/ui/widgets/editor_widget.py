from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class EditorWidget(QWidget):
    """Простейший редактор кода (заглушка)."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write Python code here...")

        layout.addWidget(self.editor)

    def get_code(self) -> str:
        """Получить текст кода."""
        return self.editor.toPlainText()