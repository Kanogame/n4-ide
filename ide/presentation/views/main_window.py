from typing import Self
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QSplitter,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
)

from ide.presentation.components.graph_view import GraphView
from ide.presentation.components.console_widget import ConsoleWidget
from ide.presentation.components.dataset_panel import DatasetPanel
from ide.presentation.components.weights_table import WeightsTable
from ide.presentation.components.debug_panel import DebugPanel
from ide.presentation.components.model_panel_view import ModelPanelView
from ide.presentation.components.navbar import NavBar
from ide.presentation.common.styled_widget import StyledMainWindow


class MainWindow(StyledMainWindow):
    """
    Главное окно приложение, содержит navbar слева, а также главную панель

    Все компоненты коммуницируют через сигналы
    """

    def __init__(self) -> None:
        super().__init__(
            None,
        )

        self.setWindowTitle("N4 IDE")
        self.resize(1600, 900)

        self._build_ui()

    def _build_ui(self) -> None:
        """Собрать главный интерфейс"""

        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Navbar слева
        self.setup_nabar()

        # Панель справа
        self.setup_panel_view()

        # Создание всех разделов
        self.setup_tabs()

        # Установить главный виджет
        self.setCentralWidget(main_widget)

    def setup_nabar(self: Self) -> None:
        self.navbar = NavBar()

        # Подключаем сигнал в _on_navbar_item_clicked
        self.navbar.item_clicked.connect(self._on_navbar_item_clicked)

        # Устанавливаем редактор кода как начальный раздел
        self.navbar.set_selected_item_by_id("code")
        self.main_layout.addWidget(self.navbar)

    def setup_panel_view(self: Self) -> None:
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.main_layout.addLayout(self.content_layout)

    def setup_tabs(self: Self) -> None:

        # Используем QStackedWidget чтобы быстро и легко
        # менять разделы через setCurrentIndex
        self.stacked = QStackedWidget()

        self.model_view = ModelPanelView()
        self.stacked.addWidget(self.model_view)

        self.dataset = DatasetPanel()
        self.stacked.addWidget(self.dataset)

        self.content_layout.addWidget(self.stacked)

    def _on_navbar_item_clicked(self, item_id: str) -> None:
        """
        Обработчик сигнала кнопки navbar
        """

        # Мапим названия панелей к их id в stacked виджете
        item_id_mapping = {
            "code": 0,
            "dataset": 1,
        }

        # Вызываем смену
        self.stacked.setCurrentIndex(item_id_mapping[item_id])
