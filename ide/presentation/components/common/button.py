"""Кнопка для N4-IDE с поддержкой стилевых вариантов."""

from enum import Enum, auto
from typing import Optional

from PyQt6.QtWidgets import QPushButton, QWidget

from ide.presentation.common.mixins import StyledMixin, FontMixin


class ButtonStyle(Enum):
    """Варианты стилей кнопки."""

    ACCENT = auto()  # Синяя основная кнопка
    SECONDARY = auto()  # Кнопка с лёгкой границей
    DANGER = auto()  # Красная кнопка для деструктивных действий
    GHOST = auto()  # Кнопка без фона


class Button(QPushButton, StyledMixin, FontMixin):
    """Стилизованная кнопка, соответствующая дизайн-системе N4-IDE.

    Поддерживает несколько вариантов стилей через перечисление ButtonStyle.
    Стили загружаются из QSS файла и применяются через объектные имена.

    Атрибуты:
        style_variant: Текущий выбранный стиль кнопки (ButtonStyle).
    """

    def __init__(
        self,
        text: str = "",
        style: ButtonStyle = ButtonStyle.ACCENT,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать кнопку.

        Args:
            text: Текст, отображаемый на кнопке.
            style: Вариант стиля из ButtonStyle.
            parent: Родительский виджет.
        """
        super().__init__(text, parent)
        self._apply_style("button.qss")
        self._apply_font(12)

        # Сохранить выбранный стиль
        self.style_variant = style

        # Установить объектное имя для селектора QSS
        self._set_style_class()

    def _set_style_class(self) -> None:
        """Установить объектное имя для соответствующего QSS класса."""
        # Объектные имена используются в QSS селекторах
        if self.style_variant == ButtonStyle.ACCENT:
            self.setObjectName("ButtonAccent")
        elif self.style_variant == ButtonStyle.SECONDARY:
            self.setObjectName("ButtonSecondary")
        elif self.style_variant == ButtonStyle.DANGER:
            self.setObjectName("ButtonDanger")
        else:  # GHOST
            self.setObjectName("ButtonGhost")

    def set_style(self, style: ButtonStyle) -> None:
        """Изменить вариант стиля кнопки.

        Args:
            style: Новый вариант стиля из ButtonStyle.
        """
        self.style_variant = style
        self._set_style_class()
