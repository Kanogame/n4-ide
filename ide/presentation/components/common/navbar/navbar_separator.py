from typing import Optional

from PyQt6.QtWidgets import QFrame, QWidget

from ide.presentation.common.mixins import StyledMixin


class NavBarSeparator(QFrame, StyledMixin):
    """Горизонтальный разделитель для навигационной панели.

    Компонент отображается как тонкая горизонтальная линия
    и используется для визуального разделения групп элементов.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать разделитель навигационной панели.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("navbar.qss")
        self.setFixedHeight(1)
