from n4.numeric import NumericProtocol
from n4.core import Value
from typing import Self
from ide.domain.collectors.base import Collector, CollectorMode


class Loss(Collector):
    """Сборщик функции потерь (Loss).

    Режим: DIRECT - значение вычисляется непосредственно из значения loss.
    Не требует накопления данных между батчами.
    """

    def __init__(self) -> None:
        """Инициализировать метрику Loss."""
        super().__init__(mode=CollectorMode.DIRECT)
        self._last_loss: float = 0.0

    def update(self: Self, *args: Value | NumericProtocol | float) -> None:
        """Обновить значение loss

        Args:
            loss_value: Значение функции потерь (n4.Value или float)
        """

        loss_value = args[0]

        if isinstance(loss_value, Value) or isinstance(loss_value, NumericProtocol):
            self._last_loss = loss_value.get_float()
        else:
            self._last_loss = loss_value

    def compute(self) -> float:
        """Вычислить текущее значение loss.

        Returns:
            Значение функции потерь.
        """
        return self._last_loss

    def reset(self) -> None:
        """Сбросить состояние метрики.

        Для Loss это просто устанавливает последнее значение в 0.
        """
        self._last_loss = 0.0
