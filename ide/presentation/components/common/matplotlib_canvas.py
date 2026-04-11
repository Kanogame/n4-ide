from typing import Optional
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class MatplotlibCanvas(FigureCanvas):
    """Встраиваемый виджет для отображения matplotlib графиков в PyQt6.

    Предоставляет возможность отображения и обновления графиков
    с поддержкой интерактивных инструментов (zoom, pan, save).
    """

    def __init__(
        self,
        width: float = 8,
        height: float = 6,
        dpi: int = 100,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать холст matplotlib.

        Args:
            width: Ширина фигуры в дюймах.
            height: Высота фигуры в дюймах.
            dpi: Разрешение в точках на дюйм.
            parent: Родительский виджет.
        """
        # Создать фигуру matplotlib
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor("white")

        # Инициализировать FigureCanvas
        super().__init__(self.fig)
        self.setParent(parent)

        # Установить качество графика
        self.fig.tight_layout()

    def clear(self) -> None:
        """Очистить все оси на фигуре."""
        self.fig.clear()

    def add_subplot(self, *args, **kwargs):
        """Добавить подграфик на фигуру.

        Args:
            *args: Позиционные аргументы для add_subplot.
            **kwargs: Именованные аргументы для add_subplot.

        Returns:
            Объект Axes для рисования графика.
        """
        return self.fig.add_subplot(*args, **kwargs)

    def draw_plot(self) -> None:
        """Перерисовать график."""
        self.draw()

    def set_background_color(self, color: str) -> None:
        """Установить цвет фона фигуры.

        Args:
            color: Цвет в формате hex или названия (e.g., '#ffffff', 'white').
        """
        self.fig.patch.set_facecolor(color)


class MatplotlibCanvasWidget(QWidget):
    """Виджет-обертка для встраивания matplotlib графика в PyQt6 интерфейс.

    Включает панель инструментов (toolbar) для интерактивного управления графиком.
    """

    def __init__(
        self,
        width: float = 8,
        height: float = 6,
        dpi: int = 100,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать виджет с matplotlib холстом.

        Args:
            width: Ширина фигуры в дюймах.
            height: Высота фигуры в дюймах.
            dpi: Разрешение в точках на дюйм.
            show_toolbar: Показывать ли панель инструментов.
            parent: Родительский виджет.
        """
        super().__init__(parent)

        # Создать layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создать холст matplotlib
        self.canvas = MatplotlibCanvas(width, height, dpi, parent=self)
        layout.addWidget(self.canvas)

    def get_canvas(self) -> MatplotlibCanvas:
        """Получить объект холста matplotlib.

        Returns:
            MatplotlibCanvas для рисования графиков.
        """
        return self.canvas

    def clear(self) -> None:
        """Очистить все оси на холсте."""
        self.canvas.clear()

    def add_subplot(self, *args, **kwargs):
        """Добавить подграфик.

        Args:
            *args: Позиционные аргументы для add_subplot.
            **kwargs: Именованные аргументы для add_subplot.

        Returns:
            Объект Axes для рисования.
        """
        return self.canvas.add_subplot(*args, **kwargs)

    def draw_plot(self) -> None:
        """Перерисовать график."""
        self.canvas.draw_plot()

    def set_background_color(self, color: str) -> None:
        """Установить цвет фона.

        Args:
            color: Цвет в формате hex или названия.
        """
        self.canvas.set_background_color(color)
