from n4.loss import Loss, MSELoss, CrossEntropyLoss

# Реестр всех доступных функций потерь
LOSS_REGISTRY: dict[str, type[Loss]] = {
    "MSE": MSELoss,
    "CrossEntropy": CrossEntropyLoss,
}

# Маппинг потерь для UI
PUBLIC_LOSS_MAPPING: dict[str, str] = {
    "Классификация": "CrossEntropy",
    "Регрессия": "MSE",
}


def get_loss_by_public_mapping(mapping: str) -> Loss:
    """Получить экземпляр функции потерь по его UI имени.

    Args:
        name: Имя функции потерь из реестра (e.g., "Регрессия").

    Returns:
        Экземпляр функции потерь.

    Raises:
        ValueError: Если функция потерь с заданным именем не найден.
    """
    if mapping not in PUBLIC_LOSS_MAPPING:
        available = ", ".join(PUBLIC_LOSS_MAPPING.keys())
        raise ValueError(
            f"Датасет '{mapping}' не найден. Доступные функции потень: {available}"
        )

    real_mapping_name = PUBLIC_LOSS_MAPPING[mapping]
    loss_class = LOSS_REGISTRY[real_mapping_name]
    return loss_class()
