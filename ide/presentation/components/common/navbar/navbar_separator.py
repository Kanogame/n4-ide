from ide.presentation.common.styled_widget import StyledComponent
from typing import Optional
from PyQt6.QtWidgets import QWidget


class NavBarSeparator(StyledComponent):
    """Горизонтальный разделитель для навигационной панели.

    Компонент отображается как тонкая горизонтальная линия
    и используется для визуального разделения групп элементов.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать разделитель навигационной панели.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent, "navbar.qss")
        self.setObjectName("NavBarSeparator")
        self.setFixedHeight(1)
