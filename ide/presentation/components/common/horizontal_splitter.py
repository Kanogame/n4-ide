from PyQt6.QtCore import Qt

from typing import Self
from ide.presentation.common.mixins import StyledMixin
from PyQt6.QtWidgets import QSplitter, QWidget, QSizePolicy


class HorizontalSplitter(QSplitter, StyledMixin):
    """
    Горизонтальный сплиттер со стилизацией
    """

    def __init__(self: Self, left: QWidget, right: QWidget):
        super().__init__(Qt.Orientation.Horizontal)
        self._apply_style("splitter.qss")
        self.setHandleWidth(10)

        # Добавляем растягивание - всегда ведет себя как flex: 1
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.addWidget(left)
        self.addWidget(right)

        self.setSizes([1, 1])
