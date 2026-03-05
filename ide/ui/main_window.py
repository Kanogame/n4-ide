from PyQt6.QtCore import Qt
from typing import Self

from .widgets.editor_widget import EditorWidget
from .widgets.graph_view import GraphView
from .widgets.console_widget import ConsoleWidget
from .widgets.dataset_panel import DatasetPanel
from .widgets.weights_table import WeightsTable
from PyQt6.QtWidgets import QMainWindow, QSplitter, QTabWidget, QWidget, QToolBar, QVBoxLayout

class MainWindow(QMainWindow):
    """Главное окно IDE"""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("N4 IDE Prototype")
        self.resize(1400, 900)

        self._build_ui()

    def _build_ui(self) -> None:
        """Создание интерфейса"""

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Центральный виджет
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        self.setCentralWidget(central_widget)

        # Главный вертикальный splitter
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Верхний splitter (editor + graph)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.editor = EditorWidget()
        self.graph = GraphView()

        top_splitter.addWidget(self.editor)
        top_splitter.addWidget(self.graph)

        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 4)

        # Нижние вкладки
        bottom_tabs = QTabWidget()

        self.console = ConsoleWidget()
        self.dataset = DatasetPanel()
        self.weights = WeightsTable()

        bottom_tabs.addTab(self.console, "Console")
        bottom_tabs.addTab(self.weights, "Weights")
        bottom_tabs.addTab(self.dataset, "Dataset")

        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_tabs)

        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)

        central_layout.addWidget(main_splitter)