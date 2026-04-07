from dataclasses import dataclass, field
from typing import Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass(frozen=True)
class ExecutionResult:
    """Неизменяемый результат выполнения кода."""

    success: bool
    output: str
    error: Optional[str] = None
    duration_ms: float = 0.0
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingState:
    """Неизменяемое состояние обучения модели.

    Attributes:
        model_class: Класс модели для обучения.
        model_instance: Экземпляр модели (если создана).
        dataset_x: Входные данные датасета (ndarray или Tensor).
        dataset_y: Целевые данные датасета (ndarray или Tensor).
        backend: Выбранный вычислительный backend (PyFloat, NumPy, PyTorch).
    """

    model_class: Optional[type] = None
    model_instance: Optional[Any] = None
    dataset_x: Optional[Any] = None
    dataset_y: Optional[Any] = None
    backend: str = "PyFloat"


@dataclass(frozen=True)
class DatasetState:
    """Неизменяемое состояние датасета.

    Attributes:
        name: Имя датасета.
        x: Входные данные.
        y: Целевые данные.
        title: Название для отображения.
    """

    name: str
    x: Any
    y: Any
    title: str = ""


class Application(QObject):
    """Центральное приложение, управляющее состоянием IDE.

    Служит связующим звеном между UI (presentation layer) и бизнес-логикой (domain layer).
    Следует принципам Signal-Driven Architecture.
    """

    # Сигналы для оповещения об изменениях состояния
    execution_started = pyqtSignal()  # Выполнение кода начато
    execution_finished = pyqtSignal(ExecutionResult)  # Выполнение кода завершено
    output_received = pyqtSignal(str)  # Получен новый вывод
    model_loaded = pyqtSignal(object)  # Модель загружена и готова
    error_occurred = pyqtSignal(str)  # Произошла ошибка
    dataset_loaded = pyqtSignal(DatasetState)  # Датасет загружен
    training_state_changed = pyqtSignal(TrainingState)  # Состояние обучения изменилось

    def __init__(self) -> None:
        super().__init__()
        self._model: Optional[object] = None
        self._execution_namespace: dict[str, Any] = {}
        self._output_buffer: list[str] = []
        self._training_state = TrainingState()
        self._dataset_state: Optional[DatasetState] = None
        self._selected_backend: str = "PyFloat"

    def set_model(self, model: object) -> None:
        """Установить текущую модель и извлечь из неё информацию.

        Args:
            model: Объект модели из namespace выполнения
        """
        self._model = model
        self.model_loaded.emit(model)

    def append_output(self, text: str) -> None:
        """Добавить текст в буфер вывода.

        Args:
            text: Текст для добавления
        """
        self._output_buffer.append(text)
        self.output_received.emit(text)

    def clear_output_buffer(self) -> None:
        """Очистить буфер вывода."""
        self._output_buffer.clear()

    def get_current_model(self) -> Optional[object]:
        """Получить текущую загруженную модель."""
        return self._model

    def get_execution_namespace(self) -> dict[str, Any]:
        """Получить namespace последнего выполнения."""
        return self._execution_namespace.copy()

    def set_execution_namespace(self, namespace: dict[str, Any]) -> None:
        """Установить namespace после выполнения кода."""
        self._execution_namespace = namespace.copy()

    def set_dataset(self, name: str, x: Any, y: Any, title: str = "") -> None:
        """Установить текущий датасет.

        Args:
            name: Имя датасета.
            x: Входные данные.
            y: Целевые данные.
            title: Название для отображения.
        """
        self._dataset_state = DatasetState(name=name, x=x, y=y, title=title)
        self.dataset_loaded.emit(self._dataset_state)

    def get_dataset_state(self) -> Optional[DatasetState]:
        """Получить текущее состояние датасета."""
        return self._dataset_state

    def set_backend(self, backend: str) -> None:
        """Установить вычислительный backend.

        Args:
            backend: Название backend (PyFloat, NumPy, PyTorch).
        """
        self._selected_backend = backend

    def get_backend(self) -> str:
        """Получить выбранный backend."""
        return self._selected_backend

    def set_training_state(self, state: TrainingState) -> None:
        """Установить состояние обучения.

        Args:
            state: TrainingState с информацией об обучении.
        """
        self._training_state = state
        self.training_state_changed.emit(state)

    def get_training_state(self) -> TrainingState:
        """Получить текущее состояние обучения."""
        return self._training_state

    # Placeholder методы для расширения функциональности
    def save_state(self) -> None:
        """Сохранить состояние приложения на диск."""
        # TODO: Реализовать сохранение состояния
        pass

    def load_state(self) -> None:
        """Загрузить состояние приложения с диска."""
        # TODO: Реализовать загрузку состояния
        pass

    def configure_backend(self, backend_name: str) -> None:
        """
        Настроить вычислительный backend.

        Args:
            backend_name: Название backend ('float', 'numpy', 'torch' и т.д.)
        """
        # TODO: Реализовать переключение backend
        pass

    def reset_state(self) -> None:
        """Сбросить состояние приложения в начальное."""
        self._model = None
        self._execution_namespace.clear()
        self._output_buffer.clear()
