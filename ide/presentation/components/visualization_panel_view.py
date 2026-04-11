from graphviz import Digraph
from n4.nn import Sequential, Model
from n4.core import CompGraph
from enum import Enum, auto
from typing import Optional, Self
from dataclasses import dataclass

from PyQt6.QtWidgets import QWidget

from ide.presentation.common.mixins import StyledMixin
from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.panel_view import PanelView
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.common.form_field import FormField
from ide.presentation.components.visualization_panel import CompGraphViewer
from ide.domain.visualization import (
    LayersGraphBuilder,
    ComputationalGraphBuilder,
)


class VisualizationMode(Enum):
    """Режимы визуализации."""

    COMPUTATIONAL = auto()
    LAYERS = auto()


@dataclass()
class VisualizationState:
    """Неизменяемое состояние визуализации.

    Attributes:
        model: Текущая модель для визуализации.
        comp_graph: Вычислительный граф (если доступен).
        backend: Выбранный вычислительный бекенд.
        visualization_mode: Текущий режим визуализации ("computational" или "layers").
    """

    model: Optional[Model] = None
    comp_graph: Optional[CompGraph] = None
    visualization_mode: VisualizationMode = VisualizationMode.LAYERS


class VisualizationPanelView(QWidget, StyledMixin):
    """Панель интерактивной визуализации архитектуры и вычислений модели.

    Компонент отображает структуру сети двумя способами:
    - Послойно: каждый слой как отдельный узел с параметрами
    - Вычислительный граф: операции и промежуточные значения

    Поддерживается pan & zoom

    Signals:
        None (read-only visualization)
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать панель визуализации.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("visualization_panel.qss")

        # Состояние панели
        self._visualization_state = VisualizationState()

        # Основной layout
        layout = create_vertical_layout(self)

        # Создать панель с информацией
        self.main_content = PanelView("Визуализация модели")

        # Создать селектор режима визуализации
        self.create_visualization_mode_selector()

        # Создать граф-визуализатор
        self.create_graph_viewer()

        layout.addWidget(self.main_content)

    def create_visualization_mode_selector(self: Self) -> None:
        """Создать выпадающий список выбора режима визуализации.

        Режимы:
        - Послойно: Архитектура слоёв модели
        - Вычислительный граф: Операции и значения из прямого прохода
        """
        self.mode_combo = ComboBox()
        self.mode_combo.addItems(["Послойно", "Вычислительный граф"])
        self.mode_combo.value_changed.connect(self._on_visualization_mode_changed)

        mode_field = FormField("Тип визуализации", self.mode_combo)
        self.main_content.add_widget(mode_field)

    def create_graph_viewer(self: Self) -> None:
        """Создать интерактивный граф-визуализатор.

        Граф поддерживает:
        - Масштабирование колесом мыши
        - Панорамирование средней кнопкой мыши + перетаскивание
        - Автоматическое подгон размера
        """
        self.graph_viewer = CompGraphViewer()
        self.main_content.add_widget(self.graph_viewer)

    def set_model(self: Self, model: Model) -> None:
        """Установить модель для визуализации и отобразить её архитектуру.

        Args:
            model: Объект Sequential модели из n4 library.

        Raises:
            ValueError: Если модель некорректна.
        """
        try:
            if model is None:
                self._visualization_state = VisualizationState()
                self.graph_viewer.clear_graph()
                return

            # Обновить состояние, сохраняя вычислительный граф
            state = VisualizationState(
                model=model,
                comp_graph=self._visualization_state.comp_graph,
                visualization_mode=self._visualization_state.visualization_mode,
            )

            self._visualization_state = state

            # Отобразить текущий режим визуализации
            self._update_visualization()

        except Exception as e:
            print(f"Ошибка при установке модели: {e}")
            self.graph_viewer.clear_graph()

    def set_computational_graph(self: Self, comp_graph: CompGraph) -> None:
        """Установить вычислительный граф для визуализации.

        Args:
            comp_graph: CompGraph объект из n4 library (результат collect_graph).
        """
        try:
            # Обновить состояние
            self._visualization_state = VisualizationState(
                model=self._visualization_state.model,
                comp_graph=comp_graph,
                visualization_mode=self._visualization_state.visualization_mode,
            )

            # Если активен режим вычислительного графа, обновить отображение
            self._update_visualization()

        except Exception as e:
            print(f"Ошибка при установке вычислительного графа: {e}")

    def _on_visualization_mode_changed(self: Self, mode_name: str) -> None:
        """Обработчик изменения режима визуализации.

        Args:
            mode_name: Название выбранного режима ("Послойно" или "Вычислительный граф").
        """
        # Преобразовать названиие в константу режима
        mode_map = {
            "Послойно": VisualizationMode.LAYERS,
            "Вычислительный граф": VisualizationMode.COMPUTATIONAL,
        }

        mode = mode_map.get(mode_name, VisualizationMode.LAYERS)

        # Обновить состояние
        self._visualization_state = VisualizationState(
            model=self._visualization_state.model,
            comp_graph=self._visualization_state.comp_graph,
            visualization_mode=mode,
        )

        # Обновить визуализацию
        self._update_visualization()

    def _update_visualization(self: Self) -> None:
        """Обновить отображение графа в соответствии с текущим режимом.

        Выбирает построитель графа (слои или вычислительный) в зависимости
        от режима и отображает результат.
        """

        try:
            mode = self._visualization_state.visualization_mode

            if mode == VisualizationMode.LAYERS:
                self._display_layers_graph()
            elif mode == VisualizationMode.COMPUTATIONAL:
                self._display_computational_graph()
            else:
                self.graph_viewer.clear_graph()

        except Exception as e:
            print(f"Ошибка при обновлении визуализации: {e}")
            self.graph_viewer.clear_graph()

    def _display_layers_graph(self: Self) -> None:
        """Отобразить архитектуру слоёв модели.

        Создаёт граф на основе Sequential модели и отображает информацию
        о каждом слое (тип, количество нейронов, параметры и т.д.).
        """
        model = self._visualization_state.model

        if model is None:
            self.graph_viewer.clear_graph()
            return

        try:
            # Построить граф архитектуры слоёв
            builder = LayersGraphBuilder(model)
            graph = builder.export_graphviz()

            # Отобразить граф
            self.graph_viewer.set_graph(graph)
        except Exception as e:
            print(f"Ошибка при построении графа слоёв: {e}")
            self.graph_viewer.clear_graph()

    def _display_computational_graph(self: Self) -> None:
        """Отобразить вычислительный граф операций.

        Создаёт граф на основе CompGraph с операциями и промежуточными значениями.
        """
        comp_graph = self._visualization_state.comp_graph

        if comp_graph is None:
            self.graph_viewer.clear_graph()
            return

        # Обернуть в построитель для согласованности
        builder = ComputationalGraphBuilder(comp_graph)
        graph = builder.export_graphviz()

        # Отобразить граф
        self.graph_viewer.set_graph(graph)
