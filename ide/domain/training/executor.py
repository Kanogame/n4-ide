import logging
import time
from typing import Any

from ide.domain.training.models import TrainingExecutorConfig, TrainingResult
from ide.domain.collectors import (
    get_collector_registry,
    CollectorRegistry,
    CollectorRepository,
)


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
        self._is_paused = False
        self._collector_repository: CollectorRepository = CollectorRepository()

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

        try:
            self.logger.info("Инициализация модели и компонентов обучения...")

            # Импортировать необходимые компоненты n4
            from n4.numeric import PyFloat
            from n4.tensor import Tensor

            # Создать экземпляр модели
            model = model_class()
            self.logger.info(f"Модель создана: {model_class.__name__}")

            # Выбрать loss функцию
            loss_fn = config.loss
            self.logger.info(f"Loss функция: {loss_fn.__class__.__name__}")

            # Создать оптимизатор
            optimizer = config.optimizer(model.parameters(), lr=config.learning_rate)
            self.logger.info(
                f"Оптимизатор: {optimizer.__class__.__name__}, lr={config.learning_rate}"
            )

            # Инициализировать метрики
            metrics = self._initialize_metrics(config.metrics)
            self.logger.info(
                f"Активные метрики: {', '.join(m.get_name() for m in metrics)}"
            )

            # Конвертировать данные в Tensor если нужно
            if not isinstance(dataset_x, Tensor):
                dataset_x = Tensor(
                    [
                        __import__("n4.core", fromlist=["Value"]).Value.from_float(
                            float(v), PyFloat
                        )
                        for v in dataset_x.flat
                    ],
                    shape=dataset_x.shape,
                )
            if not isinstance(dataset_y, Tensor):
                dataset_y = Tensor(
                    [
                        __import__("n4.core", fromlist=["Value"]).Value.from_float(
                            float(v), PyFloat
                        )
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

                # Сбросить метрики для новой эпохи
                for metric in metrics:
                    metric.reset()

                # Обнулить градиенты модели
                model.zero_grad()

                # Батчирование и обучение
                batch_count = self._execute_epoch(
                    model,
                    dataset_x,
                    dataset_y,
                    loss_fn,
                    optimizer,
                    metrics,
                    config.batch_size,
                    epoch,
                    batch_metrics_history,
                )

                # Собрать метрики эпохи
                epoch_metrics = self._collect_epoch_metrics(metrics)
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
                    f"{m.get_name()}: {m.compute():.6f}" for m in metrics
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
            self._is_paused = False

    def _initialize_metrics(self, metrics_config: dict[str, bool]) -> list[Any]:
        """Инициализировать метрики на основе конфигурации.

        Args:
            metrics_config: Словарь активных метрик {имя: включена ли}.

        Returns:
            Список инициализированных метрик.
        """
        registry = get_collector_registry()
        metrics = []

        for metric_name, is_enabled in metrics_config.items():
            if is_enabled:
                try:
                    metric = registry.create(metric_name)
                    metrics.append(metric)
                except KeyError:
                    self.logger.warning(f"Метрика '{metric_name}' не найдена")

        return metrics

    def _execute_epoch(
        self,
        model: Any,
        dataset_x: Any,
        dataset_y: Any,
        loss_fn: Any,
        optimizer: Any,
        metrics: list[Any],
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
            metrics: Список активных метрик.
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

            # Backward pass
            loss_value.backward()

            # Обновить параметры
            optimizer.step()

            # Обновить метрики
            for metric in metrics:
                if metric.get_name() == "loss":
                    metric.update(loss_value, batch_y)
                else:
                    metric.update(predictions, batch_y)
                metric.set_sample_count(batch_sample_count)

            # Собрать метрики батча
            batch_metrics = {m.get_name(): m.compute() for m in metrics}
            batch_metrics_history[global_batch_index] = batch_metrics

            # Записать в хранилище
            self._collector_repository.record_batch(batch_metrics, batch_sample_count)

            global_batch_index += 1

        return batch_count

    def _collect_epoch_metrics(self, metrics: list[Any]) -> dict[str, float]:
        """Собрать финальные метрики для эпохи.

        Args:
            metrics: Список активных метрик.

        Returns:
            Словарь с финальными значениями метрик.
        """
        return {m.get_name(): m.compute() for m in metrics}

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

        Args:
            dataset: n4.Tensor или другой тип данных.
            start_idx: Начальный индекс батча.
            end_idx: Конечный индекс батча.

        Returns:
            Батч данных.
        """
        if hasattr(dataset, "__getitem__"):
            return dataset[start_idx:end_idx]
        return dataset

    def pause_training(self) -> None:
        """Поставить обучение на паузу."""
        self._is_paused = True
        self.logger.info("Обучение поставлено на паузу")

    def resume_training(self) -> None:
        """Продолжить обучение."""
        self._is_paused = False
        self.logger.info("Обучение возобновлено")

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

    def is_paused(self) -> bool:
        """Проверить поставлено ли обучение на паузу.

        Returns:
            True если обучение на паузе, False иначе.
        """
        return self._is_paused
