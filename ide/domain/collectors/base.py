from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Any


class CollectorMode(Enum):
    """Режим работы сборщика.

    Определяет, требует ли сборщик накопления данных или вычисляется мгновенно.

    Attributes:
        ACCUMULATIVE: Сборщик требует накопления данных (Accuracy, F1).
        DIRECT: Сборщик вычисляется мгновенно (Loss).
    """

    ACCUMULATIVE = auto()
    DIRECT = auto()


@dataclass(frozen=True)
class CollectedValue:
    """Неизменяемое значение сборщика.

    Attributes:
        value: Численное значение сборщика.
        mode: Режим работы сборщика.
        sample_count: Количество образцов, учтённых в вычисление.
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
        collectors: Словарь со значениями сборщиков {имя_сборщика: значение}.
        sample_count: Количество образцов в батче.
    """

    batch_index: int
    epoch_index: int
    collectors: dict[str, float] = field(default_factory=dict)
    sample_count: int = 0

    def get_collector(self, name: str) -> Optional[float]:
        """Получить значение конкретного сборщика для батча.

        Args:
            name: Имя сборщика.

        Returns:
            Значение сборщика или None если сборщик отсутствует.
        """
        return self.collectors.get(name)


@dataclass(frozen=True)
class EpochCollectorRecord:
    """Неизменяемая запись агрегированных сборщиков за целую эпоху.

    Attributes:
        epoch_index: Индекс эпохи (0-based).
        collectors: Словарь со значениями сборщиков {имя_сборщика: значение}.
        batch_count: Количество батчей в эпохе.
        total_samples: Общее количество образцов в эпохе.
        duration_seconds: Время выполнения эпохи в секундах.
    """

    epoch_index: int
    collectors: dict[str, float] = field(default_factory=dict)
    batch_count: int = 0
    total_samples: int = 0
    duration_seconds: float = 0.0

    def get_collector(self, name: str) -> Optional[float]:
        """Получить значение конкретного сборщика для эпохи.

        Args:
            name: Имя сборщика.

        Returns:
            Значение сборщика или None если сборщик отсутствует.
        """
        return self.collectors.get(name)


class Collector(ABC):
    """Абстрактный базовый класс для всех сборщиков.

    Определяет интерфейс для реализации метрик, потерь и прочего, поддерживающего:
    - Обновление состояния по мере поступления новых данных.
    - Вычисление текущего значения.
    - Сброс состояния для новой эпохи.
    - Получение метаданных.
    """

    def __init__(self, mode: CollectorMode = CollectorMode.ACCUMULATIVE) -> None:
        """Инициализировать сборщик.

        Args:
            mode: Режим работы сборщика (накопительный или прямой).
        """
        self.mode = mode
        self._sample_count = 0

    @abstractmethod
    def get_name(self) -> str:
        """Получить уникальное имя сборщика.

        Returns:
            Строковое имя сборщика (например, 'accuracy', 'loss', 'f1_score').
        """
        pass

    @abstractmethod
    def compute(self) -> float:
        """Вычислить текущее значение сборщика.

        Returns:
            Скалярное значение сборщика.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Сбросить состояние сборщика для новой эпохи."""
        pass

    def get_value(self) -> CollectedValue:
        """Получить полную информацию о текущем значении сборщика.

        Returns:
            CollectedValue с названием, значением, режимом и счётчиком образцов.
        """
        return CollectedValue(
            value=self.compute(),
            mode=self.mode,
            sample_count=self._sample_count,
        )

    def set_sample_count(self, count: int) -> None:
        """Установить количество образцов.

        Используется для отслеживания объёма обработанных данных.

        Args:
            count: Количество образцов в текущем батче.
        """
        self._sample_count = count

    @property
    def sample_count(self) -> int:
        """Получить количество образцов, учтённых в вычисление.

        Returns:
            Количество образцов в последнем батче.
        """
        return self._sample_count


