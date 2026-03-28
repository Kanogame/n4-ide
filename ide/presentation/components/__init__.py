"""
Presentation layer components for N4-IDE.

Exports all UI components following strict separation of concerns:
- Styled components: Button, ComboBox, TextBox, etc.
- NavBar: Icon-based sidebar
- Specialized views: ModelView, DatasetPanel, etc.
"""

from ide.presentation.components.button import Button, ButtonStyle
from ide.presentation.components.combobox import ComboBox
from ide.presentation.components.textbox import TextBox
from ide.presentation.components.spinbox import SpinBox
from ide.presentation.components.containers import FormField, Section, Divider
from ide.presentation.components.navbar import NavBar, NavItem, NavItemType
from ide.presentation.components.model_view import ModelView, ModelInfo
from ide.presentation.components.editor_widget import EditorWidget
from ide.presentation.components.graph_view import GraphView
from ide.presentation.components.console_widget import ConsoleWidget
from ide.presentation.components.dataset_panel import DatasetPanel
from ide.presentation.components.weights_table import WeightsTable
from ide.presentation.components.debug_panel import DebugPanel

__all__ = [
    # Styled components
    "Button",
    "ButtonStyle",
    "ComboBox",
    "TextBox",
    "SpinBox",
    "FormField",
    "Section",
    "Divider",
    # Navigation
    "NavBar",
    "NavItem",
    "NavItemType",
    # Views
    "ModelView",
    "ModelInfo",
    "EditorWidget",
    "GraphView",
    "ConsoleWidget",
    "DatasetPanel",
    "WeightsTable",
    "DebugPanel",
]
