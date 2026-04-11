from ide.domain.collectors.base import BatchCollectorRecord, EpochCollectorRecord
from typing import Optional, Any


class CollectorRepository:
    """Хранилище для накопления и анализа метрик обучения.

    Отслеживает метрики на уровне:
    - Батча: детальные метрики для каждого батча
    - Эпохи: агрегированные метрики для целой эпохи

    Позволяет анализировать ход обучения и выявлять проблемы.
    """

    def __init__(self) -> None:
        """Инициализировать хранилище метрик."""
        self._batch_records: list[BatchCollectorRecord] = []
        self._epoch_records: list[EpochCollectorRecord] = []
        self._current_epoch_index: int = 0
        self._current_batch_index: int = 0

    def start_epoch(self, epoch_index: int) -> None:
        """Начать новую эпоху в хранилище.

        Args:
            epoch_index: Индекс новой эпохи.
        """
        self._current_epoch_index = epoch_index
        self._current_batch_index = 0

    def record_batch(self, collectors: dict[str, float], sample_count: int) -> None:
        """Записать сборщики для батча.

        Args:
            сборщики: Словарь с метриками батча.
            sample_count: Количество образцов в батче.
        """
        record = BatchCollectorRecord(
            batch_index=self._current_batch_index,
            epoch_index=self._current_epoch_index,
            collectors=collectors.copy(),
            sample_count=sample_count,
        )
        self._batch_records.append(record)
        self._current_batch_index += 1

    def finish_epoch(
        self,
        collectors: dict[str, float],
        duration_seconds: float = 0.0,
    ) -> EpochCollectorRecord:
        """Завершить текущую эпоху и записать агрегированные сборщики.

        Args:
            collectors: Агрегированные метрики эпохи.
            duration_seconds: Время выполнения эпохи.

        Returns:
            EpochMetricsRecord с записанными метриками.
        """
        # Подсчитать количество батчей и образцов в текущей эпохе
        epoch_batches = [
            r for r in self._batch_records if r.epoch_index == self._current_epoch_index
        ]
        batch_count = len(epoch_batches)
        total_samples = sum(r.sample_count for r in epoch_batches)

        record = EpochCollectorRecord(
            epoch_index=self._current_epoch_index,
            collectors=collectors.copy(),
            batch_count=batch_count,
            total_samples=total_samples,
            duration_seconds=duration_seconds,
        )
        self._epoch_records.append(record)
        return record

    def get_batch_record(self, batch_index: int) -> Optional[BatchCollectorRecord]:
        """Получить запись метрик для конкретного батча.

        Args:
            batch_index: Глобальный индекс батча.

        Returns:
            BatchMetricsRecord или None если батч не найден.
        """
        for record in self._batch_records:
            if record.batch_index == batch_index:
                return record
        return None

    def get_epoch_record(self, epoch_index: int) -> Optional[EpochCollectorRecord]:
        """Получить запись метрик для конкретной эпохи.

        Args:
            epoch_index: Индекс эпохи.

        Returns:
            EpochMetricsRecord или None если эпоха не найдена.
        """
        for record in self._epoch_records:
            if record.epoch_index == epoch_index:
                return record
        return None

    def get_batch_records_for_epoch(
        self, epoch_index: int
    ) -> list[BatchCollectorRecord]:
        """Получить все записи батчей для конкретной эпохи.

        Args:
            epoch_index: Индекс эпохи.

        Returns:
            Список BatchMetricsRecord для эпохи.
        """
        return [r for r in self._batch_records if r.epoch_index == epoch_index]

    def get_all_batch_records(self) -> list[BatchCollectorRecord]:
        """Получить все записи батчей.

        Returns:
            Список всех BatchMetricsRecord в порядке добавления.
        """
        return self._batch_records.copy()

    def get_all_epoch_records(self) -> list[EpochCollectorRecord]:
        """Получить все записи эпох.

        Returns:
            Список всех EpochMetricsRecord в порядке добавления.
        """
        return self._epoch_records.copy()

    def get_metric_history(self, metric_name: str, level: str = "epoch") -> list[float]:
        """Получить историю значений метрики.

        Args:
            metric_name: Имя метрики.
            level: Уровень агрегации ("batch" или "epoch").

        Returns:
            Список значений метрики в порядке хронологии.
        """
        if level == "epoch":
            return [r.get_metric(metric_name) or 0.0 for r in self._epoch_records]
        elif level == "batch":
            return [r.get_metric(metric_name) or 0.0 for r in self._batch_records]
        else:
            raise ValueError(f"Неизвестный уровень: {level}")

    def get_epoch_summary(self) -> dict[str, Any]:
        """Получить сводку по всем эпохам.

        Returns:
            Словарь с статистикой по эпохам:
            - epoch_count: Количество завершённых эпох
            - total_samples: Общее количество образцов
            - metrics: Словарь со средними/финальными значениями метрик
        """
        if not self._epoch_records:
            return {
                "epoch_count": 0,
                "total_samples": 0,
                "metrics": {},
            }

        total_samples = sum(r.total_samples for r in self._epoch_records)

        # Собрать последние значения метрик
        latest_metrics: dict[str, float] = {}
        if self._epoch_records:
            latest_metrics = self._epoch_records[-1].collectors.copy()

        return {
            "epoch_count": len(self._epoch_records),
            "total_samples": total_samples,
            "metrics": latest_metrics,
        }

    def clear(self) -> None:
        """Очистить хранилище (удалить все записи).

        Используется в основном для переиспользования хранилища
        при запуске нового процесса обучения.
        """
        self._batch_records.clear()
        self._epoch_records.clear()
        self._current_epoch_index = 0
        self._current_batch_index = 0

    def __repr__(self) -> str:
        """Получить строковое представление хранилища.

        Returns:
            Строка с информацией о состоянии хранилища.
        """
        return (
            f"MetricsStorage("
            f"epochs={len(self._epoch_records)}, "
            f"batches={len(self._batch_records)}"
            f")"
        )
