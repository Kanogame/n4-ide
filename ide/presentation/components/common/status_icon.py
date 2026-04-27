"""Иконка статуса приложения с информацией об ошибках.

Отображает текущее состояние приложения (idle, training, trained, error)
и позволяет пользователю просмотреть последнюю ошибку при клике.
"""

from pathlib import Path
from typing import Callable, Optional

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget

from ide.application.state_manager import ApplicationState, ApplicationStatus
from ide.presentation.components.common.navbar.navbar_button import NavBarButton


class StatusIcon(NavBarButton):
    """Иконка статуса приложения как кнопка navbar.

    Наследует от NavBarButton для последовательного внешнего вида.
    Отображает иконку текущего состояния приложения:
    - idle.svg: Готовность к обучению
    - training.svg: Процесс обучения
    - trained.svg: Обучение завершено
    - error.svg: Ошибка

    При клике показывает последнюю ошибку (если application в ERROR).

    Attributes:
        ICON_SIZE: Размер иконки в пикселях.
        ICONS_DIR: Директория с файлами иконок.
    """

    ICON_SIZE = 16
    ICONS_DIR = Path("assets/icons/status")

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        on_error_click: Optional[Callable[[], None]] = None,
    ) -> None:
        """Инициализировать иконку статуса.

        Args:
            parent: Родительский виджет.
            on_error_click: Callback при клике на иконку в состоянии ERROR.
        """
        # Инициализировать с пустой иконкой (будет установлена при set_status)
        super().__init__(
            icon_path="",
            tooltip="Статус приложения",
            parent=parent,
        )

        # Callback при клике на ошибку
        self._on_error_click = on_error_click
        self._current_status = ApplicationStatus(state=ApplicationState.IDLE)

        # Подключить обработчик клика для STATUS-специфичной логики
        self.clicked.connect(self._on_clicked)

        # Инициализировать с idle иконкой
        self._update_icon(ApplicationState.IDLE)

    def set_status(self, status: ApplicationStatus) -> None:
        """Обновить статус и иконку.

        Args:
            status: Новый статус приложения.
        """
        self._current_status = status
        self._update_icon(status.state)

        # Обновить подсказку
        tooltip = self._get_tooltip(status)
        self.setToolTip(tooltip)

    def _update_icon(self, state: ApplicationState) -> None:
        """Обновить иконку по состоянию.

        Args:
            state: Состояние приложения.
        """
        icon_name = self._get_icon_name(state)
        icon_path = self.ICONS_DIR / f"{icon_name}.svg"

        # Загрузить иконку если существует
        if icon_path.exists():
            self.setIcon(QIcon(str(icon_path)))
        else:
            # Иначе установить пустую иконку
            self.setIcon(QIcon())

    def _get_icon_name(self, state: ApplicationState) -> str:
        """Получить имя файла иконки по состоянию.

        Args:
            state: Состояние приложения.

        Returns:
            Имя файла иконки (без расширения).
        """
        icon_map = {
            ApplicationState.IDLE: "idle",
            ApplicationState.TRAINING: "training",
            ApplicationState.TRAINED: "trained",
            ApplicationState.ERROR: "error",
        }
        return icon_map.get(state, "idle")

    def _get_tooltip(self, status: ApplicationStatus) -> str:
        """Получить текст подсказки по статусу.

        Args:
            status: Статус приложения.

        Returns:
            Текст подсказки для отображения.
        """
        state_names = {
            ApplicationState.IDLE: "Готовность",
            ApplicationState.TRAINING: "Обучение...",
            ApplicationState.TRAINED: "Обучено",
            ApplicationState.ERROR: "Ошибка",
        }

        text = state_names.get(status.state, "Неизвестно")

        # Добавить информацию об ошибке если есть
        if status.state == ApplicationState.ERROR and status.error_message:
            # Обрезать длинные сообщения
            error = status.error_message[:100]
            if len(status.error_message) > 100:
                error += "..."
            text += f"\n\nКликните для деталей:\n{error}"

        return text

    def _on_clicked(self) -> None:
        """Обработчик клика на иконку."""
        # Если в состоянии ERROR, вызвать callback
        if self._current_status.state == ApplicationState.ERROR:
            if self._on_error_click:
                self._on_error_click()
