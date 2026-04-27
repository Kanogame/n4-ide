from typing import Callable

from n4.nn import Model
from n4.numeric import NumericProtocol
from PyQt6.QtCore import QObject, pyqtSignal

from ide.domain.training.controller import TrainingController
from ide.domain.training.models import TrainingResult
from ide.presentation.components.trainer_panel.training_control import TrainingConfig


class TrainingManager(QObject):
    """Управляет процессом обучения модели.

    Отвечает за валидацию предусловий, запуск обучения,
    обработку результатов и ошибок.
    """

    # Сигналы об изменениях состояния обучения
    training_started = pyqtSignal()
    training_finished = pyqtSignal(object)
    training_error = pyqtSignal(str)
    training_stopped = pyqtSignal()

    def __init__(self, training_controller: TrainingController) -> None:
        """Инициализировать менеджер обучения.

        Args:
            training_controller: Контроллер обучения модели.
        """
        super().__init__()
        self._training_controller = training_controller
        self._is_training = False

    def start_training(
        self,
        model_class: type[Model],
        dataset_x,
        dataset_y,
        config: TrainingConfig,
        backend_type: type[NumericProtocol],
        on_progress: Callable[[str], None],
        on_finished: Callable[[TrainingResult], None],
        on_error: Callable[[str], None],
    ) -> bool:
        """Запустить обучение модели.

        Проверяет наличие необходимых компонентов (модель, датасет),
        затем запускает процесс обучения в отдельном потоке.

        Args:
            model_class: Класс модели для обучения.
            dataset_x: Входные данные датасета.
            dataset_y: Целевые данные датасета.
            config: Конфигурация параметров обучения.
            backend_type: Класс вычислительного backend.
            on_progress: Callback для обновления логов прогресса.
            on_finished: Callback для обработки успешного завершения.
            on_error: Callback для обработки ошибок.

        Returns:
            True если обучение запущено, False если есть ошибки валидации.
        """
        if model_class is None:
            on_error("Ошибка: сначала нужно загрузить модель (раздел 'Модель')")
            return False

        if dataset_x is None or dataset_y is None:
            on_error("Ошибка: сначала нужно сгенерировать датасет (раздел 'Датасет')")
            return False

        self._log_training_start(config, model_class, on_progress)

        def wrapped_on_finished(result):
            on_finished(result)
            self.training_finished.emit(result)

        self._training_controller.start_training(
            model_class=model_class,
            dataset_x=dataset_x,
            dataset_y=dataset_y,
            config=config,
            backend_type=backend_type,
            on_progress=on_progress,
            on_finished=wrapped_on_finished,
            on_error=on_error,
        )

        self._is_training = True
        self.training_started.emit()
        return True

    def stop_training(self) -> None:
        """Остановить текущее обучение."""
        if self._is_training:
            self._training_controller.stop_current()
            self._is_training = False
            self.training_stopped.emit()

    def is_training(self) -> bool:
        """Проверить статус обучения.

        Returns:
            True если обучение активно, False иначе.
        """
        return self._is_training

    def mark_training_finished(self) -> None:
        """Отметить обучение как завершенное."""
        self._is_training = False

    def _log_training_start(
        self,
        config: TrainingConfig,
        model_class: type,
        on_progress: Callable[[str], None],
    ) -> None:
        """Залогировать начало обучения с параметрами.

        Args:
            config: Конфигурация обучения.
            model_class: Класс модели.
            on_progress: Callback для вывода логов.
        """
        on_progress("Обучение начато...")
        on_progress("=" * 50)
        on_progress(f"Модель: {model_class.__name__}")
        on_progress("Параметры обучения:")
        on_progress(f"  Эпохи: {config.epochs}")
        on_progress(f"  Батч: {config.batch_size}")
        on_progress(f"  Скорость обучения: {config.learning_rate}")
        on_progress("=" * 50)
