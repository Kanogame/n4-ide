from typing import Optional, Any, Union, Literal
import numpy as np
from PyQt6.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from ide.presentation.common.layouts import create_vertical_layout


class DatasetVisualizerWidget(QWidget):
    """Виджет для визуализации датасета.

    Отображает двумерные данные (X, y) как scatter plot.
    Поддерживает:
    - Классификацию: метки классов (одномерный массив или one-hot)
    - Регрессию: непрерывные целевые значения с цветовой шкалой (colormap)

    Автоматически определяет тип задачи по данным, либо можно указать явно.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        layout = create_vertical_layout(self)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def set_dataset(
        self,
        X: Any,
        y: Any,
        title: str = "Dataset Visualization",
        task_type: Optional[Literal["classification", "regression"]] = None,
    ) -> None:
        """Отобразить данные датасета.

        Args:
            X: Массив входных данных (n_samples, n_features). Поддерживается только 2D.
            y: Массив целевых значений:
                - Для классификации: (n_samples,) с целочисленными метками
                  или (n_samples, n_classes) в one-hot формате.
                - Для регрессии: (n_samples,) или (n_samples, 1) с вещественными числами.
            title: Название графика.
            task_type: Явное указание типа задачи ("classification" или "regression").
                       Если None, определяется автоматически.
        """
        self.figure.clear()

        X_arr = np.asarray(X)
        y_arr = np.asarray(y)

        # Преобразование one-hot в метки классов
        if y_arr.ndim == 2 and y_arr.shape[1] > 1:
            # Проверим, похоже ли на one-hot (сумма по строке ~1 и значения 0/1)
            if np.all(np.isclose(y_arr.sum(axis=1), 1.0)) and np.all(
                (y_arr == 0) | (y_arr == 1)
            ):
                y_labels = np.argmax(y_arr, axis=1)
            else:
                # Возможно, это регрессия с несколькими выходами — не поддерживается
                y_labels = y_arr.flatten()
        else:
            y_labels = y_arr.flatten()

        # Определение типа задачи
        if task_type is None:
            task_type = self._infer_task_type(y_labels)

        # Проверка размерности X
        if X_arr.ndim != 2 or X_arr.shape[1] != 2:
            ax = self.figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "Датасет должен быть двумерным (n_samples, 2)",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(111)

        if task_type == "classification":
            self._plot_classification(ax, X_arr, y_labels, title)
        else:  # regression
            self._plot_regression(ax, X_arr, y_labels, title)

        self.canvas.draw()

    def _infer_task_type(self, y: np.ndarray) -> str:
        """Автоматически определить тип задачи по целевым значениям."""
        unique_vals = np.unique(y)
        # Если мало уникальных значений и они целые — классификация
        if len(unique_vals) <= 10 and np.all(np.isclose(y, y.astype(int))):
            return "classification"
        return "regression"

    def _plot_classification(
        self, ax, X: np.ndarray, y: np.ndarray, title: str
    ) -> None:
        """Отрисовка scatter plot для классификации."""
        unique_classes = np.unique(y)
        colors = [
            "#005FB8",
            "#DE2FDE",
            "#51CF66",
            "#FFD93D",
            "#A78BFA",
            "#FF6B6B",
            "#4ECDC4",
            "#1A535C",
            "#FF9F1C",
            "#2D3142",
        ]

        for i, class_label in enumerate(unique_classes):
            mask = y == class_label
            X_class = X[mask]
            color = colors[i % len(colors)]
            ax.scatter(
                X_class[:, 0],
                X_class[:, 1],
                c=color,
                label=f"Class {class_label}",
                alpha=0.7,
                s=50,
                edgecolors="black",
                linewidth=0.5,
            )

        ax.set_xlabel("Feature 1")
        ax.set_ylabel("Feature 2")
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_regression(self, ax, X: np.ndarray, y: np.ndarray, title: str) -> None:
        """Отрисовка scatter plot для регрессии с цветовой шкалой."""
        norm = Normalize(vmin=y.min(), vmax=y.max())
        cmap = "viridis"

        scatter = ax.scatter(
            X[:, 0],
            X[:, 1],
            c=y,
            cmap=cmap,
            norm=norm,
            alpha=0.7,
            s=50,
            edgecolors="black",
            linewidth=0.5,
        )

        # Добавление colorbar
        cbar = self.figure.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax)
        cbar.set_label("Target value")

        ax.set_xlabel("Feature 1")
        ax.set_ylabel("Feature 2")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

    def clear(self) -> None:
        """Очистить график."""
        self.figure.clear()
        self.canvas.draw()
