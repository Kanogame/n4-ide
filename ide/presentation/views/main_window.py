"""Главное окно приложения N4 IDE.

Содержит навигационную панель слева и основную область контента.
Все компоненты коммуницируют через сигналы приложения.

В этом файле находится ТОЛЬКО:
- Построение UI (layouts, widgets)
- Подключение сигналов между компонентами и приложением
- Очень минимальная логика для управления видимостью панелей

Вся бизнес-логика находится в application слое.
"""

from ide.domain.training.models import TrainingResult

from ide.presentation.components.metrics_panel_view import MetricsPanelView
from ide.presentation.components.visualization_panel_view import VisualizationPanelView
from ide.presentation.components.common.navbar_widget import NavBar
from ide.application.app import Application
from typing import Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
)

from ide.presentation.components.model_panel_view import ModelPanelView
from ide.presentation.components.dataset_panel_view import DatasetPanelView
from ide.presentation.components.trainer_panel_view import TrainerPanelView

from ide.presentation.common.mixins import StyledMainWindow


class MainWindow(StyledMainWindow):
    """Главное окно приложения.

    Содержит навигационную панель слева, а также главную панель с разделами.
    Все компоненты коммуницируют через сигналы. Управляет только layout
    и подключением сигналов.

    Attributes:
        app: Центральное приложение (Application).
        navbar: Навигационная панель.
        stacked: QStackedWidget для переключения разделов.
    """

    def __init__(self) -> None:
        """Инициализировать главное окно приложения."""
        super().__init__(None)

        self.setWindowTitle("N4 IDE")
        self.resize(1600, 900)

        # Инициализировать Application слой
        self.app = Application()

        self._build_ui()

    def _build_ui(self) -> None:
        """Собрать главный интерфейс."""
        main_widget = QWidget()
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Создать navbar слева
        self._setup_navbar()

        # Создать основной layout справа
        self._setup_panel_view()

        # Создать все разделы приложения
        self._setup_tabs()

        # Установить главный виджет
        self.setCentralWidget(main_widget)

    def _setup_navbar(self) -> None:
        """Настроить навигационную панель.

        Создает и подключает navbar для переключения между разделами.
        """
        self.navbar = NavBar()
        self.navbar.item_clicked.connect(self._on_navbar_item_clicked)

        # Устанавливаем редактор кода как начальный раздел
        self.navbar.set_selected_item_by_id("code")
        self.main_layout.addWidget(self.navbar)

    def _setup_panel_view(self) -> None:
        """Настроить основной layout для панелей."""
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.main_layout.addLayout(self.content_layout)

    def _setup_tabs(self) -> None:
        """Создать все разделы приложения и подключить сигналы.

        Включает:
        - ModelPanelView для редактирования модели
        - DatasetPanelView для генерации датасетов
        - VisualizationPanelView для визуализации архитектуры и вычислений
        - TrainerPanelView для обучения модели
        - MetricsPanelView для отображения метрик
        """
        # Используем QStackedWidget чтобы быстро менять разделы
        self.stacked = QStackedWidget()

        self.model_view = ModelPanelView()
        self.stacked.addWidget(self.model_view)

        self.dataset = DatasetPanelView()
        self.stacked.addWidget(self.dataset)

        self.visualization = VisualizationPanelView()
        self.stacked.addWidget(self.visualization)

        self.trainer = TrainerPanelView()
        self.stacked.addWidget(self.trainer)

        self.metrics = MetricsPanelView()
        self.stacked.addWidget(self.metrics)

        self.content_layout.addWidget(self.stacked)

        # Подключить сигналы модели
        self.model_view.train_requested.connect(
            lambda: self.app.model_manager.load_model_from_code(
                self.model_view.get_model_code()
            )
        )
        self.model_view.backend_changed.connect(self.app.model_manager.set_backend)

        # Подключить сигнал генерации датасета
        self.dataset.generate_requested.connect(self._on_dataset_generate_requested)

        # Подключить сигналы визуализации к приложению
        self.app.model_ready.connect(self.visualization.set_model)
        self.app.computational_graph_ready.connect(
            self.visualization.set_computational_graph
        )

        # Подключить сигналы обучения
        self.trainer.training_started.connect(self._on_training_started)
        self.trainer.training_stopped.connect(self._on_training_stopped)

        # Подключить сигналы приложения к логам обучения
        self.app.output_received.connect(self.trainer.append_log)

    def _on_navbar_item_clicked(self, item_id: str) -> None:
        """Обработчик сигнала нажатия кнопки navbar.

        Переключает текущий раздел между доступными панелями.

        Args:
            item_id: Идентификатор выбранного пункта в навигации.
        """
        # Маппинг названия панелей к их индексам в stacked виджете
        item_id_mapping = {
            "code": 0,
            "dataset": 1,
            "visualization": 2,
            "trainer": 3,
            "metrics": 4,
        }

        # Переключить раздел
        self.stacked.setCurrentIndex(item_id_mapping[item_id])

    def _on_dataset_generate_requested(self, config: Any) -> None:
        """Обработчик сигнала генерации датасета.

        Запускает рабочий поток для генерации датасета в фоне
        и подключает сигналы для обновления UI и состояния приложения.

        Args:
            config: DatasetConfig с именем датасета и параметрами.
        """
        # Запустить рабочий поток генерации датасета через менеджер
        worker = self.app.dataset_manager.start_generation_worker(
            config.dataset_name,
            config.parameters,
        )

        # Подключить сигналы завершения
        worker.finished.connect(self._on_dataset_generated)
        worker.error.connect(self.app.dataset_manager.on_dataset_generation_error)

    def _on_dataset_generated(self, dataset_result: Any) -> None:
        """Обработчик успешной генерации датасета.

        Отображает сгенерированный датасет в визуализаторе
        и сохраняет данные в приложение.

        Args:
            dataset_result: DatasetResult с массивами X и y.
        """
        # Отобразить датасет в визуализаторе
        self.dataset.visualizer.set_dataset(
            dataset_result.X,
            dataset_result.y,
            title=dataset_result.title,
        )

        # Сохранить в состояние приложения через менеджер датасета
        self.app.dataset_manager.on_dataset_generated(dataset_result)

        # Логировать успех
        self.app.append_output(
            f"✓ Датасет '{dataset_result.title}' сгенерирован успешно"
        )

    def _on_training_started(self, config: Any) -> None:
        """Обработчик сигнала начала обучения.

        Запускает процесс обучения с валидацией предусловий.

        Args:
            config: TrainingConfig с параметрами обучения.
        """
        # Получить модель и датасет из менеджеров
        model_class = self.app.model_manager.get_current_model()
        dataset_state = self.app.dataset_manager.get_dataset_state()

        if not model_class:
            raise ValueError("Model is not defined")

        # Извлечь данные датасета
        dataset_x = None
        dataset_y = None
        if dataset_state is not None:
            dataset_x = dataset_state.X
            dataset_y = dataset_state.y

        # Очистить логи обучения
        self.trainer.clear_logs()

        # Запустить обучение через менеджер обучения
        success = self.app.training_manager.start_training(
            model_class=model_class,
            dataset_x=dataset_x,
            dataset_y=dataset_y,
            config=config,
            on_progress=self.trainer.append_log,
            on_finished=self._on_training_finished,
            on_error=self._on_training_error,
        )

        # Если ошибка валидации, включить кнопку старта
        if not success:
            self.trainer.set_training_enabled(True)
        else:
            # Отключить кнопку старта во время обучения
            self.trainer.set_training_enabled(False)

    def _on_training_finished(self, result: TrainingResult) -> None:
        """Обработчик завершения обучения.

        Отображает результаты обучения и обновляет UI.

        Args:
            result: TrainingResult с результатами обучения.
        """
        if result.success:
            self.app.append_output(
                f"✓ Обучение завершено за {result.duration_seconds:.2f} сек"
            )
            if result.final_metrics:
                for key, value in result.final_metrics.items():
                    self.app.append_output(f"  {key}: {value:.6f}")

            collector_repository = (
                self.app.training_controller.get_collector_repository()
            )
            if collector_repository is not None:
                self.metrics.set_metrics_storage(collector_repository)

            if result.comp_graph is not None:
                self.app.set_comp_graph(result.comp_graph)

            if result.final_model is not None:
                self.app.set_final_model(result.final_model)
        else:
            self.app.append_output(f"✗ Ошибка обучения: {result.error_message}")
            self.app.error_occurred.emit(result.error_message or "Unknown error")

        # Отметить обучение как завершенное
        self.app.training_manager.mark_training_finished()

        # Включить кнопку старта
        self.trainer.set_training_enabled(True)

    def _on_training_stopped(self) -> None:
        """Обработчик сигнала остановки обучения."""
        self.app.training_manager.stop_training()
        self.trainer.append_log("Обучение остановлено пользователем")
        self.trainer.set_training_enabled(True)

    def _on_training_error(self, error_message: str) -> None:
        """Обработчик ошибки во время обучения.

        Args:
            error_message: Сообщение об ошибке.
        """
        self.app.append_output(f"✗ Ошибка: {error_message}")
        self.app.training_manager.mark_training_finished()
        self.trainer.set_training_enabled(True)
