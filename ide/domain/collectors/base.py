from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class CollectorMode(Enum):
    """Режим работы сборщика

    Определяет, требует ли сборщик накопления данных или вычисляется мгновенно.

    Attributes:
        ACCUMULATIVE: Метрика требует накопления данных (Accuracy, F1).
        DIRECT: Потери вычисляеются мгновенно (Loss).
    """

    ACCUMULATIVE = auto()
    DIRECT = auto()


@dataclass(frozen=True)
class CollectedValue:
    """Неизменяемое значение сборщика

    Attributes:
        value: Численное значение сборщика
        mode: Режим работы сборщика
        sample_count: Количество образцов, учтённых в вычисление
    """

    value: float
    mode: CollectorMode
    sample_count: int


@dataclass(frozen=True)
class BatchCollectorRecord:
    """Неизменяемая запись сборщика для одного батча.

    Attributes:
        batch_index: Индекс батча в пределах эпохи (0-based).
        epoch_index: Индекс эпохи (0-based).
        collectors: Словарь с значениями метрик {имя_метрики: значение}.
        sample_count: Количество образцов в батче.
    """

    batch_index: int
    epoch_index: int
    collectors: dict[str, float] = field(default_factory=dict)
    sample_count: int = 0

    def get_metric(self, name: str) -> Optional[float]:
        """Получить значение конкретной метрики для батча.

        Args:
            name: Имя метрики.

        Returns:
            Значение метрики или None если метрика отсутствует.
        """
        return self.collectors.get(name)


@dataclass(frozen=True)
class EpochCollectorRecord:
    """Неизменяемая запись агрегированных сборщиков за целую эпоху.

    Attributes:
        epoch_index: Индекс эпохи (0-based).
        metrics: Словарь агрегированных метрик {имя_метрики: значение}.
        batch_count: Количество батчей в эпохе.
        total_samples: Общее количество образцов в эпохе.
        duration_seconds: Время выполнения эпохи в секундах.
    """

    epoch_index: int
    collectors: dict[str, float] = field(default_factory=dict)
    batch_count: int = 0
    total_samples: int = 0
    duration_seconds: float = 0.0

    def get_metric(self, name: str) -> Optional[float]:
        """Получить значение конкретной метрики для эпохи.

        Args:
            name: Имя метрики.

        Returns:
            Значение метрики или None если метрика отсутствует.
        """
        return self.collectors.get(name)


class Collector(ABC):
    """Абстрактный базовый класс для всех сборщиков

    Определяет интерфейс для реализации метрик, потерь и прочего, поддерживающего:
    - Обновление состояния по мере поступления новых данных
    - Вычисление текущего значения
    - Сброс состояния для новой эпохи
    - Получение метаданных
    """

    def __init__(self, mode: CollectorMode = CollectorMode.ACCUMULATIVE) -> None:
        """Инициализировать сборщик.

        Args:
            mode: Режим работы метрики (накопительный или прямой)
        """
        self.mode = mode
        self._sample_count = 0

    @abstractmethod
    def compute(self) -> float:
        """Вычислить текущее значение метрики.

        Returns:
            Скалярное значение сборщика
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Сбросить состояние сборщика"""
        pass

    def get_value(self) -> CollectedValue:
        """Получить полную информацию о текущем значении метрики

        Returns:
            MetricValue с именем, значением, режимом и счётчиком образцов.
        """
        return CollectedValue(
            value=self.compute(),
            mode=self.mode,
            sample_count=self._sample_count,
        )

    def set_sample_count(self, count: int) -> None:
        """Установить количество образцов

        Используется для отслеживания объёма обработанных данных.

        Args:
            count: Количество образцов в текущем батче
        """
        self._sample_count = count

    @property
    def sample_count(self) -> int:
        """Получить количество образцов, учтённых в вычисление

        Returns:
            Количество образцов в последнем батче
        """
        return self._sample_count
