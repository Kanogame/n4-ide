"""ComboBox component for N4-IDE."""

from typing import Optional
from PyQt6.QtWidgets import QComboBox, QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class ComboBox(QComboBox):
    """Styled combo box matching N4-IDE design.

    Features:
    - Consistent styling with border and background
    - Type hints for dropdown items
    - Signal emission on value change
    """

    value_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._apply_style()
        self.currentTextChanged.connect(self.value_changed.emit)

    def _apply_style(self) -> None:
        """Apply stylesheet for combo box."""
        font = QFont("Open Sans", 14)
        self.setFont(font)

        stylesheet = """
            QComboBox {
                padding: 4px 8px;
                background-color: rgba(255, 255, 255, 0.70);
                border: 1px rgba(0, 0, 0, 0.06) solid;
                border-radius: 3px;
                color: rgba(0, 0, 0, 0.90);
            }
            QComboBox:hover {
                background-color: white;
                border: 1px solid #005FB8;
            }
            QComboBox:focus {
                border: 2px solid #005FB8;
                padding: 3px 7px;
            }
            QComboBox::drop-down {
                border: none;
                width: 12px;
                margin-right: 4px;
            }
            QComboBox::drop-down:button {
                background-color: transparent;
            }
            QAbstractItemView {
                background-color: white;
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 3px;
                selection-background-color: #005FB8;
                color: rgba(0, 0, 0, 0.90);
            }
            QAbstractItemView::item:selected {
                background-color: #005FB8;
                color: white;
            }
        """
        self.setStyleSheet(stylesheet)
