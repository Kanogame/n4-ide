"""Панель управления генерацией датасета.

Компонент позволяет выбрать тип датасета, настроить его параметры
и просмотреть сгенерированные данные с помощью matplotlib.
"""

from ide.presentation.components.common.panel_view import PanelView, PanelToolbar
from ide.presentation.components.dataset_visualizer import DatasetVisualizerWidget
from ide.domain.datasets import DATASET_REGISTRY, get_dataset_by_name
from typing import Optional, Self, Any
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QSplitter,
)
from PyQt6.QtCore import pyqtSignal, Qt

from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.spinbox import SpinBox
from ide.presentation.components.containers import FormField


@dataclass(frozen=True)
class DatasetConfig:
    """Неизменяемая конфигурация датасета.

    Attributes:
        dataset_name: Имя выбранного датасета (например, "xor").
        parameters: Словарь параметров конфигурации датасета.
    """

    dataset_name: str
    parameters: dict[str, Any]


class DatasetPanelView(QWidget):
    """Панель для управления синтетическими датасетами.

    Компонент включает:
    - Выбор типа датасета из реестра
    - Динамическое отображение параметров в зависимости от выбранного датасета
    - Визуализацию сгенерированных данных через matplotlib
    - Кнопку для генерации датасета

    Signals:
        generate_requested: Сигнал при нажатии на кнопку генерации датасета.
    """

    # Сигнал при нажатии на кнопку генерации датасета.
    generate_requested = pyqtSignal(DatasetConfig)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать панель датасета.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)

        # Основной layout панели
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Сплиттер для разделения конфигурации и визуализации
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая часть - конфигурация датасета
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Создать панель с тулбаром
        toolbar = self.create_toolbar()
        self.main_content = PanelView("Выбор датасета", toolbar)

        # Создать селектор датасета
        self.create_dataset_selector()

        # Создать контейнер для динамических полей параметров
        self.create_parameters_container()

        # Создать кнопку генерации
        self.create_buttons()

        left_layout.addWidget(self.main_content)
        splitter.addWidget(left_widget)

        # Правая часть - визуализация датасета
        self.visualizer = DatasetVisualizerWidget()
        splitter.addWidget(self.visualizer)

        # Установить соотношение размеров (40/60)
        splitter.setStretchFactor(0, 40)
        splitter.setStretchFactor(1, 60)

        layout.addWidget(splitter)

        # Инициализировать поля параметров для первого датасета
        self._update_parameters_fields()

    def create_toolbar(self: Self) -> PanelToolbar:
        """Создать тулбар панели.

        Returns:
            Экземпляр PanelToolbar.
        """
        return PanelToolbar()

    def create_dataset_selector(self: Self) -> None:
        """Создать выпадающий список выбора датасета.

        Динамически заполняется из реестра датасетов.
        При изменении выбора обновляет отображаемые параметры.
        """
        self.dataset_combo = ComboBox()
        self.dataset_combo.addItems(list(DATASET_REGISTRY.keys()))
        self.dataset_combo.value_changed.connect(self._on_dataset_changed)

        dataset_field = FormField("Тип датасета", self.dataset_combo)
        self.main_content.add_widget(dataset_field)

    def create_parameters_container(self: Self) -> None:
        """Создать контейнер для динамических полей параметров.

        Контейнер содержит поля параметров, которые меняются
        в зависимости от выбранного датасета.
        """
        # Скроллируемая область для параметров
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        # Виджет-контейнер для полей параметров
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(12)

        scroll.setWidget(self.params_container)
        self.main_content.add_widget(scroll)

        # Словарь для хранения ссылок на widgets параметров
        self.parameter_widgets: dict[str, QWidget] = {}

    def create_buttons(self: Self) -> None:
        """Создать кнопки управления панели.

        Включает кнопку "Сгенерировать датасет" для запуска генерации.
        """
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        self.generate_button = Button("Сгенерировать", ButtonStyle.ACCENT)
        self.generate_button.clicked.connect(self._on_generate_clicked)

        buttons_layout.addWidget(self.generate_button)
        self.main_content.add_layout(buttons_layout)

    def _on_dataset_changed(self, dataset_name: str) -> None:
        """Обработчик изменения выбранного датасета.

        Обновляет отображаемые параметры согласно новому датасету.

        Args:
            dataset_name: Имя выбранного датасета.
        """
        self._update_parameters_fields()

    def _update_parameters_fields(self: Self) -> None:
        """Обновить поля параметров для текущего датасета.

        Получает список параметров из датасета и создаёт
        соответствующие виджеты в интерфейсе.
        """
        # Очистить старые параметры
        while self.params_layout.count() > 0:
            item = self.params_layout.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

        self.parameter_widgets.clear()

        # Получить текущий датасет и его параметры
        dataset_name = self.dataset_combo.currentText()

        try:
            dataset = get_dataset_by_name(dataset_name)
            fields = dataset.get_fields()

            # Создать виджеты для каждого параметра
            for field in fields:
                widget = self._create_parameter_widget(field)
                field_container = FormField(field.label, widget)
                self.params_layout.addWidget(field_container)
                self.parameter_widgets[field.name] = widget

        except ValueError:
            # Датасет не найден в реестре, пропустить
            pass

        # Добавить растяжение в конец
        self.params_layout.addStretch()

    def _create_parameter_widget(self: Self, field: Any) -> QWidget:
        """Создать виджет для параметра датасета.

        Args:
            field: DatasetField с описанием параметра.

        Returns:
            QWidget для редактирования значения параметра.
        """
        from ide.domain.datasets import FieldType
        from ide.presentation.components.double_spinbox import DoubleSpinBox

        if field.field_type == FieldType.INTEGER:
            spinbox = SpinBox()
            spinbox.setMinimum(int(field.min_value or 0))
            spinbox.setMaximum(int(field.max_value or 100))
            spinbox.setValue(int(field.default_value))
            return spinbox

        elif field.field_type == FieldType.FLOAT:
            doublespinbox = DoubleSpinBox()
            doublespinbox.setMinimum(float(field.min_value or 0.0))
            doublespinbox.setMaximum(float(field.max_value or 1.0))
            doublespinbox.setValue(float(field.default_value))
            doublespinbox.setSingleStep(0.01)
            return doublespinbox

        elif field.field_type == FieldType.CHOICE:
            combobox = ComboBox()
            if field.choices:
                combobox.addItems(field.choices)
            return combobox

        else:  # FieldType.TEXT
            from PyQt6.QtWidgets import QLineEdit

            lineedit = QLineEdit()
            lineedit.setText(str(field.default_value))
            return lineedit

    def _on_generate_clicked(self: Self) -> None:
        """Обработчик нажатия кнопки генерации датасета.

        Собирает текущие значения параметров и эмитирует сигнал generate_requested.
        """
        dataset_name = self.dataset_combo.currentText()

        # Собрать значения параметров из виджетов
        parameters: dict[str, Any] = {}

        try:
            dataset = get_dataset_by_name(dataset_name)
            fields = dataset.get_fields()

            for field in fields:
                widget = self.parameter_widgets.get(field.name)
                if widget:
                    # Получить значение из виджета в зависимости от типа
                    from ide.domain.datasets import FieldType

                    if field.field_type == FieldType.INTEGER:
                        # SpinBox имеет value()
                        value: Any = int(widget.value())  # type: ignore
                    elif field.field_type == FieldType.FLOAT:
                        # DoubleSpinBox имеет value()
                        value = float(widget.value())  # type: ignore
                    elif field.field_type == FieldType.CHOICE:
                        # ComboBox имеет currentText()
                        value = str(widget.currentText())  # type: ignore
                    else:  # TEXT
                        # QLineEdit имеет text()
                        value = str(widget.text())  # type: ignore

                    parameters[field.name] = value

        except ValueError:
            pass

        config = DatasetConfig(dataset_name=dataset_name, parameters=parameters)
        self.generate_requested.emit(config)

    def get_current_dataset_name(self) -> str:
        """Получить имя текущего выбранного датасета.

        Returns:
            Имя датасета.
        """
        return self.dataset_combo.currentText()
