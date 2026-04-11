from ide.presentation.components.metrics_panel_view import MetricsPanelView
from ide.presentation.components.common.navbar_widget import NavBar
from ide.domain.datasets.controller import DatasetGenerationWorker
from ide.domain.execution.controller import ExecutionController
from ide.domain.training.controller import TrainingController
from ide.application.app import Application
from typing import Self, Optional, Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
)

from ide.presentation.components.model_panel_view import ModelPanelView
from ide.presentation.components.dataset_panel_view import DatasetPanelView
from ide.presentation.components.trainer_panel_view import TrainerPanelView
from ide.presentation.components.trainer_panel.training_control import TrainingConfig

from ide.presentation.common.mixins import StyledMainWindow


class MainWindow(StyledMainWindow):
    """Главное окно приложение, содержит navbar слева, а также главную панель.

    Все компоненты коммуницируют через сигналы. Управляет
    выполнением кода модели, генерацией датасетов и обучением.
    """

    def __init__(self) -> None:
        super().__init__(None)

        self.setWindowTitle("N4 IDE")
        self.resize(1600, 900)

        # Инициализировать Application слой
        self.app = Application()

        # Инициализировать контроллеры
        self.execution_controller = ExecutionController(
            output_callback=self.app.append_output
        )
        self.training_controller = TrainingController()

        # Текущие ссылки на данные
        self.current_dataset_x: Optional[Any] = None
        self.current_dataset_y: Optional[Any] = None
        self.current_model_class: Optional[type] = None
        self.generation_worker: Optional[DatasetGenerationWorker] = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Собрать главный интерфейс."""

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
        """Настроить навигационную панель."""
        self.navbar = NavBar()

        # Подключаем сигнал в _on_navbar_item_clicked
        self.navbar.item_clicked.connect(self._on_navbar_item_clicked)

        # Устанавливаем редактор кода как начальный раздел
        self.navbar.set_selected_item_by_id("code")
        self.main_layout.addWidget(self.navbar)

    def setup_panel_view(self: Self) -> None:
        """Настроить основной layout для панелей."""
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.main_layout.addLayout(self.content_layout)

    def setup_tabs(self: Self) -> None:
        """Создать все разделы приложения и подключить сигналы.

        Включает:
        - ModelPanelView для редактирования модели
        - DatasetPanelView для генерации датасетов
        - TrainerPanelView для обучения модели
        - Подключение сигналов для взаимодействия компонентов
        """

        # Используем QStackedWidget чтобы быстро менять разделы
        self.stacked = QStackedWidget()

        self.model_view = ModelPanelView()
        self.stacked.addWidget(self.model_view)

        self.dataset = DatasetPanelView()
        self.stacked.addWidget(self.dataset)

        self.trainer = TrainerPanelView()
        self.stacked.addWidget(self.trainer)

        self.metrics = MetricsPanelView()
        self.stacked.addWidget(self.metrics)

        self.content_layout.addWidget(self.stacked)

        # Подключить сигналы модели
        self.model_view.train_requested.connect(self._on_model_code_run)
        self.model_view.backend_changed.connect(
            lambda backend: self.app.set_backend(backend)
        )

        # Подключить сигнал генерации датасета
        self.dataset.generate_requested.connect(self._on_dataset_generate_requested)

        # Подключить сигналы обучения
        self.trainer.training_started.connect(self._on_training_started)
        self.trainer.training_stopped.connect(self._on_training_stopped)

        # Подключить сигналы приложения к UI
        self.app.output_received.connect(self.trainer.append_log)

    def _on_navbar_item_clicked(self, item_id: str) -> None:
        """Обработчик сигнала кнопки navbar.

        Переключает текущий раздел между доступными панелями.

        Args:
            item_id: Идентификатор выбранного пункта в навигации.
        """

        # Маппинг названия панелей к их индексам в stacked виджете
        item_id_mapping = {
            "code": 0,
            "dataset": 1,
            "trainer": 2,
            "metrics": 3,
        }

        # Вызываем смену раздела
        self.stacked.setCurrentIndex(item_id_mapping[item_id])

    def _on_model_code_run(self) -> None:
        """Обработчик сигнала запуска кода модели.

        Выполняет код из редактора модели, извлекает класс модели
        и обновляет состояние приложения.
        """
        try:
            # Получить код модели из редактора
            model_code = self.model_view.get_model_code()
            backend_name = self.model_view.get_selected_backend()

            # Выполнить код с backend
            namespace = self.execution_controller.run(model_code, backend_name)

            # Извлечь класс модели
            model_class = self.execution_controller.extract_and_validate_model(
                namespace
            )

            # Сохранить класс модели
            self.current_model_class = model_class

            # Обновить состояние приложения
            self.app.set_backend(backend_name)

            # Вывести успешное сообщение
            self.app.append_output(f"✓ Модель {model_class.__name__} загружена успешно")

        except Exception as e:
            self.app.append_output(f"✗ Ошибка при загрузке модели: {e}")
            self.app.error_occurred.emit(str(e))

    def _on_dataset_generate_requested(self, config) -> None:
        """Обработчик сигнала генерации датасета.

        Запускает рабочий поток для генерации датасета в фоне
        и подключает сигналы для обновления UI и состояния.

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

        Отображает сгенерированный датасет в визуализаторе
        и сохраняет данные для последующего обучения.

        Args:
            dataset_result: DatasetResult с массивами X и y.
        """
        # Отобразить датасет в визуализаторе
        self.dataset.visualizer.set_dataset(
            dataset_result.X,
            dataset_result.y,
            title=dataset_result.title,
        )

        # Сохранить данные в состояние приложения
        self.current_dataset_x = dataset_result.X
        self.current_dataset_y = dataset_result.y

        # Обновить состояние приложения
        self.app.set_dataset(
            name=dataset_result.title or "Dataset",
            x=dataset_result.X,
            y=dataset_result.y,
            title=dataset_result.title or "Generated Dataset",
        )

        # Логировать успех
        self.app.append_output(
            f"✓ Датасет '{dataset_result.title}' сгенерирован успешно"
        )

    def _on_dataset_generation_error(self, error_message: str) -> None:
        """Обработчик ошибки при генерации датасета.

        Выводит сообщение об ошибке в логи приложения.

        Args:
            error_message: Текст сообщения об ошибке.
        """
        self.app.append_output(f"✗ Ошибка генерации датасета: {error_message}")
        self.app.error_occurred.emit(error_message)

    def _on_training_started(self: Self, config: TrainingConfig) -> None:
        """Обработчик сигнала начала обучения.

        Проверяет наличие модели и датасета, затем запускает
        процесс обучения в отдельном потоке.

        Args:
            config: TrainingConfig с параметрами обучения.
        """
        # Проверить наличие модели
        if self.current_model_class is None:
            self.app.append_output(
                "Ошибка: сначала нужно загрузить модель (раздел 'Модель')"
            )
            self.trainer.set_training_enabled(True)
            return

        # Проверить наличие датасета
        if self.current_dataset_x is None or self.current_dataset_y is None:
            self.app.append_output(
                "Ошибка: сначала нужно сгенерировать датасет (раздел 'Датасет')"
            )
            self.trainer.set_training_enabled(True)
            return

        # Логировать начало обучения
        self.app.append_output("Обучение начато...")
        self.trainer.clear_logs()
        self.trainer.append_log("=" * 50)
        self.trainer.append_log(f"Модель: {self.current_model_class.__name__}")
        self.trainer.append_log("Параметры обучения:")
        self.trainer.append_log(f"  Эпохи: {config.epochs}")
        self.trainer.append_log(f"  Батч: {config.batch_size}")
        self.trainer.append_log(f"  Скорость обучения: {config.learning_rate}")
        self.trainer.append_log("=" * 50)

        # Запустить обучение
        self.training_controller.start_training(
            model_class=self.current_model_class,
            dataset_x=self.current_dataset_x,
            dataset_y=self.current_dataset_y,
            config=config,
            on_progress=self.trainer.append_log,
            on_finished=self._on_training_finished,
            on_error=self._on_training_error,
        )

        # Отключить кнопку старта
        self.trainer.set_training_enabled(False)

    def _on_training_finished(self, result) -> None:
        """Обработчик завершения обучения.

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

            # Получить хранилище сборщиков метрик и передать в панель метрик
            collector_repository = self.training_controller.get_collector_repository()
            if collector_repository is not None:
                self.metrics.set_metrics_storage(collector_repository)
        else:
            self.app.append_output(f"✗ Ошибка обучения: {result.error_message}")
            self.app.error_occurred.emit(result.error_message or "Unknown error")

        # Включить кнопку старта
        self.trainer.set_training_enabled(True)

    def _on_training_stopped(self) -> None:
        """Обработчик сигнала остановки обучения."""
        self.training_controller.stop_current()
        self.trainer.append_log("Обучение остановлено пользователем")
        self.trainer.set_training_enabled(True)

    def _on_training_error(self, error_message: str) -> None:
        """Обработчик ошибки во время обучения.

        Args:
            error_message: Сообщение об ошибке.
        """
        self.app.append_output(f"✗ Ошибка: {error_message}")
        self.trainer.set_training_enabled(True)
