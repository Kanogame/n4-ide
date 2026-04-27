from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QWidget

from ide.application.state_manager import ApplicationState, ApplicationStatus


class ErrorHandler(QObject):
    """Обработчик ошибок с отображением диалоговых окон.

    Слушает сигналы status_changed приложения и отображает
    диалоговые окна об ошибках при переходе в состояние ERROR.

    Signals:
        error_shown: Испускается когда диалог об ошибке показан (str).
    """

    error_shown = pyqtSignal(str)

    def __init__(self, parent_widget: Optional[QWidget] = None) -> None:
        """Инициализировать обработчик ошибок.

        Args:
            parent_widget: Родительский виджет для диалогов.
        """
        super().__init__()
        self._parent_widget = parent_widget
        self._last_error_message: str = ""

    def on_status_changed(self, status: ApplicationStatus) -> None:
        """Обработчик изменения статуса приложения.

        Отображает диалог об ошибке при переходе в состояние ERROR.

        Args:
            status: Новый статус приложения.
        """
        if status.state == ApplicationState.ERROR and status.error_message:
            self._last_error_message = status.error_message
            self._show_error_dialog(status.error_message)
            self.error_shown.emit(status.error_message)

    def show_last_error(self) -> None:
        """Показать последнюю сохранённую ошибку.

        Вызывается при клике на иконку статуса, когда приложение в ERROR.
        """
        if self._last_error_message:
            self._show_error_dialog(self._last_error_message)

    def _show_error_dialog(self, error_message: str) -> None:
        """Показать диалоговое окно об ошибке.

        Args:
            error_message: Текст ошибки для отображения.
        """
        QMessageBox.critical(
            self._parent_widget,
            "Ошибка выполнения",
            f"Произошла ошибка:\n\n{error_message}",
            QMessageBox.StandardButton.Ok,
        )

    def get_last_error_message(self) -> str:
        """Получить последнее сообщение об ошибке.

        Returns:
            Текст последней ошибки или пустая строка.
        """
        return self._last_error_message
