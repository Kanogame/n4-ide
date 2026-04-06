from pathlib import Path

from typing import Optional, Self
from PyQt6.QtWidgets import QWidget, QMainWindow


class StyledMixin:
    """
    Миксин для стилизации виджета с загрузкой QSS стиля

    Важно: не работает с QWidget, так как у этого базового виждета нет реализации с отрисовкой стилей
    Рекомендовано использовать с QFrame
    """

    @staticmethod
    def _resolve_stylesheet_path(stylesheet_name: Optional[str]) -> Optional[Path]:
        """Разрешить абсолютный путь к файлу стиля компонента.

        Args:
            stylesheet_name: Имя файла стиля (например, "panel.qss"), или None.

        Returns:
            Абсолютный путь к файлу стиля, или None если stylesheet_name = None.
        """
        if stylesheet_name is None:
            return None

        # Получить директорию пакета ide/
        ide_root = Path("ide")
        stylesheet_path = ide_root / "styles" / "components" / stylesheet_name

        if not stylesheet_path.exists():
            print(f"Предупреждение: Файл стиля не найден: {stylesheet_path}")

        return stylesheet_path

    def _apply_style(self: Self, stylesheet_name: str) -> None:
        """Применить новый стиль к компоненту.

        Args:
            stylesheet_name: Имя файла QSS в ide/styles/components/.
        """
        stylesheet_path = self._resolve_stylesheet_path(stylesheet_name)
        self._load_stylesheet(stylesheet_path)

    def _load_stylesheet(self: Self, stylesheet_path: Optional[Path]) -> None:
        """Загрузить и применить QSS-стиль к виджету.

        Args:
            stylesheet_path: Абсолютный путь к файлу QSS, или None.
        """
        if stylesheet_path is None:
            return

        try:
            with open(stylesheet_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())  # type: ignore
        except FileNotFoundError:
            print(f"Предупреждение: Файл стиля не найден: {stylesheet_path}")


class StyledMainWindow(QMainWindow):
    """Базовый класс главного окна с автоматической загрузкой QSS-стилей.

    Применяется только для представлений (views), загружает стили из
    ide/styles/views/main_window.qss.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать главное окно и загрузить стиль.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        stylesheet_path = self._resolve_stylesheet_path()
        self._load_stylesheet(stylesheet_path)

    @staticmethod
    def _resolve_stylesheet_path() -> Path:
        """Разрешить абсолютный путь к главному стилю окна.

        Returns:
            Абсолютный путь к ide/styles/views/main_window.qss.
        """
        ide_root = Path("ide")
        return ide_root / "styles" / "views" / "main_window.qss"

    def _load_stylesheet(self, stylesheet_path: Path) -> None:
        """Загрузить и применить QSS-стиль к главному окну.

        Args:
            stylesheet_path: Абсолютный путь к файлу QSS.
        """
        try:
            with open(stylesheet_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Предупреждение: Файл стиля не найден: {stylesheet_path}")
