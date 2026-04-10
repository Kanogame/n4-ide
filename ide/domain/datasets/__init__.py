from ide.domain.datasets.base import Dataset, DatasetField, DatasetResult, FieldType
from ide.domain.datasets.xor import XORDataset

# Реестр всех доступных датасетов
DATASET_REGISTRY: dict[str, type[Dataset]] = {
    "xor": XORDataset,
}


def get_dataset_by_name(name: str) -> Dataset:
    """Получить экземпляр датасета по его имени.

    Args:
        name: Имя датасета из реестра (e.g., "xor").

    Returns:
        Экземпляр датасета.

    Raises:
        ValueError: Если датасет с заданным именем не найден.
    """
    if name not in DATASET_REGISTRY:
        available = ", ".join(DATASET_REGISTRY.keys())
        raise ValueError(f"Датасет '{name}' не найден. Доступные датасеты: {available}")

    dataset_class = DATASET_REGISTRY[name]
    return dataset_class()


__all__ = [
    "Dataset",
    "DatasetField",
    "DatasetResult",
    "FieldType",
    "XORDataset",
    "DATASET_REGISTRY",
    "get_dataset_by_name",
]
