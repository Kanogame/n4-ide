from dataclasses import dataclass, field
from typing import Any, Optional

from n4.core import CompGraph
from n4.nn import Model
from n4.numeric import NumericProtocol
from PyQt6.QtCore import QObject, pyqtSignal

from ide.application.dataset_manager import DatasetManager
from ide.application.file_manager import FileManager
from ide.application.model_manager import ModelManager
from ide.application.state_manager import ApplicationState, ApplicationStatus
from ide.application.training_manager import TrainingManager
from ide.domain.execution.controller import ExecutionController
from ide.domain.training.controller import TrainingController


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

    Сигналы:
    - status_changed: Изменение состояния приложения (ApplicationStatus).
    - output_received: Новый вывод программы (str).

    Attributes:
        execution_controller: Контроллер выполнения кода.
        training_controller: Контроллер обучения модели.
        model_manager: Менеджер состояния модели.
        dataset_manager: Менеджер состояния датасета.
        training_manager: Менеджер процесса обучения.
    """

    # Основные сигналы: состояние и вывод
    status_changed = pyqtSignal(ApplicationStatus)
    output_received = pyqtSignal(str)

    # Сигналы для обновления UI (передают объекты для визуализации)
    computational_graph_ready = pyqtSignal(object)
    model_ready = pyqtSignal(object)

    # Сигналы для файловых операций с моделью
    model_save_finished = pyqtSignal(object)  # FileSaveResult
    model_load_finished = pyqtSignal(object)  # FileLoadResult

    def __init__(self) -> None:
        """Инициализировать приложение с контроллерами и менеджерами."""
        super().__init__()

        # Состояние приложения - начиная с IDLE
        self._application_status = ApplicationStatus(state=ApplicationState.IDLE)

        # Инициализировать контроллеры
        self.execution_controller = ExecutionController(
            output_callback=self.append_output
        )
        self.training_controller = TrainingController()

        # Инициализировать менеджеры
        self.model_manager = ModelManager(self.execution_controller)
        self.dataset_manager = DatasetManager()
        self.training_manager = TrainingManager(self.training_controller)
        self.file_manager = FileManager()

        # Буфер вывода и namespace
        self._output_buffer: list[str] = []
        self._execution_namespace: dict[str, Any] = {}

        # Объекты для визуализации
        self._final_model: Optional[Model] = None
        self._computational_graph: Optional[CompGraph] = None

        # Подключить сигналы менеджеров
        self._connect_managers()

    def _connect_managers(self) -> None:
        """Подключить сигналы менеджеров к обработчикам состояния."""
        # Ошибки модели
        self.model_manager.model_validation_failed.connect(self._on_error_occurred)

        # Ошибки датасета
        self.dataset_manager.dataset_generation_error.connect(self._on_error_occurred)

        # События тренировки - переводы состояния
        self.training_manager.training_started.connect(self._on_training_started)
        self.training_manager.training_finished.connect(self._on_training_finished)
        self.training_manager.training_error.connect(self._on_training_error)

    def _on_training_started(self) -> None:
        """Обработчик начала обучения."""
        self._set_status(ApplicationState.TRAINING)

    def _on_training_finished(self, result: Any) -> None:
        """Обработчик успешного завершения обучения.

        Args:
            result: TrainingResult с результатами обучения.
        """
        # Сохранить объекты для визуализации
        if hasattr(result, "comp_graph") and result.comp_graph:
            self._computational_graph = result.comp_graph
            self.computational_graph_ready.emit(result.comp_graph)

        if hasattr(result, "final_model") and result.final_model:
            self._final_model = result.final_model
            self.model_ready.emit(result.final_model)

        # Установить состояние TRAINED
        self._set_status(ApplicationState.TRAINED)

    def _on_training_error(self, error_message: str) -> None:
        """Обработчик ошибки обучения.

        Args:
            error_message: Сообщение об ошибке.
        """
        self._set_status(ApplicationState.ERROR, error_message)

    def _on_error_occurred(self, error_message: str) -> None:
        """Обработчик ошибки валидации или генерации.

        Модельные и датасетные ошибки не критичны - логируются но не переводят
        приложение в ERROR состояние (приложение остаётся в IDLE).
        Ошибки при обучении критичны и вызывают переход в ERROR.

        Args:
            error_message: Сообщение об ошибке.
        """
        self.append_output(f"✗ {error_message}")

    def _set_status(self, new_state: ApplicationState, error_message: str = "") -> None:
        """Установить новое состояние приложения.

        Валидирует переход состояния перед установкой.

        Args:
            new_state: Новое состояние.
            error_message: Сообщение об ошибке (если применимо).
        """
        # Валидировать переход
        if not self._application_status.can_transition_to(new_state):
            self.append_output(
                f"⚠ Недопустимый переход состояния: "
                f"{self._application_status.state.name} -> {new_state.name}"
            )
            return

        # Создать новый статус
        self._application_status = ApplicationStatus(
            state=new_state,
            error_message=error_message
            if new_state == ApplicationState.ERROR
            else None,
        )

        # Испустить сигнал
        self.status_changed.emit(self._application_status)

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

    def get_status(self) -> ApplicationStatus:
        """Получить текущее состояние приложения.

        Returns:
            Текущий ApplicationStatus.
        """
        return self._application_status

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

    def get_backend_type(self) -> type[NumericProtocol]:
        """Получить класс текущего вычислительного backend.

        Returns:
            Класс backend (например PyFloat, NumpyFloat).
        """
        return self.model_manager.get_backend_type()

    def get_final_model(self) -> Optional[Model]:
        """Получить последнюю тренированную модель.

        Returns:
            Модель или None если обучение ещё не завершено.
        """
        return self._final_model

    def get_computational_graph(self) -> Optional[CompGraph]:
        """Получить последний граф вычисления.

        Returns:
            Граф вычисления или None.
        """
        return self._computational_graph

    def save_model_code(self, file_path: str, code: str) -> None:
        """Сохранить код модели в файл и эмиттить сигнал результата.

        Использует FileManager для записи кода в файл, затем эмиттит
        signal model_save_finished с результатом операции.

        Args:
            file_path: Абсолютный путь к файлу для сохранения.
            code: Текст кода модели для сохранения.
        """
        result = self.file_manager.save_model_code(file_path, code)
        self.model_save_finished.emit(result)

        if result.success:
            self.append_output(f"✓ Модель сохранена: {result.file_path}")
        else:
            self.append_output(f"✗ Ошибка сохранения модели: {result.error}")

    def load_model_code(self, file_path: str) -> None:
        """Загрузить код модели из файла и эмиттить сигнал результата.

        Использует FileManager для чтения содержимого файла, затем эмиттит
        signal model_load_finished с результатом операции.

        Args:
            file_path: Абсолютный путь к файлу для загрузки.
        """
        result = self.file_manager.load_model_code(file_path)
        self.model_load_finished.emit(result)

        if result.success:
            self.append_output(f"✓ Модель загружена: {file_path}")
        else:
            self.append_output(f"✗ Ошибка загрузки модели: {result.error}")
