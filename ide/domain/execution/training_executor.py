import logging
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
    """Выполнитель процесса обучения с поддержкой логирования.

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
        model: Any,
        dataset: Any,
        config: TrainingConfig,
    ) -> TrainingResult:
        """Выполнить обучение модели.

        Args:
            model: Модель для обучения.
            dataset: Датасет для обучения.
            config: Конфигурация параметров обучения.

        Returns:
            TrainingResult с результатами обучения.
        """
        import time

        self._is_running = True
        start_time = time.time()

        try:
            self.logger.info("Начало обучения модели...")
            self.logger.info(f"Параметры: {config}")

            # Эмуляция процесса обучения
            final_metrics: dict[str, Any] = {}

            for epoch in range(config.epochs):
                if not self._is_running:
                    self.logger.info("Обучение остановлено пользователем")
                    break

                # Пауза если требуется
                while self._is_paused:
                    time.sleep(0.1)

                # Эмуляция обучения эпохи
                loss = 0.5 - (epoch * 0.005)  # Симуляция убывания loss
                accuracy = 0.5 + (epoch * 0.005)  # Симуляция роста accuracy

                self.logger.info(
                    f"Эпоха {epoch + 1}/{config.epochs} | "
                    f"loss: {loss:.6f} | accuracy: {accuracy:.5f}"
                )

                final_metrics = {
                    "loss": loss,
                    "accuracy": accuracy,
                }

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
