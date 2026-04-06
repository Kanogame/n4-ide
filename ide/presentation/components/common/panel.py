from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
)
from typing import Self, Optional
from ide.presentation.common.styled_widget import StyledComponent


class PanelContent(StyledComponent):
    """Контейнер содержимого панели с управляемым макетом.

    Компонент отвечает за отображение основного содержимого панели.
    Управляет вертикальным макетом и предоставляет методы
    для добавления виджетов и подмакетов.
    """

    def __init__(self: Self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать контейнер содержимого панели.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent, "panel.qss")

        self.setObjectName("PanelContent")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(12)

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


class PanelToolbar(StyledComponent):
    """Тулбар панели для управления действиями.

    Компонент предоставляет верхнюю панель инструментов для размещения
    кнопок и других элементов управления.
    """

    def __init__(self: Self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать тулбар панели.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent, "panel.qss")

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


class PanelView(StyledComponent):
    """Главный компонент панели с заголовком, тулбаром и содержимым.

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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Добавить заголовок
        title_label = QLabel(title)
        layout.addWidget(title_label)

        # Добавить тулбар если предоставлен
        if toolbar:
            self.toolbar = toolbar
            layout.addWidget(toolbar)

        # Добавить контейнер содержимого
        self.content = PanelContent()
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
