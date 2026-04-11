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
    "register_metric",
    "CollectorRepository",
    "BatchCollectorRecord",
    "EpochCollectorRecord",
]

from typing import Dict, Set

# Маппинг типов задач на доступные метрики
TASK_TO_METRICS: Dict[str, Set[str]] = {
    "Классификация": {"loss", "accuracy", "f1_score"},
    "Регрессия": {"loss"},
}

# Метаданные метрик: описание, единицы измерения и т.д.
METRIC_METADATA: Dict[str, Dict[str, str]] = {
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


def get_metrics_for_task(task_type: str) -> Set[str]:
    """Получить доступные метрики для типа задачи.

    Args:
        task_type: Тип задачи (из PUBLIC_LOSS_MAPPING).

    Returns:
        Множество доступных метрик для этого типа задачи.
    """
    return TASK_TO_METRICS.get(task_type, {"loss"})


def get_metric_description(metric_name: str) -> str:
    """Получить описание метрики.

    Args:
        metric_name: Имя метрики.

    Returns:
        Описание метрики.
    """
    metadata = METRIC_METADATA.get(metric_name, {})
    return metadata.get("description", "Неизвестная метрика")


def is_metric_applicable(metric_name: str, task_type: str) -> bool:
    """Проверить применима ли метрика для типа задачи.

    Args:
        metric_name: Имя метрики.
        task_type: Тип задачи.

    Returns:
        True если метрика применима, False иначе.
    """
    available_metrics = get_metrics_for_task(task_type)
    return metric_name in available_metrics
