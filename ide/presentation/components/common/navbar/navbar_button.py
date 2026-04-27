from typing import Optional, Self

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QPushButton, QWidget

from ide.presentation.common.mixins import StyledMixin


class NavBarButton(QPushButton, StyledMixin):
    """Кнопка навигационной панели с округлённым индикатором выделения.

    Кнопка отображает иконку и может находиться в выбранном
    или невыбранном состоянии. При выборе слева отображается
    округлённый квадратный индикатор.

    Поддерживает состояние отключения (disabled), при котором
    кнопка не реагирует на клики и отображается полупрозрачной.
    """

    ICON_SIZE = 16
    INDICATOR_SIZE = 3
    INDICATOR_HEIGHT = 16
    INDICATOR_RADIUS = 3
    DISABLED_OPACITY = 0.25

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
        self.setEnabled(True)
        self._is_selected = False

        if icon_path:
            self.icon_path = icon_path
            self.icon_color = QColor("#000")
            self.pixmap: QPixmap = QPixmap(self.icon_path)
            self.setIcon(self.colorize_icon(self.icon_color))

    def colorize_icon(self: Self, color: QColor) -> QIcon:
        """Перекрасить иконку"""
        colored_pixmap = QPixmap(self.pixmap.size())
        colored_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(colored_pixmap)
        painter.drawPixmap(0, 0, self.pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)
        painter.end()

        return QIcon(colored_pixmap)

    def set_selected(self, selected: bool) -> None:
        """Установить состояние выделения кнопки.

        При выборе кнопки отображается округлённый квадратный индикатор
        на левой стороне кнопки.

        Args:
            selected: True если кнопка выбрана, False иначе.
        """
        self._is_selected = selected
        self.update()

    def is_selected(self) -> bool:
        """Получить состояние выделения кнопки.

        Returns:
            True если кнопка выбрана, False иначе.
        """
        return self._is_selected

    def set_enabled(self, enabled: bool) -> None:
        """Установить доступность кнопки.

        При отключении кнопка становится полупрозрачной и не реагирует
        на клики. При включении восстанавливается нормальное состояние.

        Args:
            enabled: True если кнопка доступна, False если отключена.
        """
        self._is_enabled = enabled
        if self._is_enabled:
            self.icon_color = QColor("#000")
        else:
            self.icon_color = QColor("#D6D6D6")
        self.setIcon(self.colorize_icon(self.icon_color))

        self.setClickable(enabled)
        self.update()

    def is_enabled(self) -> bool:
        """Получить состояние доступности кнопки.

        Returns:
            True если кнопка доступна, False если отключена.
        """
        return self._is_enabled

    def setClickable(self, clickable: bool) -> None:
        """Установить возможность клика по кнопке.

        Args:
            clickable: True если кнопка можно кликать, False иначе.
        """
        self.blockSignals(not clickable)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if clickable
            else Qt.CursorShape.ForbiddenCursor
        )

    def paintEvent(self, a0) -> None:
        """Отрисовать кнопку с индикатором выделения и состоянием отключения.

        При выборе отрисовывает округлённый квадратный индикатор на левой стороне.
        При отключении применяется полупрозрачность.

        Args:
            a0: Событие отрисовки PyQt.
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
