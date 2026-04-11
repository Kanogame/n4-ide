from .base import Collector, CollectorMode, BatchCollectorRecord, EpochCollectorRecord
from .loss.loss import Loss
from .registry import CollectorRegistry, get_collector_registry
from .repository import CollectorRepository

from .metrics.accuracy import Accuracy
from .metrics.f1_score import F1Score

__all__ = [
    "Collector",
    "CollectorMode",
    "Accuracy",
    "F1Score",
    "Loss",
    "CollectorRegistry",
    "get_collector_registry",
    "CollectorRepository",
    "BatchCollectorRecord",
    "EpochCollectorRecord",
]

from typing import Dict, Set

# Маппинг типов задач на доступные сборщики
TASK_TO_COLLECTORS: Dict[str, Set[str]] = {
    "Классификация": {"loss", "accuracy", "f1_score"},
    "Регрессия": {"loss"},
}

# Метаданные сборщиков: описание, единицы измерения и т.д.
COLLECTOR_METADATA: Dict[str, Dict[str, str]] = {
    "loss": {
        "description": "Функция потерь (оптимизируется модель)",
        "unit": "значение",
    },
    "accuracy": {
        "description": "Доля правильных предсказаний",
        "unit": "доля [0-1]",
    },
    "f1_score": {
        "description": "Гармоническое среднее precision и recall",
        "unit": "доля [0-1]",
    },
}


def get_collectors_for_task(task_type: str) -> Set[str]:
    """Получить доступные сборщики для типа задачи.

    Args:
        task_type: Тип задачи (из PUBLIC_LOSS_MAPPING).

    Returns:
        Множество доступных сборщиков для этого типа задачи.
    """
    return TASK_TO_COLLECTORS.get(task_type, {"loss"})


def get_collector_description(collector_name: str) -> str:
    """Получить описание сборщика.

    Args:
        collector_name: Имя сборщика.

    Returns:
        Описание сборщика.
    """
    metadata = COLLECTOR_METADATA.get(collector_name, {})
    return metadata.get("description", "Неизвестный сборщик")


def is_collector_applicable(collector_name: str, task_type: str) -> bool:
    """Проверить применим ли сборщик для типа задачи.

    Args:
        collector_name: Имя сборщика.
        task_type: Тип задачи.

    Returns:
        True если сборщик применим, False иначе.
    """
    available_collectors = get_collectors_for_task(task_type)
    return collector_name in available_collectors


# Инициализировать и зарегистрировать сборщики при импорте
def _initialize_collectors() -> None:
    """Зарегистрировать все встроенные сборщики в реестре."""
    registry = get_collector_registry()

    # Зарегистрировать Loss
    registry.register("loss", Loss)

    # Зарегистрировать Accuracy
    registry.register("accuracy", Accuracy)

    # Зарегистрировать F1Score
    registry.register("f1_score", F1Score)


# Выполнить инициализацию при импорте модуля
_initialize_collectors()
