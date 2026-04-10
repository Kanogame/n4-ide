from dataclasses import dataclass, field
from typing import Optional, Any, Self

from ide.domain.loss import get_loss_by_public_mapping
from ide.domain.optimizer import get_optimizer_by_name


@dataclass(frozen=True)
class TrainingConfig:
    """Неизменяемая конфигурация параметров обучения.

    Attributes:
        task_type: Тип задачи обучения (классификация, регрессия и т.д.).
        epochs: Количество эпох обучения.
        batch_size: Размер батча для обучения.
        learning_rate: Скорость обучения (learning rate).
        optimizer: Выбранный оптимизатор (SGD, Adam и т.д.).
        metrics: Словарь активных метрик.
    """

    task_type: str = "Классификация"
    epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: str = "Adam"
    metrics: dict[str, bool] = field(
        default_factory=lambda: {"loss": True, "accuracy": True}
    )


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


class TrainingExecutorConfig:
    def __init__(self: Self, config: TrainingConfig):
        self.loss = get_loss_by_public_mapping(config.task_type)
        self.optimizer = get_optimizer_by_name(config.optimizer)
        self.epochs = config.epochs
        self.batch_size = config.batch_size
        self.learning_rate = config.learning_rate
        self.metrics = config.metrics
