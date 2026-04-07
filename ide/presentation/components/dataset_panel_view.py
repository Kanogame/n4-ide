from ide.presentation.components.common.splitter import HorizontalSplitter
from typing import Optional, Self, Any
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QScrollArea,
    QLineEdit,
)
from PyQt6.QtCore import pyqtSignal

from ide.domain.datasets import DATASET_REGISTRY, get_dataset_by_name
from ide.domain.datasets import FieldType

from ide.presentation.common.styled_widget import StyledMixin
from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.panel_view import PanelView
from ide.presentation.components.dataset_panel.dataset_visualizer import (
    DatasetVisualizerWidget,
)
from ide.presentation.components.common.double_spinbox import DoubleSpinBox
from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.common.spinbox import SpinBox
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


class DatasetPanelView(QWidget, StyledMixin):
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
        """Инициализировать панель датасета"""
        super().__init__(parent)
        self._apply_style("dataset_panel_view.qss")

        # Основной layout панели
        layout = create_vertical_layout(self)

        # Создать панель
        self.main_content = PanelView("Выбор датасета")

        # Создать форму - селектор датасета
        self.create_dataset_selector()

        # Создать контейнер для динамических полей параметров
        self.create_parameters_container()

        # Создать кнопку генерации
        self.create_buttons()

        # Правая часть - визуализация датасета
        self.visualizer = DatasetVisualizerWidget()

        # Сплиттер для разделения конфигурации и визуализации
        splitter = HorizontalSplitter(self.left_widget, self.visualizer)
        self.main_content.add_widget(splitter)

        layout.addWidget(self.main_content)

        # Инициализировать поля параметров для первого датасета
        self._update_parameters_fields()

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

        # Левая панель сплиттера
        self.left_widget = QWidget()
        self.left_layout = create_vertical_layout(self.left_widget)

        # Скроллируемая область для параметров
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("DatasetScroll")

        # Виджет-контейнер для полей параметров
        self.params_container = QWidget()
        self.params_layout = create_vertical_layout(self.params_container, 12)
        self.params_container.setObjectName("DatasetParams")
        self.params_layout.setObjectName("DatasetParamsLayout")

        scroll.setWidget(self.params_container)
        self.left_layout.addWidget(scroll)

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
        self.left_layout.addLayout(buttons_layout)

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

        if field.field_type == FieldType.INTEGER:
            spinbox = SpinBox(field.min_value, field.max_value)
            spinbox.setValue(int(field.default_value))
            return spinbox

        elif field.field_type == FieldType.FLOAT:
            doublespinbox = DoubleSpinBox(field.min_value, field.max_value, 0.01)
            doublespinbox.setValue(float(field.default_value))
            return doublespinbox

        elif field.field_type == FieldType.CHOICE:
            combobox = ComboBox()
            if field.choices:
                combobox.addItems(field.choices)
            return combobox

        else:
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
