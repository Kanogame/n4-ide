from n4.nn import Model
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from ide.domain.execution.controller import ExecutionController


class ModelManager(QObject):
    """Управляет состоянием модели в приложении.

    Отвечает за загрузку модели из кода, валидацию и сохранение состояния.
    Emits сигналы об изменениях состояния для обновления UI.
    """

    # Сигналы об изменениях состояния
    model_loaded = pyqtSignal(type)
    model_validation_started = pyqtSignal()
    model_validation_failed = pyqtSignal(str)
    backend_changed = pyqtSignal(str)

    def __init__(self, execution_controller: ExecutionController) -> None:
        """Инициализировать менеджер моделей.

        Args:
            execution_controller: Контроллер выполнения кода.
        """
        super().__init__()
        self._model: Optional[type[Model]] = None
        self._selected_backend: str = "PyFloat"
        self._execution_controller = execution_controller

    def load_model_from_code(self, model_code: str) -> None:
        """Загрузить модель из кода.

        Выполняет код с выбранным backend и извлекает класс модели.

        Args:
            model_code: Строка с кодом модели.
        """
        self.model_validation_started.emit()

        try:
            # Выполнить код с текущим backend
            namespace = self._execution_controller.run(
                model_code, self._selected_backend
            )

            # Извлечь и валидировать класс модели
            model_class = self._execution_controller.extract_and_validate_model(
                namespace
            )

            # Сохранить модель и emit сигнал
            self._model = model_class
            self.model_loaded.emit(model_class)

        except Exception as e:
            self.model_validation_failed.emit(str(e))

    def set_backend(self, backend: str) -> None:
        """Установить вычислительный backend.

        Args:
            backend: Название backend (PyFloat, NumPy, PyTorch).
        """
        self._selected_backend = backend
        self.backend_changed.emit(backend)

    def get_backend(self) -> str:
        """Получить выбранный backend.

        Returns:
            Название выбранного backend.
        """
        return self._selected_backend

    def get_current_model(self) -> Optional[type[Model]]:
        """Получить текущую загруженную модель.

        Returns:
            Класс модели или None, если не загружена.
        """
        return self._model

    def has_model(self) -> bool:
        """Проверить наличие загруженной модели.

        Returns:
            True если модель загружена, False иначе.
        """
        return self._model is not None

    def clear_model(self) -> None:
        """Очистить текущую модель."""
        self._model = None
