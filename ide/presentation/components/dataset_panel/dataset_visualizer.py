from typing import Optional, Any
from PyQt6.QtWidgets import QWidget

from ide.presentation.common.layouts import create_vertical_layout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class DatasetVisualizerWidget(QWidget):
    """Виджет для визуализации датасета.

    Отображает двумерные данные (X, y) как scatter plot,
    где каждый класс обозначен разным цветом.

    Features:
    - Автоматическое масштабирование графика
    - Цветовая кодировка классов
    - Поддержка matplotlib фигур
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать компонент визуализации.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        layout = create_vertical_layout(self)

        # Создать matplotlib фигуру
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

    def set_dataset(
        self,
        X: Any,
        y: Any,
        title: str = "Dataset Visualization",
    ) -> None:
        """Отобразить данные датасета.

        Args:
            X: Массив входных данных (n_samples, n_features).
                Поддерживает только 2D данные.
            y: Массив целевых значений (n_samples,).
            title: Название графика.
        """
        # Очистить предыдущую фигуру
        self.figure.clear()

        # Обработать входные данные
        X_arr = np.asarray(X)
        y_arr = np.asarray(y)

        # Проверить размерность
        if X_arr.ndim != 2 or X_arr.shape[1] != 2:
            # Если не 2D, показать сообщение об ошибке
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

        # Создать subplot
        ax = self.figure.add_subplot(111)

        # Определить уникальные классы
        unique_classes = np.unique(y_arr)

        # Цвета для классов
        colors = ["#0066CC", "#FF6B6B", "#51CF66", "#FFD93D", "#A78BFA"]

        # Нарисовать каждый класс отдельно
        for i, class_label in enumerate(unique_classes):
            mask = y_arr == class_label
            X_class = X_arr[mask]

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

        self.canvas.draw()

    def clear(self) -> None:
        """Очистить график."""
        self.figure.clear()
        self.canvas.draw()
