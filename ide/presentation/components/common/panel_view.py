from ide.presentation.common.layouts import create_layout
from ide.presentation.common.styled_widget import StyledMixin
from ide.presentation.components.common.panel.panel_content import PanelContent
from ide.presentation.components.common.panel.panel_toolbar import PanelToolbar
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLayout,
    QFrame,
)
from typing import Self, Optional


class PanelView(QFrame, StyledMixin):
    """
    Главный компонент панели с заголовком, тулбаром и содержимым.

    Компонент объединяет заголовок, опциональный тулбар и основное содержимое
    в единую панель с соответствующей структурой и стилизацией.
    """

    def __init__(
        self: Self,
        title: str,
        toolbar: Optional[PanelToolbar] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать панель.

        Args:
            title: Текст заголовка панели.
            toolbar: Опциональный тулбар панели, или None.
            parent: Родительский виджет.
        """
        super().__init__(
            parent,
        )

        self._apply_style("panel.qss")

        self.setObjectName("PanelView")

        layout = create_layout(self)

        # Добавить тулбар если предоставлен
        if toolbar:
            self.toolbar = toolbar
            layout.addWidget(toolbar)

        # Добавить контейнер содержимого
        self.content = PanelContent(title)
        layout.addWidget(self.content)

    def add_widget(self: Self, widget: QWidget) -> None:
        """Добавить виджет в содержимое панели.

        Args:
            widget: Виджет для добавления.
        """
        self.content.add_widget(widget)

    def add_layout(self: Self, layout: QLayout) -> None:
        """Добавить подмакет в содержимое панели.

        Args:
            layout: Макет для добавления.
        """
        self.content.add_layout(layout)
