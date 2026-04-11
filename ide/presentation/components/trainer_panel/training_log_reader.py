from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.common.mixins import StyledMixin
import logging
from typing import Optional, Self

from PyQt6.QtWidgets import (
    QWidget,
    QTextEdit,
    QHBoxLayout,
    QFrame,
)
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QFont, QTextCursor


class QtLogHandler(QObject, logging.Handler):
    """Обработчик логирования для передачи сообщений в Qt сигналы.

    Позволяет направлять вывод логгера в Qt интерфейс без
    блокирования основного потока.
    """

    # Сигнал при получении нового лога.
    log_emitted = pyqtSignal(str)

    def __init__(self: Self) -> None:
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        """Вызывается логгером при появлении нового сообщения.

        Args:
            record: Запись логирования с информацией о событии.
        """
        try:
            msg = self.format(record)
            self.log_emitted.emit(msg)
        except Exception:
            # Игнорировать ошибки в логировании
            pass


class TrainingLogReader(QFrame, StyledMixin):
    """Интерактивное поле для отображения логов обучения с копированием.

    Компонент отображает вывод обучения модели в прокручиваемой области
    и предоставляет кнопку для копирования содержимого в буфер обмена.

    Signals:
        Нет сигналов; компонент только потребляет логи.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать логировщик обучения.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("training_log_reader.qss")

        main_layout = create_vertical_layout(self, 8)

        # Создать текстовое поле для логов
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setObjectName("TrainingLogReader")

        # Настроить шрифт для логов
        font = QFont("Droid Sans Mono", 10)
        self.log_text_edit.setFont(font)

        main_layout.addWidget(self.log_text_edit)

        # Нижняя панель с кнопками
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 10, 10)
        button_layout.setSpacing(10)
        button_layout.addStretch()

        # Кнопка копирования текста
        self.copy_button = Button("Копировать")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_button)

        # Кнопка очистки логов
        self.clear_button = Button("Очистить", ButtonStyle.SECONDARY)
        self.clear_button.clicked.connect(self._clear_logs)
        button_layout.addWidget(self.clear_button)

        main_layout.addLayout(button_layout)

    def append_log(self, message: str) -> None:
        """Добавить сообщение в логи.

        Добавляет сообщение в конец текста и прокручивает до конца.

        Args:
            message: Текст сообщения для добавления.
        """
        self.log_text_edit.append(message)

        # Прокрутить до конца
        cursor = self.log_text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text_edit.setTextCursor(cursor)

    def get_log_text(self) -> str:
        """Получить весь текст логов.

        Returns:
            Полный текст всех логов.
        """
        return self.log_text_edit.toPlainText()

    def _copy_to_clipboard(self) -> None:
        """Скопировать все логи в буфер обмена."""
        from PyQt6.QtWidgets import QApplication

        text = self.get_log_text()
        if text:
            clipboard = QApplication.clipboard()
            if clipboard is not None:
                clipboard.setText(text)

    def _clear_logs(self) -> None:
        """Очистить все логи."""
        self.log_text_edit.clear()

    @staticmethod
    def create_logger(name: str) -> logging.Logger:
        """Создать логгер сQt обработчиком.

        Args:
            name: Имя логгера.

        Returns:
            Логгер с подключённым Qt обработчиком.
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Удалить существующие обработчики
        logger.handlers.clear()

        # Создать и подключить Qt обработчик
        handler = QtLogHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger
