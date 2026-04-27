from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ide.domain.datasets import DatasetResult
from ide.domain.datasets.controller import DatasetGenerationWorker


class DatasetManager(QObject):
    """Управляет состоянием датасета в приложении.

    Отвечает за загрузку, валидацию и сохранение состояния датасета.
    Также управляет рабочим потоком генерации датасета.
    Emits сигналы об изменениях состояния для обновления UI.

    Attributes:
        dataset_loaded: Сигнал о загрузке датасета.
        dataset_generation_started: Сигнал о начале генерации.
        dataset_generation_finished: Сигнал о завершении генерации.
        dataset_generation_error: Сигнал об ошибке генерации.
    """

    # Сигналы об изменениях состояния
    dataset_loaded = pyqtSignal(object)
    dataset_generation_started = pyqtSignal()
    dataset_generation_finished = pyqtSignal(object)
    dataset_generation_error = pyqtSignal(str)

    def __init__(self) -> None:
        """Инициализировать менеджер датасета."""
        super().__init__()
        self._dataset_state: Optional[DatasetResult] = None
        self._generation_worker: Optional[DatasetGenerationWorker] = None

    def set_dataset(self, dataset: DatasetResult) -> None:
        """Установить текущий датасет.

        Args:
            dataset: Объект датасета.
        """
        self._dataset_state = dataset
        self.dataset_loaded.emit(self._dataset_state)

    def get_dataset_state(self) -> Optional[DatasetResult]:
        """Получить текущее состояние датасета.

        Returns:
            Текущее состояние датасета или None, если не загружен.
        """
        return self._dataset_state

    def has_dataset(self) -> bool:
        """Проверить наличие загруженного датасета.

        Returns:
            True если датасет загружен, False иначе.
        """
        return self._dataset_state is not None

    def clear_dataset(self) -> None:
        """Очистить текущий датасет."""
        self._dataset_state = None

    def start_generation_worker(
        self, dataset_name: str, parameters: dict
    ) -> DatasetGenerationWorker:
        """Запустить новый рабочий поток генерации датасета.

        Останавливает предыдущий рабочий поток если он активен,
        затем создает и запускает новый.

        Args:
            dataset_name: Имя датасета для генерации.
            parameters: Словарь параметров для датасета.

        Returns:
            Созданный и запущенный рабочий поток.
        """
        # Остановить предыдущий рабочий поток если он работает
        if self._generation_worker is not None and self._generation_worker.isRunning():
            self._generation_worker.quit()
            self._generation_worker.wait()

        # Создать новый рабочий поток
        self._generation_worker = DatasetGenerationWorker(dataset_name, parameters)

        # Emit сигнал о начале генерации
        self.dataset_generation_started.emit()

        # Запустить поток
        self._generation_worker.start()

        return self._generation_worker

    def on_dataset_generated(self, dataset_result: DatasetResult) -> None:
        """Обработать успешную генерацию датасета.

        Args:
            dataset_result: Объект результата датасета.
        """
        self.set_dataset(dataset_result)
        self.dataset_generation_finished.emit(dataset_result)

    def on_dataset_generation_error(self, error_message: str) -> None:
        """Обработать ошибку при генерации датасета.

        Args:
            error_message: Текст сообщения об ошибке.
        """
        self.dataset_generation_error.emit(error_message)
