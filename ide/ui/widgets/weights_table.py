from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem


class WeightsTable(QWidget):
    """Таблица параметров модели."""

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Value", "Grad"]
        )

        layout.addWidget(self.table)

    def update_parameters(self, parameters):
        """Обновление таблицы параметров."""

        self.table.setRowCount(len(parameters))

        for i, p in enumerate(parameters):
            self.table.setItem(i, 0, QTableWidgetItem(p.name))
            self.table.setItem(i, 1, QTableWidgetItem(str(p.value)))
            self.table.setItem(i, 2, QTableWidgetItem(str(p.grad)))