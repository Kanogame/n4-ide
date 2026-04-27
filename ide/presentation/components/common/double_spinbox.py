from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDoubleSpinBox, QWidget

from ide.presentation.common.mixins import FontMixin, StyledMixin


class DoubleSpinBox(QDoubleSpinBox, StyledMixin, FontMixin):
    """Стилизованное поле ввода чисел с плавающей точкой. С инкрементом/дектементом"""

    # Сигнал при изменении значения.
    value_changed = pyqtSignal(float)

    def __init__(
        self,
        min: float = 1,
        max: float = 100,
        step: float = 1,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать компонент ввода дробного числа"""
        super().__init__(parent)
        self._apply_style("double_spinbox.qss")
        self._apply_font()

        self.setMinimum(min)
        self.setMaximum(max)
        self.setSingleStep(step)
        self.setDecimals(4)
        self.valueChanged.connect(self.value_changed.emit)
