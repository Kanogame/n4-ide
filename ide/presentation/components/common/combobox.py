from typing import Optional

from PyQt6.QtWidgets import QComboBox, QWidget
from PyQt6.QtCore import pyqtSignal

from ide.presentation.common.mixins import StyledMixin, FontMixin


class ComboBox(QComboBox, StyledMixin, FontMixin):
    """
    ComboxBox, с типизиацией дропдауна
    """

    value_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._apply_style("combobox.qss")
        self._apply_font()
        self.currentTextChanged.connect(self.value_changed.emit)
