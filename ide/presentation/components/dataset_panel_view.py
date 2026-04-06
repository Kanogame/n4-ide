from ide.presentation.components.common.panel_view import PanelView
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal

from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.spinbox import SpinBox
from ide.presentation.components.containers import FormField


class DatasetPanelView(QWidget):
    """Panel for managing synthetic dataset creation and parameters.

    Features:
    - Dataset preset selector
    - Sample count configuration
    - Test/train split ratio
    - Generate button
    - Styled with consistent design system
    """

    # Сигнал при нажатии на кнопку генерации датасета
    generate_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать панель датасета

        Args:
            parent: Родительский виджет.
        """

        super().__init__(parent)

        # Основной layout панели
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создать панель
        self.main_content = PanelView("Выбор датасета")

        # Preset selector
        self.preset_combo = ComboBox()
        self.preset_combo.addItems(
            [
                "Linear 1D",
                "Linear 2D",
                "XOR",
                "Gaussian Blobs",
                "Spiral",
                "Two Moons",
            ]
        )

        preset_field = FormField("Dataset Preset", self.preset_combo)
        self.main_content.add_widget(preset_field)

        # Sample count
        self.samples_spinbox = SpinBox()
        self.samples_spinbox.setMinimum(10)
        self.samples_spinbox.setMaximum(10000)
        self.samples_spinbox.setValue(100)
        self.samples_spinbox.setSuffix(" samples")

        samples_field = FormField("Sample Count", self.samples_spinbox)
        self.main_content.add_widget(samples_field)

        # Test split
        self.test_split_spinbox = SpinBox()
        self.test_split_spinbox.setMinimum(5)
        self.test_split_spinbox.setMaximum(95)
        self.test_split_spinbox.setValue(20)
        self.test_split_spinbox.setSuffix("%")

        test_split_field = FormField("Test/Train Split", self.test_split_spinbox)
        self.main_content.add_widget(test_split_field)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        self.generate_button = Button("Generate Dataset", ButtonStyle.ACCENT)
        self.generate_button.clicked.connect(self.generate_requested.emit)

        buttons_layout.addWidget(self.generate_button)
        self.main_content.add_layout(buttons_layout)

        layout.addWidget(self.main_content)
        layout.addStretch()
