from graphviz import Digraph

from typing import Self, Optional
from abc import abstractmethod, ABC


class GraphExporter(ABC):
    """Базовый класс для экспортеров графов.

    Определяет интерфейс для конвертации различных структур в graphviz.
    """

    @abstractmethod
    def export_graphviz(self: Self) -> Digraph:
        """Экспортировать граф в формате graphviz.Digraph.

        Returns:
            graphviz.Digraph объект с визуализацией.
        """
        pass


class LayerInfo:
    """Информация об одном слое сети"""

    def __init__(
        self,
        name: str,
        index: int,
        neuron_count: Optional[int] = None,
        parameter_count: int = 0,
    ) -> None:
        """Инициализировать информацию о слое.

        Args:
            name: Имя класса слоя.
            index: Порядковый номер слоя.
            neuron_count: Количество нейронов в слое.
            parameter_count: Количество параметров.
            input_shape: Форма входного тензора.
            output_shape: Форма выходного тензора.
            additional_info: Дополнительная информация о слое.
        """
        self.name = name
        self.index = index
        self.neuron_count = neuron_count
        self.parameter_count = parameter_count

    def get_label(self) -> str:
        """Получить отформатированный текст для визуализации в графе.

        Returns:
            Многострочный текст с информацией о слое.
        """
        lines = [self.name]

        if self.neuron_count is not None:
            lines.append(f"Neurons: {self.neuron_count}")

        if self.parameter_count > 0:
            lines.append(f"Params: {self.parameter_count:,}")

        return "\\n".join(lines)
