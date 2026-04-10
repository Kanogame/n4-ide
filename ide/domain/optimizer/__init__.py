from n4.optim import Optimizer, SGD, Adam

OPTIMIZER_REGISTRY: dict[str, type[Optimizer]] = {
    "SGD": SGD,
    "Adam": Adam,
}


def get_optimizer_by_name(name: str) -> type[Optimizer]:
    """Получить класс оптимизатора по его имени.

    Args:
        name: Имя оптимизатора из реестра

    Returns:
        Класс оптимизатора

    Raises:
        ValueError: Если оптимизатор с заданным именем не найден.
    """
    if name not in OPTIMIZER_REGISTRY:
        available = ", ".join(OPTIMIZER_REGISTRY.keys())
        raise ValueError(
            f"Оптимизато '{name}' не найден. Доступные функции потень: {available}"
        )

    return OPTIMIZER_REGISTRY[name]
