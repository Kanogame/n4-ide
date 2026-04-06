"""Контроллер для управления датасетами.

Содержит бизнес-логику для генерации датасетов и интеграции
с UI компонентами.
"""

from typing import Any
from PyQt6.QtCore import QThread, pyqtSignal
from dataclasses import dataclass

from ide.domain.datasets import get_dataset_by_name, DatasetResult


@dataclass(frozen=True)
class DatasetGenerationResult:
    """Неизменяемый результат генерации датасета.

    Attributes:
        success: Успешно ли выполнена генерация.
        dataset_result: Результат датасета (если успешно).
        error: Сообщение об ошибке (если неуспешно).
    """

    success: bool
    dataset_result: DatasetResult | None = None
    error: str | None = None


class DatasetGenerationWorker(QThread):
    """Рабочий поток для генерации датасета.

    Запускает генерацию датасета в отдельном потоке,
    чтобы не блокировать основной UI поток.

    Signals:
        finished: Сигнал при завершении генерации.
        error: Сигнал при ошибке.
    """

    # Сигнал при успешном завершении генерации
    finished = pyqtSignal(DatasetResult)

    # Сигнал при ошибке
    error = pyqtSignal(str)

    def __init__(
        self,
        dataset_name: str,
        parameters: dict[str, Any],
    ) -> None:
        """Инициализировать рабочий поток.

        Args:
            dataset_name: Имя датасета для генерации.
            parameters: Словарь параметров конфигурации.
        """
        super().__init__()
        self.dataset_name = dataset_name
        self.parameters = parameters

    def run(self) -> None:
        """Выполнить генерацию датасета в отдельном потоке."""
        try:
            dataset = get_dataset_by_name(self.dataset_name)
            result = dataset.generate(self.parameters)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(f"Ошибка при генерации датасета: {str(e)}")
