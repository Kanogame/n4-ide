"""Вертикальная навигационная панель с ограничением доступа.

Содержит кнопки для переключения между основными разделами приложения.
Поддерживает отключение кнопок в зависимости от состояния приложения.
"""

from typing import Callable, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget

from ide.application.state_manager import ApplicationState
from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.common.mixins import StyledMixin
from ide.presentation.components.common.navbar.nav_item import NavItem, NavItemType
from ide.presentation.components.common.navbar.navbar_button import NavBarButton
from ide.presentation.components.common.navbar.navbar_separator import NavBarSeparator
from ide.presentation.components.common.status_icon import StatusIcon


class NavBar(QFrame, StyledMixin):
    """Вертикальная навигационная панель с ограничением доступа.

    Компонент размещает кнопки в две группы: основную панель и нижнюю,
    разделённые растяжимым пространством. При нажатии на кнопку испускает
    сигнал item_clicked с идентификатором элемента.

    Некоторые кнопки (metrics, visualization) отключены до тех пор,
    пока приложение не находится в состоянии TRAINED.

    Signals:
        item_clicked: Сигнал при нажатии на кнопку навигации (передаёт id).
    """

    item_clicked = pyqtSignal(str)

    WIDTH = 48

    # Кнопки требующие состояния TRAINED
    REQUIRES_TRAINED = {"metrics", "visualization"}

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать навигационную панель.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("navbar.qss")

        self.setFixedWidth(self.WIDTH)

        self._selected_item_id: Optional[str] = None
        self._items: dict[str, NavBarButton] = {}
        self._nav_items: dict[str, NavItem] = {}
        self._status_icon: Optional[StatusIcon] = None
        self._error_callback: Optional[Callable[[], None]] = None

        layout = create_vertical_layout(self)

        # Основная панель для элементов сверху
        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Нижняя панель для элементов снизу
        self._bottom_layout = QVBoxLayout()
        self._bottom_layout.setContentsMargins(0, 0, 0, 0)
        self._bottom_layout.setSpacing(0)

        layout.addLayout(self._main_layout)
        layout.addStretch()
        layout.addLayout(self._bottom_layout)

        self._initialize_items()

    def _initialize_items(self) -> None:
        """Инициализировать все элементы навигационной панели.

        Добавляет кнопки для доступа к основным разделам приложения:
        редактор кода, управление данными, обучение, инспектор модели,
        визуализация графа вычисления. Заменяет Settings на StatusIcon.
        """
        self.add_item(
            NavItem(
                id="code",
                icon_path="assets/icons/code.svg",
                tooltip="Code Editor",
            )
        )

        self.add_item(
            NavItem(
                id="dataset",
                icon_path="assets/icons/dataset.svg",
                tooltip="Dataset Management",
            )
        )

        self.add_item(
            NavItem(
                id="trainer",
                icon_path="assets/icons/training.svg",
                tooltip="Model Trainer",
            )
        )

        self.add_item(
            NavItem(
                id="metrics",
                icon_path="assets/icons/metrics.svg",
                tooltip="Training Metrics",
            )
        )

        self.add_item(
            NavItem(
                id="visualization",
                icon_path="assets/icons/model.svg",
                tooltip="Model Visualization",
            )
        )

        self.add_item(
            NavItem(
                id="sep1",
                icon_path="",
                type=NavItemType.SEPARATOR,
            )
        )

        # Заменить Settings на StatusIcon
        self._status_icon = StatusIcon(
            parent=self,
            on_error_click=self._on_status_error_clicked,
        )
        self._bottom_layout.insertWidget(0, self._status_icon)

    def set_error_callback(self, callback: Callable[[], None]) -> None:
        """Установить callback для показа ошибки при клике на StatusIcon.

        Args:
            callback: Функция для вызова при клике на ошибку.
        """
        self._error_callback = callback
        if self._status_icon:
            self._status_icon._on_error_click = callback

    def add_item(self, item: NavItem) -> None:
        """Добавить элемент в основную секцию навигационной панели.

        Args:
            item: Элемент навигации для добавления.
        """
        if item.type == NavItemType.SEPARATOR:
            separator = NavBarSeparator()
            self._main_layout.addWidget(separator)
            return

        if item.type == NavItemType.SPACER:
            self._main_layout.addStretch()
            return

        button = self._create_nav_button(item)
        self._main_layout.addWidget(button)

    def _create_nav_button(self, item: NavItem) -> NavBarButton:
        """Создать и зарегистрировать кнопку навигации.

        Args:
            item: Элемент навигации для создания кнопки.

        Returns:
            Созданный объект NavBarButton.
        """
        button = NavBarButton(
            icon_path=item.icon_path,
            tooltip=item.tooltip,
        )

        button.clicked.connect(lambda: self._on_item_clicked(item.id))

        # Отключить кнопки требующие TRAINED состояния
        if item.id in self.REQUIRES_TRAINED:
            button.set_enabled(False)

        self._items[item.id] = button
        self._nav_items[item.id] = item

        return button

    def _on_item_clicked(self, item_id: str) -> None:
        """Обработать нажатие на элемент навигации.

        Args:
            item_id: Идентификатор нажатого элемента.
        """
        self._set_selected_item(item_id)
        self.item_clicked.emit(item_id)

    def _on_status_error_clicked(self) -> None:
        """Обработчик клика на StatusIcon в состоянии ERROR."""
        if self._error_callback:
            self._error_callback()

    def _set_selected_item(self, item_id: str) -> None:
        """Обновить визуальное состояние выбранного элемента.

        Args:
            item_id: Идентификатор элемента для выделения.
        """
        if self._selected_item_id and self._selected_item_id in self._items:
            self._items[self._selected_item_id].set_selected(False)

        if item_id in self._items:
            self._selected_item_id = item_id
            self._items[item_id].set_selected(True)

    def get_selected_item_id(self) -> Optional[str]:
        """Получить идентификатор текущего выбранного элемента.

        Returns:
            ID выбранного элемента, или None если элемент не выбран.
        """
        return self._selected_item_id

    def set_selected_item_by_id(self, item_id: str) -> None:
        """Программно выбрать элемент по идентификатору.

        Args:
            item_id: Идентификатор элемента для выбора.
        """
        self._set_selected_item(item_id)

    def update_button_availability(self, application_state: ApplicationState) -> None:
        """Обновить доступность кнопок в зависимости от состояния приложения.

        Args:
            application_state: Состояние приложения.
        """
        is_trained = application_state == ApplicationState.TRAINED

        # Обновить доступность кнопок требующих TRAINED
        for item_id in self.REQUIRES_TRAINED:
            if item_id in self._items:
                self._items[item_id].set_enabled(is_trained)

    def update_status_icon(self, status) -> None:
        """Обновить StatusIcon с новым статусом.

        Args:
            status: ApplicationStatus с текущим состоянием.
        """
        if self._status_icon:
            self._status_icon.set_status(status)
