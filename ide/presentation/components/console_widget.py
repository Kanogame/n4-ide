from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class ConsoleWidget(QWidget):
    """Консоль для отображения вывода программы и ошибок."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout.addWidget(self.output)

    def append_text(self, text: str) -> None:
        """Добавить текст в консоль."""
        self.output.append(text)

    def clear(self) -> None:
        """Очистить содержимое консоли."""
        self.output.clear()
