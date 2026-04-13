from typing import Self, Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt6.QtCore import pyqtSignal



from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.common.mixins import StyledMixin


class StatusIcon(QFrame, StyledMixin):
    def __init__(self: Self, parent: Optional[QWidget]):
        