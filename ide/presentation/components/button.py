"""Button component for N4-IDE."""

from enum import Enum, auto
from typing import Optional
from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtGui import QFont


class ButtonStyle(Enum):
    """Button style variants."""

    ACCENT = auto()  # Blue primary button
    SECONDARY = auto()  # Light border button
    DANGER = auto()  # Red for destructive actions
    GHOST = auto()  # Text only


class Button(QPushButton):
    """Styled push button matching N4-IDE design system.

    Features:
    - Type-safe style variants
    - Consistent padding and typography
    - Smooth hover/active states
    """

    def __init__(
        self,
        text: str = "",
        style: ButtonStyle = ButtonStyle.ACCENT,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(text, parent)
        self.style_variant = style
        self._apply_style()

    def _apply_style(self) -> None:
        """Apply stylesheet based on style variant."""
        font = QFont("Open Sans", 14)
        font.setWeight(QFont.Weight.Normal)
        self.setFont(font)

        padding = "padding: 5px 12px 7px 12px;"
        border_radius = "border-radius: 4px;"

        if self.style_variant == ButtonStyle.ACCENT:
            stylesheet = f"""
                QPushButton {{
                    {padding}
                    background-color: #005FB8;
                    color: white;
                    border: 1px solid #2D7AC2;
                    {border_radius}
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background-color: #004A92;
                }}
                QPushButton:pressed {{
                    background-color: #003A70;
                }}
                QPushButton:disabled {{
                    background-color: #CCCCCC;
                    color: #666666;
                    border: 1px solid #EEEEEE;
                }}
            """
        elif self.style_variant == ButtonStyle.SECONDARY:
            stylesheet = f"""
                QPushButton {{
                    {padding}
                    background-color: rgba(255, 255, 255, 0.70);
                    color: rgba(0, 0, 0, 0.90);
                    border: 1px solid black;
                    {border_radius}
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background-color: white;
                    border: 1px solid #005FB8;
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 95, 184, 0.1);
                }}
                QPushButton:disabled {{
                    background-color: #F5F5F5;
                    color: #CCCCCC;
                    border: 1px solid #EEEEEE;
                }}
            """
        elif self.style_variant == ButtonStyle.DANGER:
            stylesheet = f"""
                QPushButton {{
                    {padding}
                    background-color: #DA3633;
                    color: white;
                    border: 1px solid #C5221F;
                    {border_radius}
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background-color: #B71C1C;
                }}
                QPushButton:pressed {{
                    background-color: #A91610;
                }}
                QPushButton:disabled {{
                    background-color: #CCCCCC;
                    color: #666666;
                    border: 1px solid #EEEEEE;
                }}
            """
        else:  # GHOST
            stylesheet = f"""
                QPushButton {{
                    {padding}
                    background-color: transparent;
                    color: rgba(0, 0, 0, 0.90);
                    border: none;
                    {border_radius}
                    font-weight: 400;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 95, 184, 0.08);
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 95, 184, 0.15);
                }}
                QPushButton:disabled {{
                    color: #CCCCCC;
                }}
            """

        self.setStyleSheet(stylesheet)

    def set_style(self, style: ButtonStyle) -> None:
        """Change button style variant."""
        self.style_variant = style
        self._apply_style()
