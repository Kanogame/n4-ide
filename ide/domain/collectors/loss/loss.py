from ide.domain.collectors.base import DirectCollector


class Loss(DirectCollector):
    """Сборщик функции потерь (Loss).

    Режим: DIRECT - значение вычисляется непосредственно из значения loss.
    Не требует накопления данных между батчами.
    """

    def get_name(self) -> str:
        """Получить уникальное имя сборщика.

        Returns:
            Имя сборщика: "loss".
        """
        return "loss"
