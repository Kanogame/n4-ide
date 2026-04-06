from ide.presentation.components.common.navbar_widget import NavBar
from ide.domain.datasets.controller import DatasetGenerationWorker
from typing import Self
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
)

from ide.presentation.components.model_panel_view import ModelPanelView
from ide.presentation.components.dataset_panel_view import DatasetPanelView

from ide.presentation.common.styled_widget import StyledMainWindow


class MainWindow(StyledMainWindow):
    """
    Главное окно приложение, содержит navbar слева, а также главную панель

    Все компоненты коммуницируют через сигналы
    """

    def __init__(self) -> None:
        super().__init__(
            None,
        )

        self.setWindowTitle("N4 IDE")
        self.resize(1600, 900)

        self._build_ui()

    def _build_ui(self) -> None:
        """Собрать главный интерфейс"""

        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Navbar слева
        self.setup_nabar()

        # Панель справа
        self.setup_panel_view()

        # Создание всех разделов
        self.setup_tabs()

        # Установить главный виджет
        self.setCentralWidget(main_widget)

    def setup_nabar(self: Self) -> None:
        self.navbar = NavBar()

        # Подключаем сигнал в _on_navbar_item_clicked
        self.navbar.item_clicked.connect(self._on_navbar_item_clicked)

        # Устанавливаем редактор кода как начальный раздел
        self.navbar.set_selected_item_by_id("code")
        self.main_layout.addWidget(self.navbar)

    def setup_panel_view(self: Self) -> None:
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.main_layout.addLayout(self.content_layout)

    def setup_tabs(self: Self) -> None:
        """Создать все разделы приложения и подключить сигналы.

        Включает:
        - ModelPanelView для редактирования модели
        - DatasetPanelView для генерации датасетов
        - Подключение сигнала генерации датасета
        """

        # Используем QStackedWidget чтобы быстро и легко
        # менять разделы через setCurrentIndex
        self.stacked = QStackedWidget()

        self.model_view = ModelPanelView()
        self.stacked.addWidget(self.model_view)

        self.dataset = DatasetPanelView()
        self.stacked.addWidget(self.dataset)

        self.content_layout.addWidget(self.stacked)

        # Подключить сигнал генерации датасета
        self.dataset.generate_requested.connect(self._on_dataset_generate_requested)

        # Хранилище для текущего рабочего потока (только один может быть активен)
        self.generation_worker: DatasetGenerationWorker | None = None

    def _on_navbar_item_clicked(self, item_id: str) -> None:
        """Обработчик сигнала кнопки navbar.

        Переключает текущий раздел между доступными панелями.

        Args:
            item_id: Идентификатор выбранного пункта в навигации.
        """

        # Мапим названия панелей к их id в stacked виджете
        item_id_mapping = {
            "code": 0,
            "dataset": 1,
        }

        # Вызываем смену
        self.stacked.setCurrentIndex(item_id_mapping[item_id])

    def _on_dataset_generate_requested(
        self,
        config,
    ) -> None:
        """Обработчик сигнала генерации датасета.

        Запускает рабочий поток для генерации датасета в фоне
        и подключает сигналы для обновления UI.

        Args:
            config: DatasetConfig с именем датасета и параметрами.
        """
        # Остановить предыдущий рабочий поток если он работает
        if self.generation_worker is not None and self.generation_worker.isRunning():
            self.generation_worker.quit()
            self.generation_worker.wait()

        # Создать и запустить новый рабочий поток
        self.generation_worker = DatasetGenerationWorker(
            config.dataset_name,
            config.parameters,
        )

        # Подключить сигналы завершения
        self.generation_worker.finished.connect(self._on_dataset_generated)
        self.generation_worker.error.connect(self._on_dataset_generation_error)

        # Запустить поток
        self.generation_worker.start()

    def _on_dataset_generated(self, dataset_result) -> None:
        """Обработчик успешной генерации датасета.

        Отображает сгенерированный датасет в визуализаторе.

        Args:
            dataset_result: DatasetResult с массивами X и y.
        """
        self.dataset.visualizer.set_dataset(
            dataset_result.X,
            dataset_result.y,
            title=dataset_result.title,
        )

    def _on_dataset_generation_error(self, error_message: str) -> None:
        """Обработчик ошибки при генерации датасета.

        Выводит сообщение об ошибке в консоль.

        Args:
            error_message: Текст сообщения об ошибке.
        """
        print(f"Ошибка генерации датасета: {error_message}")
