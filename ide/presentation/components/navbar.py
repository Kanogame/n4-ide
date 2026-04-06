from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor

from ide.presentation.common.styled_widget import StyledComponent


class NavItemType(Enum):
    """Navigation item type for grouping."""

    TOOL = auto()
    SEPARATOR = auto()
    SPACER = auto()


@dataclass(frozen=True)
class NavItem:
    """Navigation bar item."""

    id: str
    icon_path: str
    tooltip: str = ""
    type: NavItemType = NavItemType.TOOL


class NavBarSeparator(QWidget):
    """Horizontal separator widget for navbar."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setObjectName("NavBarSeparator")


class NavBarButton(QPushButton, StyledComponent):
    """Navigation bar button with centered selection rectangle."""

    PADDING = 4
    BORDER_RADIUS = 6
    ICON_SIZE = 16

    def __init__(
        self,
        icon_path: str,
        tooltip: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._apply_style("navbar_button.qss")

        self.setObjectName("NavBarButton")
        self.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.setFixedSize(48, 40)
        self.setText("")
        self.setToolTip(tooltip)

        if icon_path:
            self.setIcon(QIcon(icon_path))

        self._is_selected = False

    def set_selected(self, selected: bool) -> None:
        """Set button selection state."""
        self._is_selected = selected
        self.update()

    def is_selected(self) -> bool:
        """Get button selection state."""
        return self._is_selected

    # TODO: remove
    def paintEvent(self, event) -> None:  # type: ignore
        """Paint button with custom selection rectangle."""
        super().paintEvent(event)

        if self._is_selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            rect = self.rect().adjusted(
                self.PADDING,
                self.PADDING,
                -self.PADDING,
                -self.PADDING,
            )

            painter.fillRect(
                rect,
                QColor(0, 95, 184, 10),
            )

            painter.setPen(QColor(0, 95, 184, 30))
            painter.drawRoundedRect(rect, self.BORDER_RADIUS, self.BORDER_RADIUS)
            painter.end()


class NavBar(StyledComponent):
    """Vertical navigation bar with icon buttons."""

    item_clicked = pyqtSignal(str)

    WIDTH = 48

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, "navbar.qss")

        self._selected_item_id: Optional[str] = None
        self._items: dict[str, NavBarButton] = {}
        self._nav_items: dict[str, NavItem] = {}

        self.setFixedWidth(self.WIDTH)
        self.setObjectName("NavBar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._bottom_layout = QVBoxLayout()
        self._bottom_layout.setContentsMargins(0, 0, 0, 0)
        self._bottom_layout.setSpacing(0)

        layout.addLayout(self._main_layout)
        layout.addStretch()
        layout.addLayout(self._bottom_layout)

        self._initialize_items()

    def _initialize_items(self) -> None:
        """Initialize all navbar items."""
        self.add_item(
            NavItem(
                id="code",
                icon_path="assets/icons/code.svg",
                tooltip="Code Editor",
            )
        )

        self.add_item(
            NavItem(
                id="dataset",
                icon_path="assets/icons/dataset.svg",
                tooltip="Dataset Management",
            )
        )

        self.add_item(
            NavItem(
                id="training",
                icon_path="assets/icons/training.svg",
                tooltip="Model Training",
            )
        )

        self.add_item(
            NavItem(
                id="model",
                icon_path="assets/icons/model.svg",
                tooltip="Model Inspector",
            )
        )

        self.add_item(
            NavItem(
                id="graph",
                icon_path="assets/icons/graph.svg",
                tooltip="Computation Graph",
            )
        )

        self.add_item(
            NavItem(
                id="sep1",
                icon_path="",
                type=NavItemType.SEPARATOR,
            )
        )

        self.add_bottom_item(
            NavItem(
                id="settings",
                icon_path="assets/icons/settings.svg",
                tooltip="Settings",
            )
        )

    def add_item(self, item: NavItem) -> None:
        """Add navigation item to main section."""
        if item.type == NavItemType.SEPARATOR:
            separator = NavBarSeparator()
            self._main_layout.addWidget(separator)
            return

        if item.type == NavItemType.SPACER:
            self._main_layout.addStretch()
            return

        button = self._create_nav_button(item)
        self._main_layout.addWidget(button)

    def add_bottom_item(self, item: NavItem) -> None:
        """Add navigation item to bottom section."""
        if item.type != NavItemType.TOOL:
            return

        button = self._create_nav_button(item)
        self._bottom_layout.insertWidget(0, button)

    def _create_nav_button(self, item: NavItem) -> NavBarButton:
        """Create and register a navigation button."""
        button = NavBarButton(
            icon_path=item.icon_path,
            tooltip=item.tooltip,
        )

        button.clicked.connect(lambda: self._on_item_clicked(item.id))

        self._items[item.id] = button
        self._nav_items[item.id] = item

        return button

    def _on_item_clicked(self, item_id: str) -> None:
        """Handle navigation item click."""
        self._set_selected_item(item_id)
        self.item_clicked.emit(item_id)

    def _set_selected_item(self, item_id: str) -> None:
        """Update visual state for selected item."""
        if self._selected_item_id and self._selected_item_id in self._items:
            self._items[self._selected_item_id].set_selected(False)

        if item_id in self._items:
            self._selected_item_id = item_id
            self._items[item_id].set_selected(True)

    def get_selected_item_id(self) -> Optional[str]:
        """Get ID of currently selected item."""
        return self._selected_item_id

    def set_selected_item_by_id(self, item_id: str) -> None:
        """Programmatically select an item by ID."""
        self._set_selected_item(item_id)
