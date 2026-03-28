"""Container and layout components for N4-IDE."""

from typing import Union, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)
from PyQt6.QtGui import QFont


class FormField(QWidget):
    """Labeled form field combining label and input.

    Composition pattern: label + input widget side-by-side.
    Useful for consistent form layouts.
    """

    def __init__(
        self,
        label_text: str,
        widget: QWidget,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.widget = widget

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        label = QLabel(label_text)
        font = QFont("Open Sans", 16)
        font.setWeight(QFont.Weight.Normal)
        label.setFont(font)
        label.setStyleSheet("color: black;")

        layout.addWidget(label)
        layout.addWidget(widget)
        layout.addStretch()

    def get_widget(self) -> QWidget:
        """Get the input widget."""
        return self.widget


class Section(QFrame):
    """Styled section/panel for grouping content.

    Features:
    - Subtle background and border
    - Consistent padding
    - Optional title
    """

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            Section {
                background-color: rgba(255, 255, 255, 0.70);
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 7px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        if title:
            title_label = QLabel(title)
            font = QFont("Open Sans", 28)
            font.setWeight(QFont.Weight.Bold)
            title_label.setFont(font)
            title_label.setStyleSheet("color: rgba(0, 0, 0, 0.90);")
            layout.addWidget(title_label)

        self.content_layout = layout

    def add_widget(self, widget: QWidget) -> None:
        """Add widget to section content."""
        self.content_layout.insertWidget(self.content_layout.count() - 1, widget)

    def add_layout(self, layout: Union[QVBoxLayout, QHBoxLayout]) -> None:
        """Add layout to section content."""
        self.content_layout.insertLayout(self.content_layout.count() - 1, layout)


class Divider(QFrame):
    """Horizontal divider line."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setStyleSheet("""
            Divider {
                border: none;
                background-color: rgba(0, 0, 0, 0.06);
                height: 1px;
            }
        """)
        self.setMaximumHeight(1)
