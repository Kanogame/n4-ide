from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget


def create_vertical_layout(parent: QWidget, gap: int = 0) -> QVBoxLayout:
    """
    Хелпер для создания QVBoxLayout, без margin и с задаваемым gap

    Все элементы располагаются вертикально
    """

    layout = QVBoxLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(gap)

    return layout


def create_horizontal_layout(parent: QWidget, gap: int = 0) -> QHBoxLayout:
    """
    Хелпер для создания QHBoxLayout, без margin и с задаваемым gap

    Все элементы располагаются горизонтально
    """

    layout = QHBoxLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(gap)

    return layout
