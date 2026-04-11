from ide.presentation.common.layouts import create_vertical_layout
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

from ide.domain.collectors import CollectorRepository
from ide.presentation.components.common.matplotlib_canvas import MatplotlibCanvasWidget
from ide.presentation.common.mixins import StyledMixin
from ide.presentation.components.common.form_field import FormField
from ide.presentation.components.common.combobox import ComboBox


class MetricsGraphWidget(QFrame, StyledMixin):
    """Виджет для интерактивного отображения графиков сборщиков.

    Позволяет выбирать сборщики для отображения и уровень детализации
    (по эпохам или по батчам), отображает соответствующий график.
    В режиме батчей отмечает границы эпох вертикальными линиями.

    Signals:
        metric_changed: Сигнал при изменении выбранного сборщика.
    """

    # Сигнал при изменении выбранного сборщика
    metric_changed = pyqtSignal(str)

    def __init__(
        self,
        metrics_storage: CollectorRepository,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать виджет графиков сборщиков.

        Args:
            metrics_storage: Хранилище сборщиков для получения данных.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("metrics_graph.qss")

        self._metrics_storage = metrics_storage
        self._current_collector = "loss"
        self._current_level = "epoch"

        # Основной layout
        main_layout = create_vertical_layout(self, 12)

        # Панель управления графиком
        self._create_control_panel(main_layout)

        # Холст для отображения графика
        self.canvas_widget = MatplotlibCanvasWidget(
            width=10,
            height=6,
            dpi=100,
            parent=self,
        )
        self.canvas_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.canvas_widget)

    def _create_control_panel(self, layout: QVBoxLayout) -> None:
        """Создать панель управления параметрами графика.

        Args:
            layout: Layout для добавления панели управления.
        """
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(16, 12, 16, 0)
        control_layout.setSpacing(16)

        # Выбор сборщика - будет заполнена динамически
        self.collector_combo = ComboBox()
        # Изначально пусто, заполнится при обновлении графика
        self.collector_combo.value_changed.connect(self._on_collector_changed)
        self.collector_combo.setObjectName("MetricsGraphCollectorCombo")
        collector_field = FormField("Сборщик", self.collector_combo)

        control_layout.addWidget(collector_field)

        # Выбор уровня детализации
        self.level_combo = ComboBox()
        self.level_combo.addItems(["Эпохи", "Батчи"])
        self.level_combo.value_changed.connect(self._on_level_changed)
        self.level_combo.setObjectName("MetricsGraphLevelCombo")
        level_field = FormField("Детализация", self.level_combo)

        control_layout.addWidget(level_field)

        layout.addLayout(control_layout)

    def _on_collector_changed(self) -> None:
        """Обработчик при изменении выбранного сборщика."""
        self._current_collector = self.collector_combo.currentText()
        self.metric_changed.emit(self._current_collector)
        self.update_plot()

    def _on_level_changed(self) -> None:
        """Обработчик при изменении уровня детализации."""
        level_text = self.level_combo.currentText()
        self._current_level = "epoch" if level_text == "Эпохи" else "batch"
        self.update_plot()

    def _update_collectors_combobox(self) -> None:
        """Обновить список доступных сборщиков в combobox на основе собранных данных.

        Получает из хранилища список имен всех сборщиков, которые были
        активны во время обучения, и заполняет combobox только ними.
        Если текущий сборщик больше недоступен, переключается на первый.
        """
        # Получить список всех собранных сборщиков
        available_collectors = self._metrics_storage.get_collectors_names()

        # Заблокировать сигналы чтобы не вызывать обновление графика
        self.collector_combo.blockSignals(True)

        # Запомнить текущий выбор
        current_text = self.collector_combo.currentText()

        # Очистить и заново заполнить combobox
        self.collector_combo.clear()
        self.collector_combo.addItems(sorted(available_collectors))

        # Если старый выбор еще доступен, восстановить его
        if current_text in available_collectors:
            index = self.collector_combo.findText(current_text)
            if index >= 0:
                self.collector_combo.setCurrentIndex(index)
                self._current_collector = current_text
        elif available_collectors:
            # Иначе выбрать первый доступный
            self.collector_combo.setCurrentIndex(0)
            self._current_collector = available_collectors[0]

        # Разблокировать сигналы
        self.collector_combo.blockSignals(False)

    def update_plot(self) -> None:
        """Обновить график на основе выбранного сборщика и уровня детализации."""
        # Обновить доступные сборщики в combobox
        self._update_collectors_combobox()

        # Получить данные из хранилища
        collector_history = self._metrics_storage.get_collector_history(
            self._current_collector,
            level=self._current_level,
        )

        # Очистить старый график
        self.canvas_widget.clear()

        # Если нет данных, вывести пустой график
        if not collector_history:
            ax = self.canvas_widget.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "Данные отсутствуют",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=16,
                color="rgba(0, 0, 0, 0.4)",
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            self.canvas_widget.draw_plot()
            return

        # Создать новый график
        ax = self.canvas_widget.add_subplot(111)

        # Определить количество шагов для оси X
        x_values = list(range(len(collector_history)))

        # Определить подпись оси X
        if self._current_level == "epoch":
            label_suffix = "эпохи"
        else:
            label_suffix = "батчи"

        # Нарисовать линию графика
        ax.plot(
            x_values,
            collector_history,
            linewidth=2.5,
            color="#005FB8",
            marker="o",
            markersize=4,
            markerfacecolor="#005FB8",
            markeredgecolor="white",
            markeredgewidth=1.5,
            label=self._current_collector,
        )

        # Добавить вертикальные линии границ эпох в режиме батчей
        if self._current_level == "batch":
            self._add_epoch_markers(ax)

        # Оформить график
        ax.set_xlabel(f"Номер {label_suffix}", fontsize=12, fontweight="normal")
        ax.set_ylabel(
            self._current_collector.capitalize(), fontsize=12, fontweight="normal"
        )
        ax.set_title(
            f"График сборщика {self._current_collector} (по {label_suffix})",
            fontsize=14,
            fontweight="normal",
        )
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
        ax.set_facecolor((1.0, 1.0, 1.0, 0.70))

        # Установить минимальные значения осей
        if collector_history:
            min_val = min(collector_history)
            max_val = max(collector_history)
            margin = (max_val - min_val) * 0.1 if max_val != min_val else 0.5
            ax.set_ylim(min_val - margin, max_val + margin)

        # Легенда
        ax.legend(loc="best", fontsize=10)

        # Перерисовать холст
        self.canvas_widget.draw_plot()

    def _add_epoch_markers(self, ax) -> None:
        """Добавить вертикальные линии, обозначающие границы эпох.

        Args:
            ax: Объект matplotlib axis для рисования.
        """
        # Получить информацию о границах эпох из батчей
        batch_records = self._metrics_storage.get_all_batch_records()

        if not batch_records:
            return

        # Найти индексы первого батча каждой эпохи
        epoch_boundaries = []
        current_epoch = -1

        for record in batch_records:
            if record.epoch_index != current_epoch:
                epoch_boundaries.append(record.batch_index)
                current_epoch = record.epoch_index

        # Нарисовать вертикальные линии на границах эпох (кроме первой)
        for boundary_idx in epoch_boundaries[1:]:
            ax.axvline(
                x=boundary_idx - 0.5,
                color="red",
                linestyle=":",
                linewidth=1.5,
                alpha=0.6,
            )

    def set_selected_collector(self, collector_name: str) -> None:
        """Установить выбранный сборщик.

        Args:
            collector_name: Имя сборщика для отображения.
        """
        index = self.collector_combo.findText(collector_name)
        if index >= 0:
            self.collector_combo.setCurrentIndex(index)

    def refresh(self) -> None:
        """Обновить график с текущими данными."""
        self.update_plot()
