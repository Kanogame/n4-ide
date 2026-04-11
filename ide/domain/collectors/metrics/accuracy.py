from n4.tensor import Tensor
from ide.domain.collectors.base import Collector, CollectorMode


class Accuracy(Collector):
    """Метрика точности (Accuracy).

    Режим: ACCUMULATIVE - накапливает корректные предсказания.
    Требует обновления после каждого батча и сброса после каждой эпохи.

    Вычисляет: количество корректных предсказаний / общее количество примеров.
    """

    def __init__(self) -> None:
        """Инициализировать метрику Accuracy."""
        super().__init__(mode=CollectorMode.ACCUMULATIVE)
        self._correct_count: int = 0
        self._total_count: int = 0

    def update(self, predictions: Tensor, targets: Tensor) -> None:
        """Обновить состояние с новыми предсказаниями

        Args:
            predictions: Предсказания модели (n4.Tensor)
            targets: Целевые значения (n4.Tensor)
        """

        try:
            # Конвертировать в списки для сравнения
            pred_list = predictions.to_list()
            target_list = targets.to_list()

            if len(pred_list) != len(target_list):
                return

            # Подсчитать совпадения
            for pred, target in zip(pred_list, target_list):
                # Для многоклассовой классификации сравнивать индексы класса
                if isinstance(pred, (list, tuple)):
                    pred_class = pred.index(max(pred)) if pred else 0
                else:
                    pred_class = int(pred)

                target_class = int(target)

                if pred_class == target_class:
                    self._correct_count += 1

                self._total_count += 1

            # Обновить счётчик образцов
            self._sample_count = len(pred_list)

        except (ValueError, TypeError, AttributeError):
            # В случае ошибки пропустить батч
            pass

    def compute(self) -> float:
        """Вычислить текущую точность.

        Returns:
            Доля корректных предсказаний в диапазоне [0, 1].
        """
        if self._total_count == 0:
            return 0.0
        return self._correct_count / self._total_count

    def reset(self) -> None:
        """Сбросить состояние для новой эпохи."""
        self._correct_count = 0
        self._total_count = 0
        self._sample_count = 0
