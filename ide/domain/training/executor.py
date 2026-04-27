import logging
import time
from typing import Any, Optional

from n4.core import Value as _Value
from n4.tensor import Tensor

from ide.domain.collectors import (
    CollectorRepository,
    get_collector_registry,
)
from ide.domain.collectors.base import DirectCollector
from ide.domain.training.models import TrainingExecutorConfig, TrainingResult


class TrainingExecutor:
    """Выполнитель процесса обучения с использованием n4 framework.

    Управляет процессом обучения модели, включая:
    - Инициализацию модели, оптимизатора и метрик
    - Батчирование входных данных
    - Вычисление и накопление метрик
    - Логирование хода выполнения
    - Контроль выполнения (остановка, пауза, возобновление)
    """

    def __init__(self) -> None:
        """Инициализировать исполнитель обучения."""
        self.logger = self._setup_logger()
        self._is_running = False
        self._collector_repository: CollectorRepository = CollectorRepository()
        self._last_loss_value: Optional[Any] = None
        self._computational_graph: Optional[Any] = None

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Создать логгер для тренировки.

        Настраивает логгер с обработчиком для вывода информации о процессе обучения.

        Returns:
            Логгер для записи информации о процессе обучения.
        """
        logger = logging.getLogger("trainer")
        logger.setLevel(logging.INFO)

        # Удалить существующие обработчики
        logger.handlers.clear()

        # Создать обработчик для консоли
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)

        # Создать форматер
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger

    def execute_training(
        self,
        model_class: type,
        dataset_x: Any,
        dataset_y: Any,
        config: TrainingExecutorConfig,
    ) -> TrainingResult:
        """Выполнить обучение модели с использованием n4 framework.

        Создаёт экземпляр модели, настраивает оптимизатор и метрики,
        затем выполняет цикл обучения на указанное количество эпох,
        с батчированием данных и сбором метрик.

        Args:
            model_class: Класс модели для обучения (подкласс n4.nn.Model).
            dataset_x: Входные данные датасета (n4.tensor.Tensor или numpy array).
            dataset_y: Целевые данные датасета (n4.tensor.Tensor или numpy array).
            config: Конфигурация параметров обучения.

        Returns:
            TrainingResult с результатами обучения и историей метрик.
        """
        self._is_running = True
        start_time = time.time()
        self._collector_repository.clear()

        # Создать экземпляр модели
        model = model_class()
        self.logger.info(f"Модель создана: {model_class.__name__}")

        try:
            self.logger.info("Инициализация модели и компонентов обучения...")

            # Выбрать loss функцию
            loss_fn = config.loss
            self.logger.info(f"Loss функция: {loss_fn.__class__.__name__}")

            # Создать оптимизатор
            optimizer = config.optimizer(model.parameters(), lr=config.learning_rate)  # type: ignore
            self.logger.info(
                f"Оптимизатор: {optimizer.__class__.__name__}, lr={config.learning_rate}"
            )

            # Инициализировать сборщики
            collectors = self._initialize_metrics(config.metrics)
            self.logger.info(
                f"Активные сборщики: {', '.join(c.get_name() for c in collectors)}"
            )

            # Конвертировать данные в Tensor если нужно
            if not isinstance(dataset_x, Tensor):
                dataset_x = Tensor(
                    [
                        _Value.from_float(float(v), config.backend_type)
                        for v in dataset_x.flat
                    ],
                    shape=dataset_x.shape,
                )
            if not isinstance(dataset_y, Tensor):
                dataset_y = Tensor(
                    [
                        _Value.from_float(float(v), config.backend_type)
                        for v in dataset_y.flat
                    ],
                    shape=dataset_y.shape,
                )

            self.logger.info(
                f"Датасет загружен: X shape {dataset_x.shape}, y shape {dataset_y.shape}"
            )
            self.logger.info(
                f"Параметры: эпохи={config.epochs}, батч={config.batch_size}"
            )

            # Основной цикл обучения
            epochs_completed = 0
            total_samples_processed = 0
            epoch_metrics_history: dict[int, dict[str, float]] = {}
            batch_metrics_history: dict[int, dict[str, float]] = {}

            for epoch in range(config.epochs):
                if not self._is_running:
                    self.logger.info("Обучение остановлено пользователем")
                    break

                epoch_start_time = time.time()
                self._collector_repository.start_epoch(epoch)

                # Сбросить сборщики для новой эпохи
                for collector in collectors:
                    collector.reset()

                # Обнулить градиенты модели
                model.zero_grad()

                # Батчирование и обучение
                batch_count = self._execute_epoch(
                    model,
                    dataset_x,
                    dataset_y,
                    loss_fn,
                    optimizer,
                    collectors,
                    config.batch_size,
                    epoch,
                    batch_metrics_history,
                )

                # Собрать метрики эпохи
                epoch_metrics = self._collect_epoch_metrics(collectors)
                epoch_duration = time.time() - epoch_start_time
                epoch_metrics_history[epoch] = epoch_metrics

                # Записать метрики в хранилище
                self._collector_repository.finish_epoch(epoch_metrics, epoch_duration)

                # Подсчитать обработанные образцы
                batch_samples = [
                    r.sample_count
                    for r in self._collector_repository.get_batch_records_for_epoch(
                        epoch
                    )
                ]
                epoch_samples = (
                    sum(batch_samples)
                    if batch_samples
                    else dataset_x.shape[0]
                    if hasattr(dataset_x, "shape")
                    else 0
                )
                total_samples_processed += epoch_samples

                # Логировать прогресс
                metrics_str = ", ".join(
                    f"{c.get_name()}: {c.compute():.6f}" for c in collectors
                )
                self.logger.info(
                    f"Эпоха {epoch + 1}/{config.epochs} "
                    f"({batch_count} батчей, {epoch_samples} образцов, "
                    f"{epoch_duration:.2f}s) | {metrics_str}"
                )

                epochs_completed = epoch + 1

            duration = time.time() - start_time
            final_metrics = epoch_metrics_history.get(epochs_completed - 1, {})

            self.logger.info(
                f"Обучение завершено! "
                f"Эпох: {epochs_completed}, "
                f"Время: {duration:.2f} сек"
            )

            return TrainingResult(
                success=True,
                final_metrics=final_metrics,
                epoch_metrics_history=epoch_metrics_history,
                batch_metrics_history=batch_metrics_history,
                duration_seconds=duration,
                epochs_completed=epochs_completed,
                total_samples_processed=total_samples_processed,
                final_model=model,
                comp_graph=self._computational_graph,
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Ошибка обучения: {str(e)}"
            self.logger.error(error_msg)
            self.logger.exception("Traceback:")

            return TrainingResult(
                success=False,
                error_message=error_msg,
                duration_seconds=duration,
            )

        finally:
            self._is_running = False

    def _initialize_metrics(self, collectors_config: dict[str, bool]) -> list[Any]:
        """Инициализировать сборщики на основе конфигурации.

        Args:
            collectors_config: Словарь активных сборщиков {имя: включен ли}.

        Returns:
            Список инициализированных сборщиков.
        """
        registry = get_collector_registry()
        collectors = []

        for collector_name, is_enabled in collectors_config.items():
            if is_enabled:
                try:
                    collector = registry.create(collector_name)
                    collectors.append(collector)
                except KeyError:
                    self.logger.warning(f"Сборщик '{collector_name}' не найден")

        return collectors

    def _execute_epoch(
        self,
        model: Any,
        dataset_x: Any,
        dataset_y: Any,
        loss_fn: Any,
        optimizer: Any,
        collectors: list[Any],
        batch_size: int,
        epoch_index: int,
        batch_metrics_history: dict[int, dict[str, float]],
    ) -> int:
        """Выполнить одну эпоху обучения с батчированием.

        Args:
            model: Модель для обучения.
            dataset_x: Входные данные.
            dataset_y: Целевые значения.
            loss_fn: Функция потерь.
            optimizer: Оптимизатор.
            collectors: Список активных сборщиков.
            batch_size: Размер батча.
            epoch_index: Индекс текущей эпохи.
            batch_metrics_history: Словарь для сбора метрик батчей.

        Returns:
            Количество обработанных батчей.
        """
        dataset_size = self._get_dataset_size(dataset_x)
        batch_count = (dataset_size + batch_size - 1) // batch_size
        global_batch_index = 0

        for batch_idx in range(batch_count):
            if not self._is_running:
                break

            # Извлечь батч
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, dataset_size)
            batch_x = self._get_batch(dataset_x, start_idx, end_idx)
            batch_y = self._get_batch(dataset_y, start_idx, end_idx)
            batch_sample_count = end_idx - start_idx

            # Обнулить градиенты для батча
            model.zero_grad()

            # Forward pass
            predictions = model.forward_pass(batch_x)

            # Вычислить loss
            loss_value = loss_fn(predictions, batch_y)

            # Сохранить последнее значение loss и собрать граф сразу
            self._last_loss_value = loss_value

            # Попытаться собрать граф пока value ещё действителен
            if self._computational_graph is None:
                try:
                    self._computational_graph = loss_value.collect_graph()
                except Exception:
                    # Граф может быть недоступен, это нормально
                    pass

            # Backward pass
            loss_value.backward()

            # Обновить параметры
            optimizer.step()

            # Обновить сборщики
            for collector in collectors:
                if isinstance(collector, DirectCollector):
                    collector.update(loss_value)
                else:
                    collector.update(predictions, batch_y)
                collector.set_sample_count(batch_sample_count)

            # Собрать метрики батча
            batch_metrics = {c.get_name(): c.compute() for c in collectors}
            batch_metrics_history[global_batch_index] = batch_metrics

            # Записать в хранилище
            self._collector_repository.record_batch(batch_metrics, batch_sample_count)

            global_batch_index += 1

        return batch_count

    def _collect_epoch_metrics(self, collectors: list[Any]) -> dict[str, float]:
        """Собрать финальные значения сборщиков для эпохи.

        Args:
            collectors: Список активных сборщиков.

        Returns:
            Словарь со значениями сборщиков.
        """
        return {c.get_name(): c.compute() for c in collectors}

    @staticmethod
    def _get_dataset_size(dataset: Any) -> int:
        """Получить размер датасета.

        Args:
            dataset: n4.Tensor или другой тип данных.

        Returns:
            Количество образцов в датасете.
        """
        if hasattr(dataset, "shape"):
            return dataset.shape[0]
        if hasattr(dataset, "__len__"):
            return len(dataset)
        return 1

    @staticmethod
    def _get_batch(dataset: Any, start_idx: int, end_idx: int) -> Any:
        """Извлечь батч из датасета.

        Для n4.Tensor извлекает отдельные строки с помощью индексации [i].
        Для других типов пытается использовать slice notation [start:end].

        Args:
            dataset: n4.Tensor или другой тип данных.
            start_idx: Начальный индекс батча.
            end_idx: Конечный индекс батча.

        Returns:
            Батч данных того же типа.
        """
        try:
            from n4.tensor import Tensor

            if isinstance(dataset, Tensor):
                # Для n4.Tensor собираем батч из отдельных строк
                batch_rows = []
                for i in range(start_idx, min(end_idx, dataset.shape[0])):
                    batch_rows.append(dataset[i])

                if not batch_rows:
                    return dataset

                # Объединяем все значения из батча
                batch_values = []
                for row in batch_rows:
                    # Получаем значения из каждой строки
                    if hasattr(row, "_values"):
                        batch_values.extend(row._values)
                    elif hasattr(row, "to_list"):
                        row_list = row.to_list()
                        if isinstance(row_list, list):
                            batch_values.extend(row_list)
                        else:
                            batch_values.append(row_list)
                    else:
                        # Если это Value
                        batch_values.append(row)

                # Формируем новую форму батча: (batch_size,) + row_shape
                batch_size = len(batch_rows)
                first_row_shape = (
                    batch_rows[0].shape if hasattr(batch_rows[0], "shape") else ()
                )
                if isinstance(first_row_shape, tuple):
                    new_shape = (batch_size,) + first_row_shape
                else:
                    new_shape = (batch_size, first_row_shape)

                # Создаем батч-тензор
                return Tensor(batch_values, shape=new_shape)
        except (ImportError, AttributeError, TypeError):
            # Если что-то не сработает с Tensor, используем fallback
            pass

        # Fallback для других типов - используем slice notation
        if hasattr(dataset, "__getitem__"):
            try:
                return dataset[start_idx:end_idx]
            except (TypeError, KeyError):
                pass

        return dataset

    def stop_training(self) -> None:
        """Остановить обучение."""
        self._is_running = False
        self.logger.info("Остановка обучения...")

    def is_running(self) -> bool:
        """Проверить работает ли обучение.

        Returns:
            True если обучение в процессе, False иначе.
        """
        return self._is_running

    def get_collector_repository(self) -> CollectorRepository:
        """Получить хранилище сборщиков метрик.

        Returns:
            CollectorRepository с данными о собранных метриках.
        """
        return self._collector_repository
