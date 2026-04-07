from typing import Optional

from PyQt6.QtWidgets import QComboBox, QWidget
from PyQt6.QtCore import pyqtSignal

from ide.presentation.common.styled_widget import StyledMixin


class ComboBox(QComboBox, StyledMixin):
    """
    ComboxBox, с типизиацией дропдауна
    """

    value_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._apply_style("combobox.qss")
        self.currentTextChanged.connect(self.value_changed.emit)
