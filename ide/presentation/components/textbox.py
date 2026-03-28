"""TextBox component for N4-IDE."""

from typing import Optional
from PyQt6.QtWidgets import QLineEdit, QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class TextBox(QLineEdit):
    """Styled text input field matching N4-IDE design.

    Features:
    - Consistent styling with border and background
    - Placeholder text support
    - Signal emission on text change
    """

    text_changed = pyqtSignal(str)

    def __init__(self, placeholder: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._apply_style()
        self.textChanged.connect(self.text_changed.emit)

    def _apply_style(self) -> None:
        """Apply stylesheet for text input."""
        font = QFont("Open Sans", 14)
        self.setFont(font)

        stylesheet = """
            QLineEdit {
                padding: 4px 8px;
                background-color: white;
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 3px;
                color: rgba(0, 0, 0, 0.90);
            }
            QLineEdit:hover {
                border: 1px solid rgba(0, 0, 0, 0.12);
            }
            QLineEdit:focus {
                border: 2px solid #005FB8;
                padding: 3px 7px;
            }
            QLineEdit::placeholder {
                color: rgba(0, 0, 0, 0.40);
            }
        """
        self.setStyleSheet(stylesheet)