class DirectCollector(Collector):
    """Базовый класс для сборщиков с режимом DIRECT (например, Loss).

    Режим DIRECT означает, что значение вычисляется напрямую из выходных
    данных (например, loss_fn возвращает значение loss напрямую).
    """

    def __init__(self) -> None:
        """Инициализировать DIRECT сборщик."""
        super().__init__(mode=CollectorMode.DIRECT)
        self._current_value: float = 0.0

    def update(self, value: Any) -> None:
        """Обновить значение сборщика.

        Args:
            value: Скалярное значение (float или преобразуемое в float).
        """
        try:
            # Попробовать различные способы извлечения числового значения
            if isinstance(value, float):
                self._current_value = value
            elif isinstance(value, int):
                self._current_value = float(value)
            # Для n4.Value объектов - у них есть метод __float__
            elif hasattr(value, "__float__"):
                self._current_value = float(value)
            # Для n4.Value объектов через get_float
            elif hasattr(value, "get_float"):
                extracted = value.get_float()
                self._current_value = (
                    float(extracted) if not isinstance(extracted, float) else extracted
                )
            # Для других объектов со значением
            elif hasattr(value, "to_float"):
                extracted = value.to_float()
                self._current_value = (
                    float(extracted) if not isinstance(extracted, float) else extracted
                )
            elif hasattr(value, "value"):
                self._current_value = float(value.value)
            else:
                # Последняя попытка - прямое преобразование
                self._current_value = float(value)
        except (TypeError, ValueError, AttributeError) as e:
            # Логирование ошибки для отладки
            import logging

            logger = logging.getLogger("trainer")
            logger.warning(
                f"DirectCollector.update failed to extract value from {type(value)}: {e}"
            )
            self._current_value = 0.0

    def compute(self) -> float:
        """Вычислить текущее значение.

        Returns:
            Текущее значение, установленное при update().
        """
        return self._current_value

    def reset(self) -> None:
        """Сбросить состояние сборщика."""
        self._current_value = 0.0


class AccumulativeCollector(Collector):
    """Базовый класс для сборщиков с режимом ACCUMULATIVE (например, Accuracy, F1).

    Режим ACCUMULATIVE означает, что значение накапливается из батча в батч
    и вычисляется как агрегированное значение (например, правильные предсказания / всего).
    """

    def __init__(self) -> None:
        """Инициализировать ACCUMULATIVE сборщик."""
        super().__init__(mode=CollectorMode.ACCUMULATIVE)

    @abstractmethod
    def update(self, predictions: Any, targets: Any) -> None:
        """Обновить состояние сборщика с предсказаниями и целевыми значениями.

        Args:
            predictions: Предсказания модели (n4.Tensor, list или ndarray).
            targets: Целевые значения (n4.Tensor, list или ndarray).
        """
        pass

    @staticmethod
    def _tensor_to_list(tensor: Any) -> list[Any]:
        """Конвертировать тензор в список.

        Args:
            tensor: n4.Tensor, список, ndarray или другой тип.

        Returns:
            Список значений.
        """
        if hasattr(tensor, "to_list"):
            return tensor.to_list()
        elif hasattr(tensor, "tolist"):
            return tensor.tolist()
        elif isinstance(tensor, (list, tuple)):
            return list(tensor)
        else:
            return [tensor]

    @staticmethod
    def _to_class_index(value: Any) -> int:
        """Конвертировать значение в индекс класса.

        Для вероятностей/логитов - возвращает индекс максимального значения.
        Для индексов - возвращает целое число.

        Args:
            value: Значение (число, список, или n4.Value).

        Returns:
            Индекс класса.
        """
        try:
            # Если это число
            if isinstance(value, (int, float)):
                return int(value)

            # Если это n4.Value или объект с методом get_float
            if hasattr(value, "get_float"):
                return int(value.get_float())
            if hasattr(value, "to_float"):
                return int(value.to_float())
            if hasattr(value, "__float__"):
                return int(float(value))
            if hasattr(value, "value"):
                return int(value.value)

            # Если это список/кортеж вероятностей (один для каждого класса)
            if isinstance(value, (list, tuple)):
                if len(value) == 0:
                    return 0

                # Конвертировать все значения в float
                float_values = []
                for v in value:
                    try:
                        if isinstance(v, float):
                            float_values.append(v)
                        elif isinstance(v, int):
                            float_values.append(float(v))
                        elif hasattr(v, "get_float"):
                            float_values.append(float(v.get_float()))
                        elif hasattr(v, "to_float"):
                            float_values.append(float(v.to_float()))
                        elif hasattr(v, "__float__"):
                            float_values.append(float(v))
                        elif hasattr(v, "value"):
                            float_values.append(float(v.value))
                        else:
                            float_values.append(float(v))
                    except (TypeError, ValueError):
                        float_values.append(0.0)

                # Найти индекс максимального значения
                if not float_values:
                    return 0
                max_idx = 0
                max_val = float_values[0]
                for i, v in enumerate(float_values[1:], 1):
                    if v > max_val:
                        max_val = v
                        max_idx = i
                return max_idx

            return int(value)

        except (TypeError, ValueError, AttributeError):
            return 0
