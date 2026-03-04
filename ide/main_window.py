from typing import Self
from PyQt6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self: Self):
        super().__init__()

        self.setWindowTitle("ide")

        self.show()

