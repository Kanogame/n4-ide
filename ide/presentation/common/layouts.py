from PyQt6.QtWidgets import QWidget, QVBoxLayout


def create_layout(parent: QWidget, gap: int = 0) -> QVBoxLayout:
    """
    Хелпер для создания QVBoxLayout, без margin и с задаваемым gap
    """

    layout = QVBoxLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(gap)

    return layout
