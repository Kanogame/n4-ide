from typing import Optional

from PyQt6.QtWidgets import QSpinBox, QWidget
from PyQt6.QtCore import pyqtSignal

from ide.presentation.common.styled_widget import StyledMixin


class SpinBox(QSpinBox, StyledMixin):
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
        self.setMinimum(min)
        self.setMaximum(max)
        self.setSingleStep(step)
        self._apply_style("spinbox.qss")
        self.valueChanged.connect(self.value_changed.emit)
