from enum import Enum, auto
from dataclasses import dataclass


class NavItemType(Enum):
    """Тип элемента навигационной панели для группировки.

    Attributes:
        TOOL: Кнопка с инструментом (иконка + сигнал).
        SEPARATOR: Разделитель между элементами.
        SPACER: Пустой элемент для выравнивания.
    """

    TOOL = auto()
    SEPARATOR = auto()
    SPACER = auto()


@dataclass(frozen=True)
class NavItem:
    """Неизменяемое описание элемента навигационной панели.

    Attributes:
        id: Уникальный идентификатор элемента.
        icon_path: Путь к файлу иконки (SVG/PNG) для отображения.
        tooltip: Текст подсказки при наведении.
        type: Тип элемента (инструмент, разделитель и т.д.).
    """

    id: str
    icon_path: str
    tooltip: str = ""
    type: NavItemType = NavItemType.TOOL
