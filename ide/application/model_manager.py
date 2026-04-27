from n4.nn import Model
from n4.numeric import NumericProtocol
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from ide.domain.execution.controller import ExecutionController
from ide.domain.backend import get_backend_registry


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
        self._registry = get_backend_registry()
        self._backend_type: type[NumericProtocol] = self._registry.get_default()
        self._execution_controller = execution_controller

    def load_model_from_code(self, model_code: str) -> None:
        """Загрузить модель из кода.

        Выполняет код с выбранным backend и извлекает класс модели.

        Args:
            model_code: Строка с кодом модели.
        """
        self.model_validation_started.emit()

        try:
            namespace = self._execution_controller.run(
                model_code, self._backend_type
            )

            model_class = self._execution_controller.extract_and_validate_model(
                namespace
            )

            self._model = model_class
            self.model_loaded.emit(model_class)

        except Exception as e:
            self.model_validation_failed.emit(str(e))

    def set_backend(self, display_name: str) -> None:
        """Установить вычислительный backend по отображаемому имени.

        Args:
            display_name: Отображаемое имя backend из реестра.

        Raises:
            KeyError: Если backend с таким именем не зарегистрирован.
        """
        try:
            self._backend_type = self._registry.get_class(display_name)
        except KeyError:
            self.model_validation_failed.emit(f"Unknown backend: {display_name!r}")
            return
        self.backend_changed.emit(display_name)

    def get_backend_type(self) -> type[NumericProtocol]:
        """Получить класс выбранного backend.

        Returns:
            Класс backend (например PyFloat, NumpyFloat).
        """
        return self._backend_type

    def get_backend_name(self) -> str:
        """Получить отображаемое имя выбранного backend.

        Returns:
            Отображаемое имя backend из реестра.
        """
        name = self._registry.get_display_name(self._backend_type)
        return name if name is not None else self._backend_type.__name__

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
