"""SpinBox component for N4-IDE."""

from typing import Optional
from PyQt6.QtWidgets import QSpinBox, QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class SpinBox(QSpinBox):
    """Styled spin box matching N4-IDE design.

    Features:
    - Consistent styling
    - Clear increment/decrement buttons
    - Signal emission on value change
    """

    value_changed = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(9999)
        self._apply_style()
        self.valueChanged.connect(self.value_changed.emit)

    def _apply_style(self) -> None:
        """Apply stylesheet for spin box."""
        font = QFont("Open Sans", 14)
        self.setFont(font)

        stylesheet = """
            QSpinBox {
                padding: 4px 8px;
                background-color: white;
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 3px;
                color: rgba(0, 0, 0, 0.90);
            }
            QSpinBox:hover {
                border: 1px solid rgba(0, 0, 0, 0.12);
            }
            QSpinBox:focus {
                border: 2px solid #005FB8;
                padding: 3px 7px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: rgba(0, 95, 184, 0.08);
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: rgba(0, 95, 184, 0.15);
            }
        """
        self.setStyleSheet(stylesheet)
