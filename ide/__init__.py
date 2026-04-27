import sys

from PyQt6.QtWidgets import QApplication

from ide.presentation.views.main_window import MainWindow


class IDE:
    @staticmethod
    def run() -> None:
        """Запустить IDE приложение.

        Инициализирует Qt приложение, создаёт Application слой (состояние),
        показывает главное окно и запускает основной event loop.
        """
        app_qt = QApplication(sys.argv)

        # Создать главное окно (которое инициализирует свой Application слой)
        window = MainWindow()
        window.show()

        sys.exit(app_qt.exec())
