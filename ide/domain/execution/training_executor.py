import logging
import time
from dataclasses import dataclass
from typing import Optional, Any
from ide.presentation.components.trainer_panel.training_control import TrainingConfig


@dataclass(frozen=True)
class TrainingResult:
    """Неизменяемый результат процесса обучения.

    Attributes:
        success: Успешно ли завершилось обучение.
        error_message: Сообщение об ошибке если обучение не удалось.
        final_metrics: Словарь финальных метрик.
        duration_seconds: Длительность обучения в секундах.
    """

    success: bool
    error_message: Optional[str] = None
    final_metrics: Optional[dict[str, Any]] = None
    duration_seconds: float = 0.0


class TrainingExecutor:
    """Выполнитель процесса обучения с использованием n4 framework.

    Управляет процессом обучения модели, логирует ход выполнения,
    и предоставляет контроль над процессом через сигналы.

    Использует стандартный Python логгер для вывода информации.
    """

    def __init__(self) -> None:
        """Инициализировать исполнитель обучения."""
        self.logger = self._setup_logger()
        self._is_running = False
        self._is_paused = False

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
        config: TrainingConfig,
    ) -> TrainingResult:
        """Выполнить обучение модели с использованием n4 framework.

        Создаёт экземпляр модели, настраивает оптимизатор и loss функцию,
        затем выполняет цикл обучения на указанное количество эпох.

        Args:
            model_class: Класс модели для обучения (подкласс n4.nn.Model).
            dataset_x: Входные данные датасета (n4.tensor.Tensor или numpy array).
            dataset_y: Целевые данные датасета (n4.tensor.Tensor или numpy array).
            config: Конфигурация параметров обучения.

        Returns:
            TrainingResult с результатами обучения.
        """
        self._is_running = True
        start_time = time.time()

        try:
            self.logger.info("Инициализация модели и компонентов обучения...")

            # Импортировать необходимые компоненты n4
            from n4.numeric import PyFloat
            from n4.tensor import Tensor
            from n4.nn.loss import MSELoss
            from n4.optim import SGD

            # Создать экземпляр модели
            model = model_class()
            self.logger.info(f"Модель создана: {model_class.__name__}")

            # Выбрать loss функцию в зависимости от задачи
            if config.task_type == "Регрессия":
                loss_fn = MSELoss()
                self.logger.info("Loss функция: MSELoss (регрессия)")
            else:
                # Для классификации используем MSELoss по умолчанию
                loss_fn = MSELoss()
                self.logger.info("Loss функция: MSELoss (классификация)")

            # Создать оптимизатор
            optimizer = SGD(model.parameters(), lr=config.learning_rate)
            self.logger.info(f"Оптимизатор: SGD, lr={config.learning_rate}")

            # Конвертировать данные в Tensor если нужно
            if not isinstance(dataset_x, Tensor):
                dataset_x = Tensor(
                    [
                        type(dataset_x.flat[0])(v, PyFloat)
                        if hasattr(type(dataset_x.flat[0]), "__call__")
                        else __import__("n4.core", fromlist=["Value"]).Value.from_float(
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
            final_metrics: dict[str, Any] = {}

            for epoch in range(config.epochs):
                if not self._is_running:
                    self.logger.info("Обучение остановлено пользователем")
                    break

                # Пауза если требуется
                while self._is_paused:
                    time.sleep(0.1)

                # Обнулить градиенты
                model.zero_grad()

                # Forward pass
                predictions = model.forward_pass(dataset_x)

                # Вычислить loss
                loss_value = loss_fn(predictions, dataset_y)

                # Backward pass
                loss_value.backward()

                # Обновить параметры
                optimizer.step()

                # Извлечь значение loss
                try:
                    loss_scalar = float(loss_value.data)
                except (AttributeError, TypeError):
                    # Если loss не имеет .data, попробовать прямое преобразование
                    loss_scalar = float(str(loss_value))

                final_metrics = {
                    "loss": loss_scalar,
                }

                # Логировать прогресс
                self.logger.info(
                    f"Эпоха {epoch + 1}/{config.epochs} | loss: {loss_scalar:.6f}"
                )

            duration = time.time() - start_time

            self.logger.info(f"Обучение завершено! Время: {duration:.2f} сек")

            return TrainingResult(
                success=True,
                final_metrics=final_metrics,
                duration_seconds=duration,
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
