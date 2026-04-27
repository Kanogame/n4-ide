from typing import Optional

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


class FormField(QWidget):
    """Поле формы, комбинирующее метку и виджет ввода.

    Использует паттерн композиции для создания согласованного поля ввода:
    метка + виджет, расположенные горизонтально рядом друг с другом.

    Полезно для создания согласованных макетов форм с одинаковым
    расстоянием между элементами.

    Attributes:
        widget: Виджет ввода данных.
    """

    def __init__(
        self,
        label_text: str,
        widget: QWidget,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Инициализировать поле формы.

        Args:
            label_text: Текст метки, отображаемой слева от виджета.
            widget: Виджет ввода данных (QLineEdit, SpinBox и т.д.).
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.widget = widget

        # Создать горизонтальный макет
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Создать и оформить метку
        label = QLabel(label_text)
        font = QFont("Open Sans", 14)
        font.setWeight(QFont.Weight.Normal)
        label.setFont(font)
        label.setObjectName("FormFieldLabel")

        # Добавить элементы в макет
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.addStretch()

    def get_widget(self) -> QWidget:
        """Получить виджет ввода.

        Returns:
            Виджет, переданный при инициализации.
        """
        return self.widget
