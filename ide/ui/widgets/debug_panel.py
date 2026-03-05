from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)


class DebugPanel(QWidget):
    """Панель управления пошаговым backprop."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # ---- статус
        self.status_label = QLabel("Debug status: idle")

        layout.addWidget(self.status_label)

        # ---- кнопки
        btn_layout = QHBoxLayout()

        self.step_btn = QPushButton("Step Backward")
        self.run_btn = QPushButton("Run Backward")
        self.reset_btn = QPushButton("Reset")

        btn_layout.addWidget(self.step_btn)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(btn_layout)

        # ---- текущий узел
        self.node_label = QLabel("Current Node: None")

        layout.addWidget(self.node_label)

    def update_node(self, node_name: str):
        """Обновление отображения текущего узла."""
        self.node_label.setText(f"Current Node: {node_name}")