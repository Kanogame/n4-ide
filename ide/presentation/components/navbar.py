"""
Icon-based navbar for N4-IDE matching model.html design.

Provides vertical navigation with icons only (no text labels).
Icons must exist at configured paths in assets/icons/.
"""

from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtGui import QIcon


class NavItemType(Enum):
    """Navigation item type for grouping."""

    TOOL = auto()  # Regular tool button
    SEPARATOR = auto()  # Visual separator
    SPACER = auto()  # Flexible space


@dataclass(frozen=True)
class NavItem:
    """Navigation menu item definition."""

    id: str
    icon_path: str
    label: str = ""
    tooltip: str = ""
    type: NavItemType = NavItemType.TOOL


class NavBar(QWidget):
    """Icon-only navigation sidebar matching model.html design.

    Features:
    - Fixed width (48px)
    - Icon-only buttons (no text labels)
    - Selected item shows left blue border
    - Signal emission for navigation events

    Icon Requirements:
    - All icons must be SVG files in assets/icons/
    - Icon paths are validated at button creation
    - If icon not found, button displays without icon
    """

    # Signal emitted when navigation item clicked
    item_clicked = pyqtSignal(str)  # Emits item id

    # Styling constants matching model.html
    WIDTH = 48
    ITEM_HEIGHT = 40

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._selected_item_id: Optional[str] = None
        self._items: dict[str, QPushButton] = {}
        self._nav_items: dict[str, NavItem] = {}

        self.setFixedWidth(self.WIDTH)
        self.setStyleSheet("""
            NavBar {
                background-color: #F3F3F3;
            }
        """)

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

    def add_item(self, item: NavItem) -> None:
        """Add navigation item to navbar.

        Args:
            item: NavItem defining the menu item
        """
        if item.type == NavItemType.SEPARATOR:
            separator = QWidget()
            separator.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 0.06);
                    height: 1px;
                }
            """)
            separator.setFixedHeight(1)
            self._main_layout.addWidget(separator)
            return

        if item.type == NavItemType.SPACER:
            self._main_layout.addStretch()
            return

        button = self._create_nav_button(item)
        self._items[item.id] = button
        self._nav_items[item.id] = item  # Store nav item
        self._main_layout.addWidget(button)

    def add_bottom_item(self, item: NavItem) -> None:
        """Add item to bottom section of navbar (e.g., settings).

        Args:
            item: NavItem defining the menu item
        """
        if item.type != NavItemType.TOOL:
            return

        button = self._create_nav_button(item)
        self._items[item.id] = button
        self._nav_items[item.id] = item  # Store nav item
        self._bottom_layout.insertWidget(0, button)

    def _create_nav_button(self, item: NavItem) -> QPushButton:
        """Create styled navigation button.

        Args:
            item: NavItem to create button for

        Returns:
            Configured QPushButton
        """
        button = QPushButton()
        button.setObjectName(item.id)
        button.setIconSize(QSize(16, 16))
        button.setFixedSize(self.WIDTH, self.ITEM_HEIGHT)

        # Load and set icon if path exists
        if item.icon_path:
            try:
                icon = QIcon(item.icon_path)
                button.setIcon(icon)
            except Exception:
                pass

        # Icons only - no text
        button.setText("")
        button.setToolTip(item.tooltip or item.label)

        button.clicked.connect(lambda: self._on_item_clicked(item.id))

        # Default unselected state
        self._apply_unselected_style(button)

        return button

    def _apply_unselected_style(self, button: QPushButton) -> None:
        """Apply unselected button style matching model.html."""
        stylesheet = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-left: 3px solid transparent;
                padding: 8px 5px;
                icon-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.04);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.08);
            }
        """
        button.setStyleSheet(stylesheet)

    def _apply_selected_style(self, button: QPushButton) -> None:
        """Apply selected button style matching model.html exactly."""
        stylesheet = """
            QPushButton {
                background-color: rgba(0, 0, 0, 0.04);
                border: none;
                border-left: 3px solid #005FB8;
                padding: 8px 5px;
                icon-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.08);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.12);
            }
        """
        button.setStyleSheet(stylesheet)

    def _on_item_clicked(self, item_id: str) -> None:
        """Handle navigation item click.

        Args:
            item_id: ID of clicked item
        """
        self._set_selected_item(item_id)
        self.item_clicked.emit(item_id)

    def _set_selected_item(self, item_id: str) -> None:
        """Update visual state for selected item.

        Args:
            item_id: ID of item to select
        """
        # Deselect previous
        if self._selected_item_id and self._selected_item_id in self._items:
            self._apply_unselected_style(self._items[self._selected_item_id])

        # Select new
        if item_id in self._items:
            self._selected_item_id = item_id
            self._apply_selected_style(self._items[item_id])

    def get_selected_item_id(self) -> Optional[str]:
        """Get ID of currently selected item.

        Returns:
            Item ID or None
        """
        return self._selected_item_id

    def set_selected_item_by_id(self, item_id: str) -> None:
        """Programmatically select an item by ID.

        Args:
            item_id: ID of item to select
        """
        self._set_selected_item(item_id)
