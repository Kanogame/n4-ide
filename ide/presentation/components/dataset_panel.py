from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QSlider,
)
from PyQt6.QtCore import Qt


class DatasetPanel(QWidget):
    """Панель для управления параметрами синтетических датасетов."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Dataset Preset"))

        self.preset = QComboBox()
        self.preset.addItems(
            [
                "Linear 1D",
                "Linear 2D",
                "XOR",
                "Gaussian Blobs",
            ]
        )

        layout.addWidget(self.preset)

        layout.addWidget(QLabel("Samples"))

        self.samples = QSlider(Qt.Orientation.Horizontal)
        self.samples.setMinimum(10)
        self.samples.setMaximum(500)
        self.samples.setValue(100)

        layout.addWidget(self.samples)
