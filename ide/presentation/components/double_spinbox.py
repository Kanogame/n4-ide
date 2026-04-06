"""DoubleSpinBox component for N4-IDE."""

from typing import Optional
from PyQt6.QtWidgets import QDoubleSpinBox, QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class DoubleSpinBox(QDoubleSpinBox):
    """Стилизованное поле ввода чисел с плавающей точкой.

    Компонент предоставляет удобный интерфейс для ввода дробных значений
    с инкрементом и декрементом через кнопки.

    Features:
    - Согласованная стилизация с дизайн-системой N4-IDE
    - Поддержка арифметических операций (инкремент/декремент)
    - Сигнал при изменении значения
    """

    # Сигнал при изменении значения.
    value_changed = pyqtSignal(float)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать компонент ввода дробного числа.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.setMinimum(0.0)
        self.setMaximum(9999.0)
        self.setDecimals(4)
        self._apply_style()
        self.valueChanged.connect(self.value_changed.emit)

    def _apply_style(self) -> None:
        """Применить стиль к компоненту."""
        font = QFont("Open Sans", 14)
        self.setFont(font)

        stylesheet = """
            QDoubleSpinBox {
                padding: 4px 8px;
                background-color: white;
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 3px;
                color: rgba(0, 0, 0, 0.90);
            }
            QDoubleSpinBox:hover {
                border: 1px solid rgba(0, 0, 0, 0.12);
            }
            QDoubleSpinBox:focus {
                border: 2px solid #005FB8;
                padding: 3px 7px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: none;
                background-color: rgba(0, 95, 184, 0.08);
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: rgba(0, 95, 184, 0.15);
            }
        """
        self.setStyleSheet(stylesheet)
