from typing import Optional, Self

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMenu,
    QToolBar,
    QToolButton,
    QWidget,
)

from ide.presentation.common.layouts import create_horizontal_layout
from ide.presentation.common.mixins import StyledMixin


class MenuContainer(QWidget):
    """Контейнер для размещения меню в тулбаре."""

    def __init__(self: Self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать контейнер с горизонтальным макетом."""
        super().__init__(parent)
        hbox = create_horizontal_layout(self)
        self._hbox = hbox

    def add_menu(self: Self, menu: QMenu) -> None:
        """Добавить меню в контейнер.

        Args:
            menu: Меню для добавления.
        """

        button = QToolButton()
        button.setText(menu.title())
        button.setObjectName(menu.objectName())
        button.setMenu(menu)
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._hbox.addWidget(button)


class PanelToolbar(QToolBar, StyledMixin):
    """Тулбар панели с меню для управления действиями.

    Компонент предоставляет меню инструментов для работы с файлами
    и редактированием кода. Наследуется от QToolBar с StyledMixin.

    Сигналы:
        new_file_requested: Создать новый файл.
        open_file_requested: Открыть файл.
        save_file_requested: Сохранить текущий файл.
        save_as_file_requested: Сохранить файл как...
        undo_requested: Отменить последнее действие.
        redo_requested: Повторить отменённое действие.
    """

    # Сигналы для работы с файлами
    new_file_requested = pyqtSignal()
    open_file_requested = pyqtSignal()
    save_file_requested = pyqtSignal()
    save_as_file_requested = pyqtSignal()

    # Сигналы для редактирования
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()

    def __init__(self: Self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать тулбар панели с меню.

        Args:
            parent: Родительский виджет.
        """
        super().__init__("Панель модели", parent)
        self._apply_style("panel_toolbar.qss")

        self.setObjectName("PanelToolbar")
        self.setMovable(False)

        # Создать контейнер для меню
        menu_container = MenuContainer(self)

        # Создать меню файлов и редактирования
        self._create_file_menu(menu_container)
        self._create_edit_menu(menu_container)

        # Добавить контейнер в тулбар
        self.addWidget(menu_container)

    def _create_file_menu(self: Self, container: MenuContainer) -> None:
        """Создать меню 'Файл' с действиями.

        Args:
            container: Контейнер для добавления меню.
        """
        file_menu = QMenu("Файл", self)
        file_menu.setObjectName("FileMenu")

        # Действие: новый файл
        self.new_action = QAction("Новый файл", self)
        self.new_action.setObjectName("NewFileAction")
        self.new_action.triggered.connect(self.new_file_requested.emit)
        file_menu.addAction(self.new_action)

        # Действие: открыть файл
        self.open_action = QAction("Открыть файл", self)
        self.open_action.setObjectName("OpenFileAction")
        self.open_action.triggered.connect(self.open_file_requested.emit)
        file_menu.addAction(self.open_action)

        file_menu.addSeparator()

        # Действие: сохранить файл
        self.save_action = QAction("Сохранить", self)
        self.save_action.setObjectName("SaveAction")
        self.save_action.triggered.connect(self.save_file_requested.emit)
        file_menu.addAction(self.save_action)

        # Действие: сохранить как
        self.save_as_action = QAction("Сохранить как...", self)
        self.save_as_action.setObjectName("SaveAsAction")
        self.save_as_action.triggered.connect(self.save_as_file_requested.emit)
        file_menu.addAction(self.save_as_action)

        container.add_menu(file_menu)

    def _create_edit_menu(self: Self, container: MenuContainer) -> None:
        """Создать меню 'Правка' с действиями редактирования.

        Args:
            container: Контейнер для добавления меню.
        """
        edit_menu = QMenu("Правка", self)
        edit_menu.setObjectName("EditMenu")

        # Действие: отменить
        self.undo_action = QAction("Отменить", self)
        self.undo_action.setObjectName("UndoAction")
        self.undo_action.triggered.connect(self.undo_requested.emit)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)

        # Действие: повторить
        self.redo_action = QAction("Повторить", self)
        self.redo_action.setObjectName("RedoAction")
        self.redo_action.triggered.connect(self.redo_requested.emit)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)

        container.add_menu(edit_menu)

    def set_undo_enabled(self: Self, enabled: bool) -> None:
        """Включить/выключить действие отмены.

        Args:
            enabled: Флаг включения.
        """
        self.undo_action.setEnabled(enabled)

    def set_redo_enabled(self: Self, enabled: bool) -> None:
        """Включить/выключить действие повтора.

        Args:
            enabled: Флаг включения.
        """
        self.redo_action.setEnabled(enabled)
