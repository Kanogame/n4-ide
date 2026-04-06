from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLayout
from typing import Self, Optional
from ide.presentation.common.styled_widget import StyledComponent


class PanelContent(StyledComponent):
    def __init__(self: Self, parent: Optional[QWidget] = None):
        super().__init__(parent, "panel.qss")

        self.setObjectName("PanelContent")

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(12)

    def add_widget(self: Self, widget: QWidget):
        self._main_layout.addWidget(widget)

    def add_layout(self: Self, layout: QLayout):
        self._main_layout.addLayout(layout)


class PanelToolbar(StyledComponent):
    def __init__(self: Self, parent: Optional[QWidget] = None):
        super().__init__(parent, "panel.qss")

        self.setObjectName("PanelToolbar")


class PanelView(StyledComponent):
    def __init__(
        self: Self,
        title: str,
        toolbar: Optional[PanelToolbar] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent, "panel.qss")

        self.setObjectName("PanelView")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title_label = QLabel(title)

        layout.addWidget(title_label)

        if toolbar:
            self.toolbar = toolbar
            layout.addWidget(toolbar)

        self.content = PanelContent()

        layout.addWidget(self.content)

    def add_widget(self: Self, widget: QWidget):
        self.content.add_widget(widget)

    def add_layout(self: Self, layout: QLayout):
        self.content.add_layout(layout)
