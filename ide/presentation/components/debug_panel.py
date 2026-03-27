from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)


class DebugPanel(QWidget):
    """Панель управления пошаговым backprop отладчиком."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        # Статус отладки
        self.status_label = QLabel("Debug status: idle")
        layout.addWidget(self.status_label)

        # Кнопки управления
        btn_layout = QHBoxLayout()

        self.step_btn = QPushButton("Step Backward")
        self.run_btn = QPushButton("Run Backward")
        self.reset_btn = QPushButton("Reset")

        btn_layout.addWidget(self.step_btn)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(btn_layout)

        # Текущий узел
        self.node_label = QLabel("Current Node: None")
        layout.addWidget(self.node_label)

    def update_node(self, node_name: str) -> None:
        """Обновить отображение текущего узла."""
        self.node_label.setText(f"Current Node: {node_name}")

    def update_status(self, status: str) -> None:
        """Обновить статус отладки."""
        self.status_label.setText(f"Debug status: {status}")
