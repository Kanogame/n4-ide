from typing import Optional, Self
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QSize, QRect, Qt
from PyQt6.QtGui import QIcon, QPainter, QColor, QPaintEvent

from ide.presentation.common.styled_widget import StyledMixin


class NavBarButton(QPushButton, StyledMixin):
    """Кнопка навигационной панели с округлённым индикатором выделения.

    Кнопка отображает иконку и может находиться в выбранном
    или невыбранном состоянии. При выборе слева отображается
    округлённый квадратный индикатор.
    """

    ICON_SIZE = 16
    INDICATOR_SIZE = 3
    INDICATOR_HEIGHT = 16
    INDICATOR_RADIUS = 3

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

        При выборе кнопки отображается округлённый квадратный индикатор
        на левой стороне кнопки.

        Args:
            selected: True если кнопка выбрана, False иначе.
        """
        self._is_selected = selected
        self.update()

    def is_selected(self: Self) -> bool:
        """Получить состояние выделения кнопки.

        Returns:
            True если кнопка выбрана, False иначе.
        """
        return self._is_selected

    def paintEvent(self: Self, a0: Optional[QPaintEvent]) -> None:
        """
        Отрисовать кнопку с индикатором выделения.

        При выборе отрисовывает округлённый квадратный индикатор на левой стороне кнопки.
        Аля windows task manager

        Args:
            a0 (event): Событие отрисовки PyQt.
        """
        # Вызвать стандартную отрисовку кнопки
        super().paintEvent(a0)

        # Если кнопка выбрана, отрисовать индикатор
        if self._is_selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            x = 0
            y = (self.height() - self.INDICATOR_HEIGHT) // 2

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#005FB8"))
            painter.drawRoundedRect(
                QRect(x, y, self.INDICATOR_SIZE, self.INDICATOR_HEIGHT),
                self.INDICATOR_RADIUS,
                self.INDICATOR_RADIUS,
            )

            painter.end()
