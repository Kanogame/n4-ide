from typing import Any, Optional, Self
from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, pyqtSignal

from n4.nn import Model
from n4.core import CompGraph

from ide.domain.datasets import DatasetResult

from ide.domain.execution.controller import ExecutionController
from ide.domain.training.controller import TrainingController

from ide.application.dataset_manager import DatasetManager
from ide.application.model_manager import ModelManager
from ide.application.training_manager import TrainingManager
from ide.application.state_manager import ApplicationStatus, ApplicationState


@dataclass(frozen=True)
class ExecutionResult:
    """Неизменяемый результат выполнения кода.

    Attributes:
        success: Флаг успеха выполнения.
        output: Текст вывода программы.
        error: Текст ошибки (если есть).
        duration_ms: Длительность выполнения в миллисекундах.
        variables: Словарь переменных из namespace.
    """

    success: bool
    output: str
    error: Optional[str] = None
    duration_ms: float = 0.0
    variables: dict[str, Any] = field(default_factory=dict)


class Application(QObject):
    """Центральное приложение, управляющее состоянием IDE.

    Служит связующим звеном между UI (presentation layer) и бизнес-логикой
    (domain layer). Следует принципам Signal-Driven Architecture.

    Attributes:
        execution_controller: Контроллер выполнения кода.
        training_controller: Контроллер обучения модели.
        model_manager: Менеджер состояния модели.
        dataset_manager: Менеджер состояния датасета.
        training_manager: Менеджер процесса обучения.
    """

    # Сигналы для оповещения об изменениях состояния
    output_received = pyqtSignal(str)
    dataset_loaded = pyqtSignal(DatasetResult)
    backend_changed = pyqtSignal(str)
    computational_graph_ready = pyqtSignal(object)
    model_ready = pyqtSignal(object)
    status_changed = pyqtSignal(ApplicationStatus)

    def __init__(self) -> None:
        """Инициализировать приложение с контроллерами и менеджерами."""
        super().__init__()

        # Состояние приложения
        self._application_status = ApplicationStatus()

        # Инициализировать контроллеры
        self.execution_controller = ExecutionController(
            output_callback=self.append_output
        )
        self.training_controller = TrainingController()

        # Инициализировать менеджеры
        self.model_manager = ModelManager(self.execution_controller)
        self.dataset_manager = DatasetManager()
        self.training_manager = TrainingManager(self.training_controller)

        # Буфер вывода и namespace
        self._output_buffer: list[str] = []
        self._execution_namespace: dict[str, Any] = {}

        # Подключить сигналы менеджеров к сигналам приложения
        self._connect_managers()

    def _connect_managers(self) -> None:
        """Подключить сигналы менеджеров к сигналам приложения."""
        # Cигналы модели
        self.model_manager.model_validation_failed.connect(
            self._on_model_validation_failed
        )
        self.model_manager.backend_changed.connect(self.backend_changed.emit)

        # Cигналы датасета
        self.dataset_manager.dataset_loaded.connect(self.dataset_loaded.emit)
        self.dataset_manager.dataset_generation_error.connect(
            self._on_dataset_generation_error
        )

        # Сигнал тренера
        self.training_manager.training_started.connect(
            lambda: self.set_application_status(ApplicationState.TRAINING)
        )

        self.training_manager.training_finished.connect(
            lambda: self.set_application_status(ApplicationState.COMPLETED)
        )

        self.training_manager.training_error.connect(
            lambda: self.set_application_status(ApplicationState.ERORRED)
        )

    def set_application_status(
        self: Self, new_state: ApplicationState, error: str = ""
    ):
        self._application_state = ApplicationStatus(
            state=new_state, last_error_message=error
        )
        self.status_changed.emit(self._application_state)

    def append_output(self, text: str) -> None:
        """Добавить текст в буфер вывода.

        Args:
            text: Текст для добавления.
        """
        self._output_buffer.append(text)
        self.output_received.emit(text)

    def clear_output_buffer(self) -> None:
        """Очистить буфер вывода."""
        self._output_buffer.clear()

    def get_execution_namespace(self) -> dict[str, Any]:
        """Получить namespace последнего выполнения.

        Returns:
            Копия namespace последнего выполнения кода.
        """
        return self._execution_namespace.copy()

    def set_execution_namespace(self, namespace: dict[str, Any]) -> None:
        """Установить namespace после выполнения кода.

        Args:
            namespace: Новый namespace для сохранения.
        """
        self._execution_namespace = namespace.copy()

    def set_final_model(self: Self, model: Model) -> None:
        """Установить модель после тренировки.

        Args:
            model: модель после тренировки
        """
        self._final_model = model
        self.model_ready.emit(self._final_model)

    def set_comp_graph(self: Self, comp_graph: CompGraph) -> None:
        """Установить модель после тренировки.

        Args:
            model: модель после тренировки
        """
        self._computational_graph = comp_graph
        self.computational_graph_ready.emit(self._computational_graph)

    def _on_model_validation_failed(self, error_message: str) -> None:
        self._append_error(f"Ошибка генерации датасета: {error_message}")

    def _on_dataset_generation_error(self, error_message: str) -> None:
        self._append_error(f"Ошибка генерации датасета: {error_message}")

    def _append_error(self: Self, error_message: str) -> None:
        self.append_output(error_message)
        self.set_application_status(ApplicationState.ERORRED, error_message)
