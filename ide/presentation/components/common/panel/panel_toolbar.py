from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLayout,
    QFrame,
)
from typing import Self, Optional
from ide.presentation.common.styled_widget import StyledMixin


class PanelToolbar(QFrame, StyledMixin):
    """Тулбар панели для управления действиями.

    Компонент предоставляет верхнюю панель инструментов для размещения
    кнопок и других элементов управления.
    """

    def __init__(self: Self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать тулбар панели.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("panel.qss")

        self.setObjectName("PanelToolbar")

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

    def add_widget(self: Self, widget: QWidget) -> None:
        """Добавить виджет в тулбар.

        Args:
            widget: Виджет для добавления (кнопка, комбобокс и т.д.).
        """
        self._layout.addWidget(widget)

    def add_stretch(self: Self) -> None:
        """Добавить растяжимый пространство для выравнивания элементов.

        Полезно для размещения элементов у левого или правого края тулбара.
        """
        self._layout.addStretch()

    def add_layout(self: Self, layout: QLayout) -> None:
        """Добавить подмакет в тулбар.

        Args:
            layout: Макет для добавления.
        """
        self._layout.addLayout(layout)
