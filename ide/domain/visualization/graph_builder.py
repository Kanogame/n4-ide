"""Построение graphviz графов для визуализации архитектуры нейронной сети.

Модуль предоставляет инструменты для преобразования структуры Sequential модели
в интерактивные диаграммы слоёв и операций.
"""

from typing import Any, Optional
from abc import ABC, abstractmethod


class LayerInfo:
    """Информация об одном слое сети.

    Attributes:
        name: Имя класса слоя (например, "DenseLayer", "SoftmaxLayer").
        index: Порядковый номер слоя в сети.
        input_shape: Форма входного тензора (если доступна).
        output_shape: Форма выходного тензора (если доступна).
        neuron_count: Количество нейронов/выходов слоя (если применимо).
        parameter_count: Количество обучаемых параметров слоя.
        additional_info: Словарь с дополнительной информацией (активация и т.д.).
    """

    def __init__(
        self,
        name: str,
        index: int,
        neuron_count: Optional[int] = None,
        parameter_count: int = 0,
        input_shape: Optional[tuple[int, ...]] = None,
        output_shape: Optional[tuple[int, ...]] = None,
        additional_info: Optional[dict[str, Any]] = None,
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
        self.input_shape = input_shape
        self.output_shape = output_shape
        self.additional_info = additional_info or {}

    def get_label(self) -> str:
        """Получить отформатированный текст для визуализации в графе.

        Returns:
            Многострочный текст с информацией о слое.
        """
        lines = [self.name]

        if self.neuron_count is not None:
            lines.append(f"Neurons: {self.neuron_count}")

        if self.output_shape is not None:
            lines.append(f"Output: {self.output_shape}")

        if self.parameter_count > 0:
            lines.append(f"Params: {self.parameter_count:,}")

        for key, value in self.additional_info.items():
            lines.append(f"{key}: {value}")

        return "\\n".join(lines)


class GraphExporter(ABC):
    """Базовый класс для экспортеров графов.

    Определяет интерфейс для конвертации различных структур в graphviz.
    """

    @abstractmethod
    def export_graphviz(self: "GraphExporter") -> Any:
        """Экспортировать граф в формате graphviz.Digraph.

        Returns:
            graphviz.Digraph объект с визуализацией.
        """
        pass


class LayersGraphBuilder(GraphExporter):
    """Построитель graphviz графа архитектуры слоёв Sequential модели.

    Преобразует Sequential модель в визуальное представление, где каждый слой
    отображается как отдельный узел с информацией о размере и параметрах.

    Example:
        >>> builder = LayersGraphBuilder(sequential_model)
        >>> graph = builder.export_graphviz()
        >>> graph.view()  # Открыть в viewer
    """

    def __init__(self, model: Any) -> None:
        """Инициализировать построитель.

        Args:
            model: Sequential модель из n4 library.

        Raises:
            ValueError: Если модель не является Sequential или не имеет слоёв.
        """
        if not hasattr(model, "layers"):
            raise ValueError("Model must have 'layers' attribute (Sequential model)")

        if not isinstance(model.layers, list) or len(model.layers) == 0:
            raise ValueError("Model must contain at least one layer")

        self.model = model
        self.layers_info = self._extract_layer_info()

    def _extract_layer_info(self: "LayersGraphBuilder") -> list[LayerInfo]:
        """Извлечь информацию из всех слоёв модели.

        Returns:
            Список LayerInfo объектов для каждого слоя.
        """
        layers_info: list[LayerInfo] = []

        for idx, layer in enumerate(self.model.layers):
            info = self._analyze_layer(layer, idx)
            layers_info.append(info)

        return layers_info

    def _analyze_layer(
        self: "LayersGraphBuilder",
        layer: Any,
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
        neuron_count = self._get_neuron_count(layer)

        # Извлечь количество параметров
        parameter_count = self._get_parameter_count(layer)

        # Извлечь форму выхода (если доступна)
        output_shape = self._get_output_shape(layer)

        # Получить дополнительную информацию
        additional_info = self._get_additional_info(layer)

        return LayerInfo(
            name=layer_name,
            index=index,
            neuron_count=neuron_count,
            parameter_count=parameter_count,
            output_shape=output_shape,
            additional_info=additional_info,
        )

    @staticmethod
    def _get_neuron_count(layer: Any) -> Optional[int]:
        """Получить количество нейронов в слое.

        Args:
            layer: Слой для анализа.

        Returns:
            Количество нейронов или None если недоступно.
        """
        # DenseLayer имеет output_size
        if hasattr(layer, "output_size"):
            return layer.output_size

        # SoftmaxLayer и другие слои могут иметь num_classes или logits_count
        if hasattr(layer, "num_classes"):
            return layer.num_classes

        if hasattr(layer, "logits_count"):
            return layer.logits_count

        return None

    @staticmethod
    def _get_parameter_count(layer: Any) -> int:
        """Получить количество обучаемых параметров слоя.

        Args:
            layer: Слой для анализа.

        Returns:
            Количество параметров.
        """
        try:
            if hasattr(layer, "parameters"):
                params = layer.parameters()
                if isinstance(params, list):
                    count = 0
                    for param in params:
                        if hasattr(param, "data"):
                            # Для тензоров посчитать элементы
                            data = param.data
                            if hasattr(data, "size"):
                                count += data.size
                            elif isinstance(data, (list, tuple)):
                                # Для простых типов данных
                                count += len(data)
                    return count
        except Exception:
            pass

        return 0

    @staticmethod
    def _get_output_shape(layer: Any) -> Optional[tuple[int, ...]]:
        """Получить форму выхода слоя.

        Args:
            layer: Слой для анализа.

        Returns:
            Кортеж с формой выхода или None.
        """
        # Попытаться получить output_size как форму
        if hasattr(layer, "output_size"):
            size = layer.output_size
            if isinstance(size, int):
                return (size,)

        return None

    @staticmethod
    def _get_additional_info(layer: Any) -> dict[str, Any]:
        """Получить дополнительную информацию о слое.

        Args:
            layer: Слой для анализа.

        Returns:
            Словарь с дополнительными параметрами слоя.
        """
        info: dict[str, Any] = {}

        # Попытаться получить информацию об активации
        if hasattr(layer, "activation"):
            activation = layer.activation
            if activation is not None:
                info["activation"] = (
                    activation.__class__.__name__
                    if hasattr(activation, "__class__")
                    else str(activation)
                )

        # Добавить input_size если доступен
        if hasattr(layer, "input_size"):
            info["input_size"] = layer.input_size

        return info

    def export_graphviz(self: "LayersGraphBuilder") -> Any:
        """Экспортировать архитектуру слоёв в graphviz.Digraph.

        Создаёт визуальное представление, где:
        - Каждый слой отображается как прямоугольный узел
        - Слои расположены вертикально в порядке выполнения
        - Информация о параметрах и размерах отображается внутри узла

        Returns:
            graphviz.Digraph объект с графом архитектуры.
        """
        from graphviz import Digraph

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


class ComputationalGraphBuilder(GraphExporter):
    """Построитель graphviz графа вычислительного графа операций.

    Преобразует компьютационный граф из n4 library в визуальное представление,
    где операции и значения отображаются как отдельные узлы.

    Примечание: Основная логика уже реализована в CompGraph.export_graphviz(),
    этот класс служит обёрткой для согласованности с архитектурой.
    """

    def __init__(self, comp_graph: Any) -> None:
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

    def export_graphviz(self: "ComputationalGraphBuilder") -> Any:
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
