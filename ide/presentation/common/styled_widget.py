"""
Base widget class with automatic stylesheet loading.

Provides a consistent pattern for loading QSS stylesheets from files
relative to the ide/styles/components/ directory.
"""

from pathlib import Path

from typing import Optional, Self
from PyQt6.QtWidgets import QWidget, QMainWindow


class StyledWidget(QWidget):
    """
    Виджет-base class с автоматической загрузкой QSS-стилей
    """

    def __init__(
        self, parent: Optional[QWidget] = None, stylesheet_path: Optional[Path] = None
    ) -> None:
        super().__init__(parent)
        self._load_stylesheet(stylesheet_path)

    def _load_stylesheet(self, stylesheet_path: Optional[Path]) -> None:
        if stylesheet_path is None:
            return

        with open(stylesheet_path, "r") as f:
            self.setStyleSheet(f.read())


class StyledComponent(StyledWidget):
    """
    Виджет-base class с автоматической загрузкой QSS-стилей

    Применяется только для компонентов
    """

    def __init__(
        self, parent: Optional[QWidget] = None, stylesheet_name: Optional[str] = None
    ) -> None:
        super().__init__(
            parent,
            Path(f"ide/styles/components/{stylesheet_name}")
            if stylesheet_name
            else None,
        )

    def _apply_style(self: Self, stylesheet_name: str) -> None:
        self._load_stylesheet(Path(f"ide/styles/components/{stylesheet_name}"))


class StyledMainWindow(QMainWindow):
    """
    Виджет-base class с автоматической загрузкой QSS-стилей

    Применяется только для представлений
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        with open(Path("ide/styles/views/main_window.qss"), "r") as f:
            self.setStyleSheet(f.read())
