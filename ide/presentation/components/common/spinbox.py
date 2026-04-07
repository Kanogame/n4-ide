from typing import Optional

from PyQt6.QtWidgets import QSpinBox, QWidget
from PyQt6.QtCore import pyqtSignal

from ide.presentation.common.mixins import StyledMixin, FontMixin


class SpinBox(QSpinBox, StyledMixin, FontMixin):
    """
    Spinbox - Инпут с инкремент/декремент кнопками
    """

    value_changed = pyqtSignal(int)

    def __init__(
        self,
        min: int = 1,
        max: int = 100,
        step: int = 1,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._apply_style("spinbox.qss")
        self._apply_font()

        self.setMinimum(min)
        self.setMaximum(max)
        self.setSingleStep(step)
        self.valueChanged.connect(self.value_changed.emit)
