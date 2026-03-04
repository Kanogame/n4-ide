from PyQt6.QtCore import Qt
from typing import Self
from PyQt6.QtWidgets import QMainWindow, QSplitter, QTabWidget, QWidget

class MainWindow(QMainWindow):
    def __init__(self: Self):
        super().__init__()

        self.main_splitter: QSplitter = QSplitter(Qt.Orientation.Vertical)
        self.top_splitter: QSplitter = QSplitter(Qt.Orientation.Horizontal)

        self.bottom_tabs: QTabWidget = QTabWidget()


        self.editor_container: QWidget = QWidget()
        self.graph_container: QWidget = QWidget()

        self.top_splitter.addWidget(self.editor_container)
        self.top_splitter.addWidget(self.graph_container)

        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.bottom_tabs)


        self.top_splitter.setStretchFactor(0, 3)
        self.top_splitter.setStretchFactor(1, 4)

        self.main_splitter.setStretchFactor(0, 4)
        self.main_splitter.setStretchFactor(1, 1)

        self.top_splitter.setChildrenCollapsible(False)
        self.main_splitter.setChildrenCollapsible(False)

        self.setCentralWidget(self.main_splitter)


        self.setWindowTitle("ide")
        self.resize(1400, 900)

        self.show()

