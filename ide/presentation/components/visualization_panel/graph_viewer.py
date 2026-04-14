"""Интерактивный визуализатор graphviz графов с поддержкой панорамирования и масштабирования.

Компонент отображает SVG графы (вычислительные и слои архитектуры) с поддержкой:
- Масштабирования колесом мыши (Ctrl+колесо мыши).
- Панорамирования средней кнопкой мыши + перетаскивание.
- Автоматического подгона графа под размер окна.
- Динамического отображения сетки точек в зависимости от позиции камеры.
- Потокового рендеринга SVG для избежания зависания главного потока.
"""

from typing import Optional, Any
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import (
    QPainter,
    QWheelEvent,
    QMouseEvent,
    QPen,
    QColor,
    QBrush,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject


class SvgRenderWorker(QObject):
    """Рабочий поток для рендеринга SVG данных.

    Выполняет потребительское преобразование SVG данных в отдельном потоке,
    чтобы не замораживать главный UI поток при обработке больших графов.

    Signals:
        render_finished: Испускается после успешного рендеринга.
        render_failed: Испускается при ошибке рендеринга.
    """

    render_finished = pyqtSignal(bytes)  # SVG данные в байтах.
    render_failed = pyqtSignal(str)  # Сообщение об ошибке.

    def __init__(self, svg_data: str) -> None:
        """Инициализировать рабочий процесс.

        Args:
            svg_data: SVG содержимое в виде строки.
        """
        super().__init__()
        self.svg_data = svg_data

    def run(self) -> None:
        """Выполнить рендеринг SVG.

        Проверяет валидность SVG данных и преобразует их в байты.
        """
        try:
            # Убедиться, что SVG валиден путём попытки загрузить его.
            svg_bytes = self.svg_data.encode("utf-8")
            renderer = QSvgRenderer()

            if not renderer.load(svg_bytes):
                self.render_failed.emit("Failed to parse SVG data from graphviz")
                return

            # Удалить фоновый цвет из SVG (установить прозрачный фон).
            svg_with_transparency = self._make_svg_transparent(
                svg_bytes.decode("utf-8")
            )
            self.render_finished.emit(svg_with_transparency.encode("utf-8"))

        except Exception as e:
            self.render_failed.emit(f"SVG rendering error: {str(e)}")

    @staticmethod
    def _make_svg_transparent(svg_data: str) -> str:
        """Сделать фон SVG прозрачным.

        Удаляет или изменяет атрибут фона в SVG для получения прозрачного фона.

        Args:
            svg_data: Исходные SVG данные.

        Returns:
            SVG данные с прозрачным фоном.
        """
        import re

        # Удалить white background из SVG.
        svg_data = svg_data.replace(
            'fill="white"',
            'fill="none"',
        )

        # Замени любые фоновые цвета на прозрачность.
        svg_data = re.sub(r'fill="white"', 'fill="none"', svg_data)

        # Убрать фоновый rect если есть.
        svg_data = re.sub(
            r'<rect[^>]*width="[^"]*"[^>]*height="[^"]*"[^>]*fill="white"[^>]*/>',
            "",
            svg_data,
        )

        return svg_data


class GridBackground:
    """Вспомогательный класс для рендеринга сетки точек.

    Рисует динамическую сетку точек на основе текущей позиции и масштаба камеры.
    Вместо предварительного создания миллионов точек, точки отображаются динамически
    при отрисовке сцены.
    """

    DOT_COLOR = QColor("#AEAEAE")
    DOT_SPACING = 50  # Интервал между точками в пикселях.

    @staticmethod
    def paint_grid(painter: QPainter, viewport_rect: Any) -> None:
        """Отрисовать сетку точек в области viewport.

        Args:
            painter: QPainter для отрисовки.
            viewport_rect: Прямоугольник области видимости сцены.
        """
        # Получить координаты области видимости.
        x_start = int(viewport_rect.left())
        y_start = int(viewport_rect.top())
        x_end = int(viewport_rect.right())
        y_end = int(viewport_rect.bottom())

        # Выровнять координаты на сетку для получения правильной позиции точек.
        x_start = (x_start // GridBackground.DOT_SPACING) * GridBackground.DOT_SPACING
        y_start = (y_start // GridBackground.DOT_SPACING) * GridBackground.DOT_SPACING

        # Установить цвет и размер точек.
        painter.setPen(QPen(GridBackground.DOT_COLOR))
        painter.setBrush(QBrush(GridBackground.DOT_COLOR))

        # Отрисовать точки в видимой области.
        x = x_start
        while x <= x_end:
            y = y_start
            while y <= y_end:
                painter.drawEllipse(x, y, 2, 2)
                y += GridBackground.DOT_SPACING

            x += GridBackground.DOT_SPACING


class GraphViewer(QGraphicsView):
    """Интерактивный визуализатор graphviz графов в формате SVG.

    Отображает SVG содержимое от graphviz с поддержкой:
    - Масштабирования (Ctrl + прокрутка колеса мыши).
    - Панорамирования (средняя кнопка мыши + перетаскивание).
    - Автоматического подгона размера при загрузке нового графа.
    - Динамической сетки точек для ориентации.
    - Потокового рендеринга для избежания зависания UI.

    Attributes:
        _zoom_factor: Коэффициент увеличения/уменьшения при масштабировании.
        _current_graph: Текущий загруженный граф (graphviz.Digraph).
        _is_panning: Флаг активного панорамирования.
        _pan_start_pos: Начальная позиция панорамирования.
        _svg_item: Текущий отображаемый SVG элемент.
        _render_thread: Рабочий поток для рендеринга SVG.
    """

    def __init__(self, parent: Optional["QGraphicsView"] = None) -> None:
        """Инициализировать визуализатор графов.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        # Создать сцену для отображения.
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Настроить качество отрисовки.
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Настроить режим отображения сцены.
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        # Параметры масштабирования.
        self._zoom_factor = 1.15
        self._current_graph: Optional[Any] = None
        self._is_panning = False
        self._pan_start_pos: Optional[Any] = None
        self._svg_item: Optional[QGraphicsSvgItem] = None
        self._svg_renderer: Optional[QSvgRenderer] = None
        self._render_thread: Optional[QThread] = None
        self._render_worker: Optional[SvgRenderWorker] = None

        # Инициализировать сцену большим размером.
        scene_size = 10000
        self._scene.setSceneRect(
            -scene_size, -scene_size, scene_size * 2, scene_size * 2
        )

    def set_graph(self: "GraphViewer", graph: Any) -> None:
        """Установить и отобразить graphviz граф в формате SVG.

        Граф преобразуется в SVG данные в отдельном потоке, затем отображаются
        как QGraphicsSvgItem для получения высокого качества масштабирования.

        Args:
            graph: graphviz.Digraph объект для визуализации.

        Raises:
            ValueError: Если граф не имеет метода pipe или невалиден.
        """
        if graph is None:
            self.clear_graph()
            return

        if not hasattr(graph, "pipe"):
            raise ValueError("Graph must be a graphviz.Digraph object with pipe method")

        self._current_graph = graph

        try:
            # Получить SVG данные из graphviz (это быстро, так что в основном потоке).
            svg_data = graph.pipe(format="svg", encoding="utf-8")

            # Запустить рендеринг в отдельном потоке.
            self._render_svg_async(svg_data)

        except Exception as e:
            # Обработать ошибку.
            self.clear_graph()
            error_text = self._scene.addText(f"Ошибка графа: {str(e)}")
            if error_text is not None:
                error_text.setDefaultTextColor(QColor("red"))

    def _render_svg_async(self: "GraphViewer", svg_data: str) -> None:
        """Запустить асинхронный рендеринг SVG в отдельном потоке.

        Args:
            svg_data: SVG содержимое для рендеринга.
        """
        # Остановить предыдущий рендеринг если он ещё выполняется.
        if self._render_thread is not None and self._render_thread.isRunning():
            self._render_thread.quit()
            self._render_thread.wait()

        # Создать рабочий процесс.
        self._render_worker = SvgRenderWorker(svg_data)
        self._render_thread = QThread()
        self._render_worker.moveToThread(self._render_thread)

        # Подключить сигналы.
        self._render_thread.started.connect(self._render_worker.run)
        self._render_worker.render_finished.connect(self._on_svg_render_finished)
        self._render_worker.render_failed.connect(self._on_svg_render_failed)
        self._render_thread.finished.connect(self._render_thread.deleteLater)

        # Запустить поток.
        self._render_thread.start()

    def _on_svg_render_finished(self: "GraphViewer", svg_bytes: bytes) -> None:
        """Обработчик успешного рендеринга SVG.

        Args:
            svg_bytes: SVG данные в байтах (готовые для загрузки).
        """
        try:
            self._display_svg(svg_bytes)
        except Exception as e:
            print(f"Ошибка при отображении SVG: {e}")
            self.clear_graph()

    def _on_svg_render_failed(self: "GraphViewer", error_message: str) -> None:
        """Обработчик ошибки рендеринга SVG.

        Args:
            error_message: Сообщение об ошибке.
        """
        print(f"Ошибка рендеринга SVG: {error_message}")
        self.clear_graph()
        error_text = self._scene.addText(error_message)
        if error_text is not None:
            error_text.setDefaultTextColor(QColor("red"))

    def _display_svg(self: "GraphViewer", svg_bytes: bytes) -> None:
        """Отобразить SVG данные в сцене.

        Использует QGraphicsSvgItem для отображения SVG без потери качества
        при масштабировании.

        Args:
            svg_bytes: SVG содержимое в байтах.
        """
        # Удалить старый SVG элемент.
        if self._svg_item is not None:
            self._scene.removeItem(self._svg_item)
            self._svg_item = None

        # Удалить старый рендерер.
        self._svg_renderer = None

        # Создать новый SVG рендер из данных.
        self._svg_renderer = QSvgRenderer()
        if not self._svg_renderer.load(svg_bytes):
            raise RuntimeError("Failed to load SVG from graphviz output")

        # Создать SVG элемент.
        self._svg_item = QGraphicsSvgItem()
        self._svg_item.setSharedRenderer(self._svg_renderer)
        self._svg_item.setZValue(10)  # Поместить над фоном.

        # Добавить в сцену.
        self._scene.addItem(self._svg_item)

        # Автоматически подогнать вид.
        self.fit_in_view()

    def drawBackground(
        self: "GraphViewer", painter: Optional[QPainter], rect: Any
    ) -> None:
        """Отрисовать фон с сеткой точек.

        Переопределяет метод отрисовки фона для отображения динамической сетки.

        Args:
            painter: QPainter для отрисовки.
            rect: Область видимости.
        """
        # Отрисовать стандартный фон.
        super().drawBackground(painter, rect)

        # Отрисовать сетку точек.
        if painter is not None:
            GridBackground.paint_grid(painter, rect)

    def wheelEvent(self: "GraphViewer", event: Optional[QWheelEvent]) -> None:
        """Обработать событие прокрутки колеса мыши для масштабирования.

        Масштабирование работает при нажатой клавише Ctrl. Направление прокрутки
        определяет увеличение (вверх) или уменьшение (вниз) масштаба.

        Args:
            event: Событие QWheelEvent с информацией о прокрутке.
        """
        if not event:
            raise ValueError("Event was empty")

        # Проверить, нажата ли клавиша Ctrl для масштабирования.
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                # Масштабировать вверх (увеличить).
                self.scale(self._zoom_factor, self._zoom_factor)
            else:
                # Масштабировать вниз (уменьшить).
                self.scale(1 / self._zoom_factor, 1 / self._zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self: "GraphViewer", event: Optional[QMouseEvent]) -> None:
        """Обработать нажатие кнопки мыши для инициализации панорамирования.

        Панорамирование активируется средней кнопкой мыши.

        Args:
            event: Событие QMouseEvent.
        """
        if not event:
            raise ValueError("Event was empty")

        if event.button() == Qt.MouseButton.MiddleButton:
            # Инициализировать панорамирование средней кнопкой мыши.
            self._is_panning = True
            self._pan_start_pos = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self: "GraphViewer", event: Optional[QMouseEvent]) -> None:
        """Обработать перемещение мыши для панорамирования.

        При активном панорамировании смещение курсора преобразуется в скролл
        сцены через полосы прокрутки.

        Args:
            event: Событие QMouseEvent.
        """
        if not event:
            raise ValueError("Event was empty")

        if self._is_panning and self._pan_start_pos is not None:
            # Вычислить смещение в пикселях.
            delta = event.pos() - self._pan_start_pos
            self._pan_start_pos = event.pos()

            # Применить панорамирование через полосы прокрутки.
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            if h_bar is not None and v_bar is not None:
                h_bar.setValue(h_bar.value() - delta.x())
                v_bar.setValue(v_bar.value() - delta.y())

            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self: "GraphViewer", event: Optional[QMouseEvent]) -> None:
        """Обработать отпускание кнопки мыши для завершения панорамирования.

        Args:
            event: Событие QMouseEvent.
        """
        if not event:
            raise ValueError("Event was empty")

        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = False
            self._pan_start_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def clear_graph(self: "GraphViewer") -> None:
        """Очистить отображаемый граф и вернуть фоновый паттерн.

        Удаляет SVG элемент и оставляет только фоновую сетку.
        """
        # Остановить поток рендеринга если он выполняется.
        if self._render_thread is not None and self._render_thread.isRunning():
            self._render_thread.quit()
            self._render_thread.wait()

        if self._svg_item is not None:
            self._scene.removeItem(self._svg_item)
            self._svg_item = None

        self._current_graph = None

    def fit_in_view(self: "GraphViewer") -> None:
        """Автоматически подогнать граф под размер окна.

        Масштабирует граф так, чтобы он полностью вмещался в видимую область
        с небольшим отступом.
        """
        if self._svg_item is None:
            return

        # Получить границы SVG элемента.
        bounds = self._svg_item.boundingRect()

        # Подогнать вид с сохранением соотношения сторон.
        self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)

        # Добавить небольший отступ.
        margin = 0.9
        self.scale(margin, margin)

    def reset_zoom(self: "GraphViewer") -> None:
        """Сбросить масштабирование и отобразить граф в нормальном размере."""
        self.resetTransform()
        self.fit_in_view()
