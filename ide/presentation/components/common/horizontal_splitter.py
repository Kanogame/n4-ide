from PyQt6.QtCore import Qt

from typing import Self
from ide.presentation.common.mixins import StyledMixin
from PyQt6.QtWidgets import QSplitter, QWidget, QSizePolicy


class HorizontalSplitter(QSplitter, StyledMixin):
    """
    Горизонтальный сплиттер со стилизацией
    """

    def __init__(
        self: Self,
        left: QWidget,
        right: QWidget,
        left_ratio: float = 0.5,
        right_ratio: float = 0.5,
    ) -> None:
        super().__init__(Qt.Orientation.Horizontal)
        self._apply_style("splitter.qss")
        self.setHandleWidth(10)

        # Добавляем растягивание - всегда ведет себя как flex: 1
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.addWidget(left)
        self.addWidget(right)

        self.left_ratio = left_ratio
        self.rigt_ratio = right_ratio

        self.apply_ratio()

    def apply_ratio(self: Self) -> None:
        total_width = self.width()
        left_width = int(total_width * self.left_ratio)
        right_width = total_width - left_width

        self.setSizes([left_width, right_width])
