from ide.presentation.common.layouts import create_vertical_layout
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

from ide.domain.collectors import CollectorRepository
from ide.presentation.components.common.matplotlib_canvas import MatplotlibCanvasWidget
from ide.presentation.common.mixins import StyledMixin
from ide.presentation.components.common.form_field import FormField
from ide.presentation.components.common.combobox import ComboBox


class MetricsGraphWidget(QFrame, StyledMixin):
    """Виджет для интерактивного отображения графиков метрик.

    Позволяет выбирать метрики для отображения и уровень агрегации
    (по эпохам или по батчам), отображает соответствующий график.

    Signals:
        metric_changed: Сигнал при изменении выбранной метрики.
    """

    # Сигнал при изменении выбранной метрики
    metric_changed = pyqtSignal(str)

    def __init__(
        self,
        metrics_storage: CollectorRepository,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать виджет графиков метрик.

        Args:
            metrics_storage: Хранилище метрик для получения данных.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._apply_style("metrics_graph.qss")

        self._metrics_storage = metrics_storage
        self._current_metric = "loss"
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
        main_layout.addWidget(self.canvas_widget)

    def _create_control_panel(self, layout: QVBoxLayout) -> None:
        """Создать панель управления параметрами графика.

        Args:
            layout: Layout для добавления панели управления.
        """
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(16, 12, 16, 0)
        control_layout.setSpacing(16)

        # Заголовок
        title = QLabel("Графики метрик")
        title_font = QFont("Open Sans", 28)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setObjectName("MetricsGraphTitle")

        control_layout.addWidget(title)
        control_layout.addStretch()

        # Выбор метрики
        self.metric_combo = ComboBox()
        self.metric_combo.addItems(["loss", "accuracy", "f1_score"])
        self.metric_combo.value_changed.connect(self._on_metric_changed)
        self.metric_combo.setObjectName("MetricsGraphMetricCombo")
        metric_field = FormField("График", self.metric_combo)

        control_layout.addWidget(metric_field)

        layout.addLayout(control_layout)

    def _on_metric_changed(self) -> None:
        """Обработчик при изменении выбранной метрики."""
        self._current_metric = self.metric_combo.currentText()
        self.metric_changed.emit(self._current_metric)
        self.update_plot()

    def update_plot(self) -> None:
        """Обновить график на основе выбранной метрики и уровня агрегации."""
        # Получить данные из хранилища
        metric_history = self._metrics_storage.get_metric_history(
            self._current_metric,
            level=self._current_level,
        )

        # Очистить старый график
        self.canvas_widget.clear()

        # Если нет данных, вывести пустой график
        if not metric_history:
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
        x_values = list(range(len(metric_history)))
        label_suffix = "эпохи" if self._current_level == "epoch" else "батчи"

        # Нарисовать линию графика
        ax.plot(
            x_values,
            metric_history,
            linewidth=2.5,
            color="#005FB8",
            marker="o",
            markersize=4,
            markerfacecolor="#005FB8",
            markeredgecolor="white",
            markeredgewidth=1.5,
            label=self._current_metric,
        )

        # Оформить график
        ax.set_xlabel(f"Номер {label_suffix}", fontsize=12, fontweight="normal")
        ax.set_ylabel(
            self._current_metric.capitalize(), fontsize=12, fontweight="normal"
        )
        ax.set_title(
            f"График метрики {self._current_metric} (по {label_suffix})",
            fontsize=14,
            fontweight="normal",
        )
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)
        ax.set_facecolor("rgba(255, 255, 255, 0.70)")

        # Установить минимальные значения осей
        if metric_history:
            min_val = min(metric_history)
            max_val = max(metric_history)
            margin = (max_val - min_val) * 0.1 if max_val != min_val else 0.5
            ax.set_ylim(min_val - margin, max_val + margin)

        # Легенда
        ax.legend(loc="best", fontsize=10)

        # Перерисовать холст
        self.canvas_widget.draw_plot()

    def set_selected_metric(self, metric_name: str) -> None:
        """Установить выбранную метрику.

        Args:
            metric_name: Имя метрики для отображения.
        """
        index = self.metric_combo.findText(metric_name)
        if index >= 0:
            self.metric_combo.setCurrentIndex(index)

    def refresh(self) -> None:
        """Обновить график с текущими данными."""
        self.update_plot()
