from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QTabWidget,
    QWidget,
    QToolBar,
    QVBoxLayout,
)

from ide.presentation.components.editor_widget import EditorWidget
from ide.presentation.components.graph_view import GraphView
from ide.presentation.components.console_widget import ConsoleWidget
from ide.presentation.components.dataset_panel import DatasetPanel
from ide.presentation.components.weights_table import WeightsTable
from ide.presentation.components.debug_panel import DebugPanel


class MainWindow(QMainWindow):
    """Главное окно IDE"""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("N4 IDE Prototype")
        self.resize(1400, 900)

        self._build_ui()

    def _build_ui(self) -> None:
        """Построить интерфейс приложения."""

        # Панель инструментов
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Центральный виджет с основным макетом
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Основной вертикальный разделитель
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Верхний горизонтальный разделитель (редактор + граф)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.editor = EditorWidget()
        self.graph = GraphView()

        top_splitter.addWidget(self.editor)
        top_splitter.addWidget(self.graph)

        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 4)

        # Нижние вкладки с консолью, параметрами и датасетом
        bottom_tabs = QTabWidget()

        self.console = ConsoleWidget()
        self.weights = WeightsTable()
        self.dataset = DatasetPanel()
        self.debug_panel = DebugPanel()

        bottom_tabs.addTab(self.console, "Console")
        bottom_tabs.addTab(self.weights, "Weights")
        bottom_tabs.addTab(self.dataset, "Dataset")
        bottom_tabs.addTab(self.debug_panel, "Debug")

        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_tabs)

        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)

        central_layout.addWidget(main_splitter)
