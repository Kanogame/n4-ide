from ide.domain.collectors.base import AccumulativeCollector


class Accuracy(AccumulativeCollector):
    """Сборщик метрики точности (Accuracy).

    Режим: ACCUMULATIVE - накапливает корректные предсказания.
    Требует обновления после каждого батча и сброса после каждой эпохи.

    Вычисляет: количество корректных предсказаний / общее количество примеров.

    Обрабатывает предсказания разных форматов:
    - Скаляры: сравниваются напрямую
    - Вероятности/логиты (списки): берется индекс максимума
    - Тензоры: конвертируются в списки, затем обрабатываются
    """

    def __init__(self) -> None:
        """Инициализировать сборщик Accuracy."""
        super().__init__()
        self._correct_count: int = 0
        self._total_count: int = 0

    def get_name(self) -> str:
        """Получить уникальное имя сборщика.

        Returns:
            Имя сборщика: "accuracy".
        """
        return "accuracy"

    def update(self, predictions, targets) -> None:
        """Обновить состояние с новыми предсказаниями.

        Обрабатывает:
        - Одномерные тензоры/списки класса индексов
        - Двумерные тензоры/матрицы вероятностей (batch_size x num_classes)

        Args:
            predictions: Предсказания модели (n4.Tensor, list, или ndarray).
            targets: Целевые значения (n4.Tensor, list, или ndarray).
        """
        try:
            # Конвертировать в списки для сравнения
            pred_list = self._tensor_to_list(predictions)
            target_list = self._tensor_to_list(targets)

            if not pred_list or not target_list:
                return

            # Если размеры не совпадают, выйти
            if len(pred_list) != len(target_list):
                return

            # Подсчитать совпадения
            for pred, target in zip(pred_list, target_list):
                # Конвертировать оба значения в индексы класса
                pred_class = self._to_class_index(pred)
                target_class = self._to_class_index(target)

                if pred_class == target_class:
                    self._correct_count += 1

                # Всегда увеличиваем счетчик, даже если не совпадают
                self._total_count += 1

            # Обновить счётчик образцов
            self._sample_count = len(pred_list)

        except (ValueError, TypeError, AttributeError) as e:
            # В случае ошибки пропустить батч
            import logging

            logging.warning(
                f"Accuracy.update failed: {e}, pred type: {type(predictions)}, target type: {type(targets)}"
            )

    def compute(self) -> float:
        """Вычислить текущую точность.

        Returns:
            Доля корректных предсказаний в диапазоне [0, 1].
        """
        if self._total_count == 0:
            return 0.0
        accuracy = self._correct_count / self._total_count
        return max(0.0, min(1.0, accuracy))  # Ограничить [0, 1]

    def reset(self) -> None:
        """Сбросить состояние сборщика для новой эпохи."""
        self._correct_count = 0
        self._total_count = 0
        self._sample_count = 0
