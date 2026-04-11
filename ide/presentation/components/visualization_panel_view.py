"""Панель визуализации вычислительного графа и архитектуры модели.

Предоставляет интерактивную визуализацию двух видов:
1. Вычислительный граф - операции и значения из прямого прохода модели
2. Послойно - архитектура модели с информацией о слоях и параметрах
"""

from typing import Optional, Any, Self
from dataclasses import dataclass

from PyQt6.QtWidgets import QWidget

from ide.presentation.common.mixins import StyledMixin
from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.panel_view import PanelView
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.common.form_field import FormField
from ide.presentation.components.common.comp_graph_viewer import CompGraphViewer
from ide.domain.visualization.graph_builder import (
    LayersGraphBuilder,
    ComputationalGraphBuilder,
)


@dataclass(frozen=True)
class VisualizationState:
    """Неизменяемое состояние визуализации.

    Attributes:
        model: Текущая модель для визуализации.
        comp_graph: Вычислительный граф (если доступен).
        backend: Выбранный вычислительный бекенд.
        visualization_mode: Текущий режим визуализации ("computational" или "layers").
    """

    model: Optional[Any] = None
    comp_graph: Optional[Any] = None
    backend: str = "PyFloat"
    visualization_mode: str = "layers"


class VisualizationMode:
    """Режимы визуализации."""

    COMPUTATIONAL = "computational"
    LAYERS = "layers"


class VisualizationPanelView(QWidget, StyledMixin):
    """Панель интерактивной визуализации архитектуры и вычислений модели.

    Компонент отображает структуру сети двумя способами:
    - Послойно: каждый слой как отдельный узел с параметрами
    - Вычислительный граф: операции и промежуточные значения

    Supports pan and zoom navigation for large graphs.

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

    def set_model(self: Self, model: Any) -> None:
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

            # Обновить состояние
            state = VisualizationState(
                model=model,
                backend=self._visualization_state.backend,
                visualization_mode=self._visualization_state.visualization_mode,
            )

            self._visualization_state = state

            # Отобразить текущий режим визуализации
            self._update_visualization()

        except Exception as e:
            print(f"Ошибка при установке модели: {e}")
            self.graph_viewer.clear_graph()

    def set_computational_graph(self: Self, comp_graph: Any) -> None:
        """Установить вычислительный граф для визуализации.

        Args:
            comp_graph: CompGraph объект из n4 library (результат collect_graph).
        """
        try:
            if comp_graph is None:
                # Очистить вычислительный граф
                state = VisualizationState(
                    model=self._visualization_state.model,
                    comp_graph=None,
                    backend=self._visualization_state.backend,
                    visualization_mode=self._visualization_state.visualization_mode,
                )
                self._visualization_state = state

                # Если активен режим вычислительного графа, обновить
                if (
                    self._visualization_state.visualization_mode
                    == VisualizationMode.COMPUTATIONAL
                ):
                    self.graph_viewer.clear_graph()

                return

            # Обновить состояние
            state = VisualizationState(
                model=self._visualization_state.model,
                comp_graph=comp_graph,
                backend=self._visualization_state.backend,
                visualization_mode=self._visualization_state.visualization_mode,
            )

            self._visualization_state = state

            # Если активен режим вычислительного графа, обновить отображение
            if (
                self._visualization_state.visualization_mode
                == VisualizationMode.COMPUTATIONAL
            ):
                self._update_visualization()

        except Exception as e:
            print(f"Ошибка при установке вычислительного графа: {e}")

    def set_backend(self: Self, backend: str) -> None:
        """Установить выбранный вычислительный бекенд.

        Args:
            backend: Имя бекенда (например, "PyFloat", "NumPy", "PyTorch").
        """
        state = VisualizationState(
            model=self._visualization_state.model,
            comp_graph=self._visualization_state.comp_graph,
            backend=backend,
            visualization_mode=self._visualization_state.visualization_mode,
        )

        self._visualization_state = state

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
        state = VisualizationState(
            model=self._visualization_state.model,
            comp_graph=self._visualization_state.comp_graph,
            backend=self._visualization_state.backend,
            visualization_mode=mode,
        )

        self._visualization_state = state

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

        try:
            # Обернуть в построитель для согласованности
            builder = ComputationalGraphBuilder(comp_graph)
            graph = builder.export_graphviz()

            # Отобразить граф
            self.graph_viewer.set_graph(graph)

        except TypeError as e:
            # Может быть ошибка типа если граф некорректен
            print(f"Ошибка типа при построении вычислительного графа: {e}")
            self.graph_viewer.clear_graph()
        except Exception as e:
            print(f"Ошибка при построении вычислительного графа: {e}")
            self.graph_viewer.clear_graph()

    def get_current_state(self: Self) -> VisualizationState:
        """Получить текущее состояние визуализации.

        Returns:
            VisualizationState с текущими параметрами.
        """
        return self._visualization_state

    def reset_zoom(self: Self) -> None:
        """Сбросить масштабирование и отобразить граф в нормальном размере."""
        self.graph_viewer.reset_zoom()

    def fit_in_view(self: Self) -> None:
        """Автоматически подогнать граф под размер окна."""
        self.graph_viewer.fit_in_view()
