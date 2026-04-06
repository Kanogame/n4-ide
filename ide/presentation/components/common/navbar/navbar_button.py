from typing import Optional, Self
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

from ide.presentation.common.styled_widget import StyledComponent


class NavBarButton(QPushButton, StyledComponent):
    """Кнопка навигационной панели с прямоугольником выделения.

    Кнопка отображает иконку и может находиться в выбранном
    или невыбранном состоянии. При нажатии испускает сигнал.
    """

    ICON_SIZE = 16

    def __init__(
        self,
        icon_path: str,
        tooltip: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать кнопку навигационной панели.

        Args:
            icon_path: Путь к файлу иконки (SVG/PNG).
            tooltip: Текст подсказки при наведении мыши.
            parent: Родительский виджет.
        """
        QPushButton.__init__(self, parent)
        self._apply_style("navbar_button.qss")

        self.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.setText("")
        self.setToolTip(tooltip)

        if icon_path:
            self.setIcon(QIcon(icon_path))

        self._is_selected = False

    def set_selected(self: Self, selected: bool) -> None:
        """Установить состояние выделения кнопки.

        При выборе кнопки отображается индикаторная полоса слева.
        Состояние отражается через CSS-класс в QSS-стилях.

        Args:
            selected: True если кнопка выбрана, False иначе.
        """
        self._is_selected = selected

        # Обновить стиль в зависимости от состояния выделения
        if selected:
            self.setProperty("selected", True)
        else:
            self.setProperty("selected", False)

        # Переприменить стиль для обновления внешнего вида
        style = self.style()
        if style is not None:
            style.polish(self)

    def is_selected(self: Self) -> bool:
        """Получить состояние выделения кнопки.

        Returns:
            True если кнопка выбрана, False иначе.
        """
        return self._is_selected
