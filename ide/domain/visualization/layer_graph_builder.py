from typing import Self

from graphviz import Digraph
from n4.nn import Model, Sequential
from n4.nn.layer import Layer

from ide.domain.visualization.base import GraphExporter, LayerInfo


class LayersGraphBuilder(GraphExporter):
    """Построитель graphviz графа архитектуры слоёв Sequential модели.

    Преобразует Sequential модель в визуальное представление, где каждый слой
    отображается как отдельный узел с информацией о размере и параметрах.

    Example:
        >>> builder = LayersGraphBuilder(sequential_model)
        >>> graph = builder.export_graphviz()
        >>> graph.view()  # Открыть в viewer
    """

    def __init__(self: Self, model: Model) -> None:
        """Инициализировать построитель.

        Args:
            model: Sequential модель из n4 library.

        Raises:
            ValueError: Если модель не является Sequential или не имеет слоёв.
        """
        if not (hasattr(model, "layers") or hasattr(model, "model")):
            raise ValueError("Model must have 'layers' attribute (Sequential model)")

        self.model = model
        self.layers_info = self._extract_layer_info()

    def _extract_layer_info(self: Self) -> list[LayerInfo]:
        """Извлечь информацию из всех слоёв модели.

        Returns:
            Список LayerInfo объектов для каждого слоя.
        """
        layers_info: list[LayerInfo] = []

        layers: list[Layer] = []
        if hasattr(self.model, "layers") and isinstance(self.model, Sequential):
            layers = self.model.layers
        elif hasattr(self.model, "model") and isinstance(self.model.model, Sequential):
            layers = self.model.model.layers
        else:
            ValueError("Model must have 'layers' attribute (Sequential model)")

        for idx, layer in enumerate(layers):
            info = self._analyze_layer(layer, idx)
            layers_info.append(info)

        return layers_info

    def _analyze_layer(
        self: Self,
        layer: Layer,
        index: int,
    ) -> LayerInfo:
        """Анализировать один слой и извлечь его параметры.

        Args:
            layer: Слой для анализа.
            index: Порядковый номер слоя.

        Returns:
            LayerInfo с информацией о слое.
        """
        layer_name = layer.__class__.__name__

        # Извлечь количество нейронов/выходов
        neuron_count = layer.neuron_count()

        # Извлечь количество параметров
        parameter_count = len(layer.parameters())

        return LayerInfo(
            name=layer_name,
            index=index,
            neuron_count=neuron_count,
            parameter_count=parameter_count,
        )

    def export_graphviz(self: Self) -> Digraph:
        """Экспортировать архитектуру слоёв в graphviz.Digraph.

        Создаёт визуальное представление, где:
        - Каждый слой отображается как прямоугольный узел
        - Слои расположены вертикально в порядке выполнения
        - Информация о параметрах и размерах отображается внутри узла

        Returns:
            graphviz.Digraph объект с графом архитектуры.
        """

        graph = Digraph(comment="N4 Layers Architecture")
        graph.attr(rankdir="TB")
        graph.attr("node", shape="box", style="rounded,filled")
        graph.attr(splines="ortho")
        graph.attr(sep="+0.5")
        graph.attr(nodesep="0.5")

        # Добавить вход (placeholder для входных данных)
        graph.node("input", label="Input", fillcolor="lightgray", shape="ellipse")

        # Добавить каждый слой
        for layer_info in self.layers_info:
            node_id = f"layer_{layer_info.index}"
            label = layer_info.get_label()

            # Выбрать цвет в зависимости от типа слоя
            color = self._get_layer_color(layer_info.name)

            graph.node(node_id, label=label, fillcolor=color)

        # Добавить выход
        graph.node("output", label="Output", fillcolor="lightgray", shape="ellipse")

        # Соединить слои в цепь
        graph.edge("input", "layer_0")

        for i in range(len(self.layers_info) - 1):
            graph.edge(f"layer_{i}", f"layer_{i + 1}")

        graph.edge(f"layer_{len(self.layers_info) - 1}", "output")

        return graph

    @staticmethod
    def _get_layer_color(layer_name: str) -> str:
        """Получить цвет для визуализации слоя по его типу.

        Args:
            layer_name: Имя класса слоя.

        Returns:
            Имя цвета для graphviz.
        """
        # Цвета для разных типов слоёв
        color_map = {
            "DenseLayer": "#54F98B",  # Зелёный
            "ConvLayer": "#54E8F9",  # Голубой
            "SoftmaxLayer": "#54E8F9",  # Голубой
            "TanhLayer": "#F9E854",  # Жёлтый
            "ReluLayer": "#F98B54",  # Оранжевый
            "SigmoidLayer": "#E854F9",  # Фиолетовый
        }

        return color_map.get(layer_name, "#E0E0E0")  # Серый по умолчанию
