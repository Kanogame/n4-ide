"""Qt виджет для интерактивной визуализации графов с поддержкой pan и zoom.

Модуль предоставляет компонент QGraphicsView с поддержкой масштабирования
колесом мыши и панорамирования методом перетаскивания.
"""

from typing import Optional, Any, Self
import tempfile
import os

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QPainter, QPixmap, QWheelEvent, QMouseEvent
from PyQt6.QtCore import Qt


class CompGraphViewer(QGraphicsView):
    """Интерактивный визуализатор вычислительных графов.

    Отображает graphviz-граф в интерактивном QGraphicsView с поддержкой:
    - Масштабирования колесом мыши
    - Панорамирования методом перетаскивания левой кнопкой мыши
    - Автоматического подгона графа под размер окна

    Attributes:
        _zoom_factor: Коэффициент масштабирования при прокрутке колеса.
        _current_graph: Текущий отображаемый граф (graphviz.Digraph).
        _is_panning: Флаг активного панорамирования.
        _pan_start_pos: Начальная позиция для панорамирования.
    """

    def __init__(self, parent: Optional[QGraphicsView] = None) -> None:
        """Инициализировать визуализатор графов.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        # Создать сцену для отображения
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Настроить отрисовку
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Настроить режим перетаскивания для панорамирования
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Параметры масштабирования
        self._zoom_factor = 1.15
        self._current_graph: Optional[Any] = None
        self._is_panning = False
        self._pan_start_pos: Optional[Any] = None

    def set_graph(self: Self, graph: Any) -> None:
        """Установить и отобразить graphviz граф.

        Граф преобразуется в SVG, затем конвертируется в изображение
        для отображения в QGraphicsView.

        Args:
            graph: graphviz.Digraph объект для визуализации.

        Raises:
            ValueError: Если граф не имеет метода render.
        """
        if graph is None:
            self.clear_graph()
            return

        if not hasattr(graph, "pipe"):
            raise ValueError("Graph must be a graphviz.Digraph object with pipe method")

        self._current_graph = graph

        try:
            # Отрендерить граф в SVG формат
            svg_data = graph.pipe(format="svg", encoding="utf-8")

            # Преобразовать SVG в PNG через временный файл
            pixmap = self._svg_to_pixmap(svg_data)

            if pixmap is not None:
                self._display_pixmap(pixmap)
            else:
                # Fallback: отобразить текстовое сообщение об ошибке
                self._scene.clear()
                self._scene.addText("Ошибка при отрисовке графа")

        except Exception as e:
            # Обработать ошибку отрисовки

            self._scene.clear()
            self._scene.addText(f"Ошибка графа: {str(e)}")

    def _svg_to_pixmap(self: Self, svg_data: str) -> Optional[QPixmap]:
        """Конвертировать SVG данные в QPixmap.

        Использует временный файл для сохранения SVG и его последующей
        конвертации в растровое изображение.

        Args:
            svg_data: SVG данные в виде строки.

        Returns:
            QPixmap с отрендеренным графом или None при ошибке.
        """
        try:
            # Создать временный файл SVG
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".svg",
                delete=False,
                encoding="utf-8",
            ) as tmp_svg:
                tmp_svg.write(svg_data)
                svg_path = tmp_svg.name

            try:
                # Загрузить SVG как QPixmap
                pixmap = QPixmap(svg_path)

                if pixmap.isNull():
                    # SVG может быть слишком сложным, попробовать через внешний инструмент
                    external_pixmap = self._convert_svg_to_png_external(svg_path)
                    if external_pixmap is not None:
                        pixmap = external_pixmap

                return pixmap if not pixmap.isNull() else None

            finally:
                # Удалить временный файл
                if os.path.exists(svg_path):
                    try:
                        os.unlink(svg_path)
                    except Exception:
                        pass

        except Exception as e:
            print(f"Ошибка при конвертации SVG: {e}")
            return None

    @staticmethod
    def _convert_svg_to_png_external(svg_path: str) -> Optional[QPixmap]:
        """Конвертировать SVG в PNG используя внешние инструменты.

        Пытается использовать convert (ImageMagick) или cairosvg для конвертации.

        Args:
            svg_path: Путь к SVG файлу.

        Returns:
            QPixmap с конвертированным изображением или None при ошибке.
        """
        import subprocess

        png_path = svg_path.replace(".svg", ".png")

        try:
            # Попробовать использовать convert (ImageMagick)
            subprocess.run(
                ["convert", "-density", "150", svg_path, png_path],
                check=True,
                capture_output=True,
                timeout=5,
            )

            pixmap = QPixmap(png_path)

            # Очистить временный PNG файл
            try:
                os.unlink(png_path)
            except Exception:
                pass

            if not pixmap.isNull():
                return pixmap

        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            pass

        return None

    def _display_pixmap(self: Self, pixmap: QPixmap) -> None:
        """Отобразить изображение в сцене с автоматическим подгоном.

        Args:
            pixmap: Изображение для отображения.
        """
        # Очистить старое содержимое сцены
        self._scene.clear()

        # Добавить новое изображение
        item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(item)

        # Установить границы сцены
        self._scene.setSceneRect(self._scene.itemsBoundingRect())

        # Автоматически подогнать вид
        self.fitInView(
            self._scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    def wheelEvent(self: Self, event: Optional[QWheelEvent]) -> None:
        """Обработать событие прокрутки колеса для масштабирования.

        Args:
            event: Событие QWheelEvent с информацией о прокрутке.
        """
        if not event:
            raise ValueError("Event was empty")

        if event.angleDelta().y() > 0:
            # Масштабировать вверх (увеличить)
            self.scale(self._zoom_factor, self._zoom_factor)
        else:
            # Масштабировать вниз (уменьшить)
            self.scale(1 / self._zoom_factor, 1 / self._zoom_factor)

    def mousePressEvent(self: Self, event: Optional[QMouseEvent]) -> None:
        """Обработать нажатие кнопки мыши для инициализации панорамирования.

        Args:
            event: Событие QMouseEvent.
        """
        if not event:
            raise ValueError("Event was empty")

        if event.button() == Qt.MouseButton.MiddleButton:
            # Инициализировать панорамирование средней кнопкой мыши
            self._is_panning = True
            self._pan_start_pos = event.pos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self: Self, event: Optional[QMouseEvent]) -> None:
        """Обработать перемещение мыши для панорамирования.

        Args:
            event: Событие QMouseEvent.
        """
        if not event:
            raise ValueError("Event was empty")

        if self._is_panning and self._pan_start_pos is not None:
            # Вычислить смещение
            delta = event.pos() - self._pan_start_pos
            self._pan_start_pos = event.pos()

            # Применить панорамирование через горизонтальный и вертикальный скролл
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            if h_bar is not None and v_bar is not None:
                h_bar.setValue(h_bar.value() - delta.x())
                v_bar.setValue(v_bar.value() - delta.y())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self: Self, event: Optional[QMouseEvent]) -> None:
        """Обработать отпускание кнопки мыши для завершения панорамирования.

        Args:
            event: Событие QMouseEvent.
        """
        if not event:
            raise ValueError("Event was empty")

        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = False
            self._pan_start_pos = None

        super().mouseReleaseEvent(event)

    def clear_graph(self: Self) -> None:
        """Очистить отображаемый граф.

        Удаляет все элементы из сцены и сбрасывает текущий граф.
        """
        self._scene.clear()
        self._current_graph = None

    def fit_in_view(self: Self) -> None:
        """Автоматически подогнать граф под размер окна.

        Масштабирует граф так, чтобы он полностью вмещался в видимую область.
        """
        if not self._scene.items():
            return

        self.fitInView(
            self._scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    def reset_zoom(self: Self) -> None:
        """Сбросить масштабирование и отобразить граф в нормальном размере."""
        self.resetTransform()
        self.fit_in_view()
