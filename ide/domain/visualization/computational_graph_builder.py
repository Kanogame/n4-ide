from typing import Self

from graphviz import Digraph
from n4.core import CompGraph

from ide.domain.visualization.base import GraphExporter


class ComputationalGraphBuilder(GraphExporter):
    """Построитель graphviz графа вычислительного графа операций.

    Преобразует компьютационный граф из n4 library в визуальное представление,
    где операции и значения отображаются как отдельные узлы.

    Примечание: Основная логика уже реализована в CompGraph.export_graphviz(),
    этот класс служит обёрткой для согласованности с архитектурой.
    """

    def __init__(self, comp_graph: CompGraph) -> None:
        """Инициализировать построитель.

        Args:
            comp_graph: CompGraph объект из n4 library (результат collect_graph).

        Raises:
            ValueError: Если граф пуст или недействителен.
        """
        if comp_graph is None:
            raise ValueError("Computational graph cannot be None")

        # Проверить что это действительно CompGraph или похожий объект
        if not hasattr(comp_graph, "export_graphviz"):
            raise ValueError(
                f"Graph must have export_graphviz method. "
                f"Got {type(comp_graph).__name__}"
            )

        self.comp_graph = comp_graph

    def export_graphviz(self: Self) -> Digraph:
        """Экспортировать вычислительный граф в graphviz.Digraph.

        Делегирует экспорт методу CompGraph, добавляя при необходимости
        дополнительные параметры визуализации.

        Returns:
            graphviz.Digraph объект с вычислительным графом.

        Raises:
            RuntimeError: Если export_graphviz вернул некорректный результат.
        """
        try:
            # Использовать встроенный метод экспорта CompGraph
            graph = self.comp_graph.export_graphviz()

            if graph is None:
                raise RuntimeError("export_graphviz returned None")

            return graph

        except AttributeError as e:
            raise RuntimeError(f"CompGraph missing export_graphviz method: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to export computational graph: {e}") from e
