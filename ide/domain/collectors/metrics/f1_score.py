from ide.domain.collectors.base import AccumulativeCollector


class F1Score(AccumulativeCollector):
    """Сборщик метрики F1-мера (F1-Score).

    Режим: ACCUMULATIVE - накапливает true positives, false positives, false negatives.
    Подходит для бинарной классификации и дисбалансированных датасетов.

    Вычисляет: 2 * (precision * recall) / (precision + recall).
    """

    def __init__(self, positive_class: int = 1) -> None:
        """Инициализировать сборщик F1Score.

        Args:
            positive_class: Индекс класса, считающегося положительным (по умолчанию 1).
        """
        super().__init__()
        self.positive_class = positive_class
        self._true_positives: int = 0
        self._false_positives: int = 0
        self._false_negatives: int = 0

    def get_name(self) -> str:
        """Получить уникальное имя сборщика.

        Returns:
            Имя сборщика: "f1_score".
        """
        return "f1_score"

    def update(self, predictions, targets) -> None:
        """Обновить состояние с новыми предсказаниями.

        Args:
            predictions: Предсказания модели.
            targets: Целевые значения.
        """
        try:
            pred_list = self._tensor_to_list(predictions)
            target_list = self._tensor_to_list(targets)

            if len(pred_list) != len(target_list):
                return

            for pred, target in zip(pred_list, target_list):
                # Определить предсказанный класс и целевой класс
                pred_class = self._to_class_index(pred)
                target_class = self._to_class_index(target)

                # Подсчитать TP, FP, FN
                if (
                    pred_class == self.positive_class
                    and target_class == self.positive_class
                ):
                    self._true_positives += 1
                elif (
                    pred_class == self.positive_class
                    and target_class != self.positive_class
                ):
                    self._false_positives += 1
                elif (
                    pred_class != self.positive_class
                    and target_class == self.positive_class
                ):
                    self._false_negatives += 1

            self._sample_count = len(pred_list)

        except (ValueError, TypeError, AttributeError):
            pass

    def compute(self) -> float:
        """Вычислить текущую F1-меру.

        Returns:
            F1-мера в диапазоне [0, 1], или 0 если нет положительных примеров.
        """
        if self._true_positives == 0:
            return 0.0

        precision = (
            self._true_positives / (self._true_positives + self._false_positives)
            if (self._true_positives + self._false_positives) > 0
            else 0.0
        )

        recall = (
            self._true_positives / (self._true_positives + self._false_negatives)
            if (self._true_positives + self._false_negatives) > 0
            else 0.0
        )

        if precision + recall == 0:
            return 0.0

        return 2 * (precision * recall) / (precision + recall)

    def reset(self) -> None:
        """Сбросить состояние сборщика для новой эпохи."""
        self._true_positives = 0
        self._false_positives = 0
        self._false_negatives = 0
        self._sample_count = 0
