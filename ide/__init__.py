import sys
from PyQt6.QtWidgets import QApplication

from ide.presentation.views.main_window import MainWindow
from ide.application.app import Application


class IDE:
    @staticmethod
    def run() -> None:
        app_qt = QApplication(sys.argv)

        # Инициализировать Application (centralized state)
        app_state = Application()

        # Создать главное окно
        window = MainWindow()
        window.show()

        sys.exit(app_qt.exec())
