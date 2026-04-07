from PyQt6.QtWidgets import (
    QWidget,
    QLayout,
    QFrame,
    QLabel,
)
from typing import Self, Optional
from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.common.styled_widget import StyledMixin


class PanelContent(QFrame, StyledMixin):
    """Контейнер содержимого панели с управляемым макетом.

    Компонент отвечает за отображение основного содержимого панели.
    Управляет вертикальным макетом и предоставляет методы
    для добавления виджетов и подмакетов.
    """

    def __init__(self: Self, title: str, parent: Optional[QWidget] = None) -> None:
        """Инициализировать контейнер содержимого панели.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("panel.qss")

        self._main_layout = create_vertical_layout(self, 12)

        # Добавить заголовок
        title_label = QLabel(title)
        title_label.setObjectName("PanelLabel")
        self._main_layout.addWidget(title_label)

    def add_widget(self: Self, widget: QWidget) -> None:
        """Добавить виджет в содержимое панели.

        Args:
            widget: Виджет для добавления.
        """
        self._main_layout.addWidget(widget)

    def add_layout(self: Self, layout: QLayout) -> None:
        """Добавить подмакет в содержимое панели.

        Args:
            layout: Макет для добавления.
        """
        self._main_layout.addLayout(layout)
