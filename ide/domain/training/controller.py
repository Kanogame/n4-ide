from typing import Self, Any, Optional, Callable

from PyQt6.QtCore import QThread, pyqtSignal, QObject

from ide.domain.training.executor import (
    TrainingExecutor,
)
from ide.domain.training.models import (
    TrainingConfig,
    TrainingResult,
    TrainingExecutorConfig,
)


from ide.presentation.components.trainer_panel.training_log_reader import (
    QtLogHandler,
)


class TrainingWorkerThread(QThread):
    """Рабочий поток для выполнения обучения модели в фоне.

    Позволяет запустить процесс обучения без блокирования основного потока
    и передавать результаты через Qt сигналы.

    Signals:
        progress: Сигнал с текущим логом обучения (str).
        finished: Сигнал с результатом обучения (TrainingResult).
        error: Сигнал с сообщением об ошибке (str).
    """

    # Сигнал при получении нового лога.
    progress = pyqtSignal(str)

    # Сигнал при завершении обучения.
    finished = pyqtSignal(TrainingResult)

    # Сигнал при ошибке.
    error = pyqtSignal(str)

    def __init__(
        self: Self,
        model_class: type,
        dataset_x: Any,
        dataset_y: Any,
        config: TrainingConfig,
        parent: Optional[QObject] = None,
    ) -> None:
        """Инициализировать рабочий поток обучения.

        Args:
            model_class: Класс модели для обучения (подкласс n4.nn.Model).
            dataset_x: Входные данные датасета.
            dataset_y: Целевые данные датасета.
            config: Конфигурация обучения.
            parent: Родительский объект Qt.
        """
        super().__init__(parent)

        self.model_class = model_class
        self.dataset_x = dataset_x
        self.dataset_y = dataset_y
        self.config = TrainingExecutorConfig(config)

        self.executor = TrainingExecutor()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Настроить логирование для передачи логов через сигналы."""
        # Получить логгер тренировки
        logger = self.executor.logger

        # Создать Qt обработчик логирования
        qt_handler = QtLogHandler()
        qt_handler.log_emitted.connect(self.progress.emit)

        # Добавить обработчик
        logger.addHandler(qt_handler)

    def run(self) -> None:
        """Выполнить обучение в рабочем потоке."""
        try:
            result = self.executor.execute_training(
                self.model_class,
                self.dataset_x,
                self.dataset_y,
                self.config,
            )
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(f"Неожиданная ошибка: {str(e)}")

    def pause(self) -> None:
        """Поставить обучение на паузу."""
        self.executor.pause_training()

    def resume(self) -> None:
        """Продолжить обучение."""
        self.executor.resume_training()

    def stop(self) -> None:
        """Остановить обучение."""
        self.executor.stop_training()


class TrainingController:
    """Контроллер для управления процессом обучения.

    Управляет созданием рабочих потоков обучения, координирует
    логирование и результаты обучения.
    """

    def __init__(self) -> None:
        """Инициализировать контроллер обучения."""
        self.current_training_thread: Optional[TrainingWorkerThread] = None

    def start_training(
        self,
        model_class: type,
        dataset_x: Any,
        dataset_y: Any,
        config: TrainingConfig,
        on_progress: Callable[[str], None],
        on_finished: Callable[[TrainingResult], None],
        on_error: Callable[[str], None],
    ) -> None:
        """Запустить процесс обучения в отдельном потоке.

        Args:
            model_class: Класс модели для обучения (подкласс n4.nn.Model).
            dataset_x: Входные данные датасета.
            dataset_y: Целевые данные датасета.
            config: Конфигурация обучения.
            on_progress: Callback при получении нового лога.
            on_finished: Callback при завершении обучения.
            on_error: Callback при ошибке.
        """
        # Остановить предыдущее обучение если оно работает
        if self.current_training_thread is not None:
            if self.current_training_thread.isRunning():
                self.current_training_thread.stop()
                self.current_training_thread.wait()

        # Создать новый рабочий поток
        self.current_training_thread = TrainingWorkerThread(
            model_class,
            dataset_x,
            dataset_y,
            config,
        )

        # Подключить сигналы
        self.current_training_thread.progress.connect(on_progress)
        self.current_training_thread.finished.connect(on_finished)
        self.current_training_thread.error.connect(on_error)

        # Запустить поток
        self.current_training_thread.start()

    def pause_current(self) -> None:
        """Поставить текущее обучение на паузу."""
        if self.current_training_thread is not None:
            self.current_training_thread.pause()

    def resume_current(self) -> None:
        """Продолжить текущее обучение."""
        if self.current_training_thread is not None:
            self.current_training_thread.resume()

    def stop_current(self) -> None:
        """Остановить текущее обучение."""
        if self.current_training_thread is not None:
            self.current_training_thread.stop()

    def is_training(self) -> bool:
        """Проверить идёт ли в данный момент обучение.

        Returns:
            True если обучение в процессе, False иначе.
        """
        if self.current_training_thread is None:
            return False

        return self.current_training_thread.isRunning()
