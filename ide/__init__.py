from .ui.main_window import MainWindow
import sys
from PyQt6.QtWidgets import QApplication

class IDE:
    def run():
        # initialization of qt window
        app = QApplication(sys.argv)

        window = MainWindow()
        window.show()
    
        sys.exit(app.exec())