from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class ConsoleWidget(QWidget):
    """Консоль вывода программы."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout.addWidget(self.output)

    def append_text(self, text: str) -> None:
        """Добавить текст в консоль."""
        self.output.append(text)