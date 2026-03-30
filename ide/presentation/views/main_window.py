"""
Main window for N4-IDE.

Provides the overall application layout with navbar, editor, graph, and bottom panels.
Integrates styled components and navbar following N4-IDE architecture.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QSplitter,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from ide.presentation.components.editor_widget import EditorWidget
from ide.presentation.components.graph_view import GraphView
from ide.presentation.components.console_widget import ConsoleWidget
from ide.presentation.components.dataset_panel import DatasetPanel
from ide.presentation.components.weights_table import WeightsTable
from ide.presentation.components.debug_panel import DebugPanel
from ide.presentation.components.model_view import ModelView
from ide.presentation.components.navbar import NavBar
from ide.presentation.common.styled_widget import StyledMainWindow


class MainWindow(StyledMainWindow):
    """Main N4-IDE window with collapsible navbar and tab-based panels.

    Architecture:
    - Left sidebar: Icon-based collapsible navbar
    - Center: Editor + Graph visualization (splitter)
    - Bottom: Tabbed panels (Console, Weights, Dataset, Debug, Model)

    All components communicate via signals, following presentation layer principles.
    """

    def __init__(self) -> None:
        super().__init__(
            None,
        )

        self.setWindowTitle("N4 IDE")
        self.resize(1600, 900)

        self._build_ui()

    def _build_ui(self) -> None:
        """Build main application interface."""

        # Central layout with navbar + main content
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar navbar
        self.navbar = NavBar()
        self._setup_navbar()
        main_layout.addWidget(self.navbar)

        # Main content area with splitters
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top area: Editor + Graph (horizontal splitter)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.editor = EditorWidget()
        self.graph = GraphView()

        top_splitter.addWidget(self.editor)
        top_splitter.addWidget(self.graph)
        top_splitter.setStretchFactor(0, 3)
        top_splitter.setStretchFactor(1, 4)

        # Bottom area: Tabbed panels
        self.bottom_tabs = QTabWidget()

        self.console = ConsoleWidget()
        self.weights = WeightsTable()
        self.dataset = DatasetPanel()
        self.debug_panel = DebugPanel()
        self.model_view = ModelView()

        self.bottom_tabs.addTab(self.model_view, "Model")
        self.bottom_tabs.addTab(self.console, "Console")
        self.bottom_tabs.addTab(self.weights, "Weights")
        self.bottom_tabs.addTab(self.dataset, "Dataset")
        self.bottom_tabs.addTab(self.debug_panel, "Debug")

        # Vertical splitter for top and bottom areas
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self.bottom_tabs)
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)

        content_layout.addWidget(main_splitter)

        # Add navbar + content to main widget
        main_widget.setLayout(main_layout)
        main_layout.addLayout(content_layout, 1)

        self.setCentralWidget(main_widget)

    def _setup_navbar(self) -> None:
        """Configure navbar items and connections.

        Icon paths must exist in assets/icons/ directory.
        Only the following icons are available:
        - code.svg
        - graph.svg
        - training.svg
        - model.svg
        - dataset.svg
        """

        # Main navigation items

        # Connect navbar signals
        self.navbar.item_clicked.connect(self._on_navbar_item_clicked)
        self.navbar.set_selected_item_by_id("editor")

    def _on_navbar_item_clicked(self, item_id: str) -> None:
        """Handle navbar item selection.

        Args:
            item_id: ID of selected navbar item
        """
        # Map navbar items to bottom tabs
        tab_mapping = {
            "editor": -1,  # Editor stays visible
            "graph": -1,  # Graph stays visible
            "training": 0,  # Model tab
            "debug": 4,  # Debug tab
            "inspector": 2,  # Weights/Inspector tab
            "settings": -1,  # Settings (implement later)
        }

        if item_id in tab_mapping and tab_mapping[item_id] >= 0:
            self.bottom_tabs.setCurrentIndex(tab_mapping[item_id])
