from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPainter


class GraphView(QGraphicsView):
    """Виджет отображения вычислительного графа модели."""

    def __init__(self) -> None:
        super().__init__()

        self.g_scene = QGraphicsScene()
        self.setScene(self.g_scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def wheelEvent(self, event) -> None:
        """Обработка масштабирования колесом мыши."""
        factor = 1.15

        if event.angleDelta().y() > 0:
            self.scale(factor, factor)
        else:
            self.scale(1 / factor, 1 / factor)

    def clear_graph(self) -> None:
        """Очистить граф."""
        self.g_scene.clear()
