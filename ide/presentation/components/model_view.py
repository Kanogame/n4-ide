"""
Model view panel for N4-IDE - displays and manages neural network model.

Recreates model.html with styled components following N4-IDE design system.
Uses Button, ComboBox, TextBox, and containers for clean, maintainable UI.
"""

from typing import Optional
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from ide.presentation.components.button import Button, ButtonStyle
from ide.presentation.components.combobox import ComboBox
from ide.presentation.components.containers import FormField, Section


@dataclass(frozen=True)
class ModelInfo:
    """Immutable model information snapshot."""

    backend: str = "PyFloat"
    layer_count: int = 0
    total_parameters: int = 0
    code: str = ""


class ModelView(QWidget):
    """Model view panel with code editor and model metadata.

    Features:
    - Backend selector dropdown
    - Model code display
    - Train button
    - Responsive layout with splitter
    - Signal-based architecture
    """

    train_requested = pyqtSignal()  # User clicked Train button
    backend_changed = pyqtSignal(str)  # Backend dropdown changed

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._current_model_info = ModelInfo()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main section
        main_section = Section("Описание модели")

        # Backend selector
        self.backend_combo = ComboBox()
        self.backend_combo.addItems(["PyFloat", "NumPy", "PyTorch"])
        self.backend_combo.value_changed.connect(self.backend_changed.emit)

        backend_field = FormField("Вычислительный бекенд", self.backend_combo)
        main_section.add_widget(backend_field)

        # Code display with line numbers
        self.code_editor = QTextEdit()
        self.code_editor.setReadOnly(True)
        font = QFont("Roboto Mono", 11)
        self.code_editor.setFont(font)
        self.code_editor.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 0.70);
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 7px;
                color: #439C37;
                padding: 8px;
                margin-bottom: 10px;
            }
        """)

        main_section.add_widget(self.code_editor)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        self.train_button = Button("Обучить", ButtonStyle.ACCENT)
        self.train_button.clicked.connect(self.train_requested.emit)

        buttons_layout.addWidget(self.train_button)
        main_section.add_layout(buttons_layout)

        layout.addWidget(main_section)

    def set_model_info(self, info: ModelInfo) -> None:
        """Update model view with new information.

        Args:
            info: ModelInfo dataclass with model metadata
        """
        self._current_model_info = info

        # Update backend selector
        if info.backend in ["PyFloat", "NumPy", "PyTorch"]:
            index = self.backend_combo.findText(info.backend)
            if index >= 0:
                self.backend_combo.blockSignals(True)
                self.backend_combo.setCurrentIndex(index)
                self.backend_combo.blockSignals(False)

        # Update code display
        self.code_editor.setText(info.code)

    def get_selected_backend(self) -> str:
        """Get currently selected backend.

        Returns:
            Backend name
        """
        return self.backend_combo.currentText()

    def get_current_model_info(self) -> ModelInfo:
        """Get current model information.

        Returns:
            ModelInfo dataclass
        """
        return self._current_model_info
