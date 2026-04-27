from typing import Any

import numpy as np

from ide.domain.datasets.base import Dataset, DatasetField, DatasetResult, FieldType


class TwirlBordersDataset(Dataset):
    """
    Датасет с двумя переплетёнными спиралями (two interleaved spirals).
    Классическая задача классификации с нелинейной границей.
    """

    name = "twirl_borders"
    description = "Two spirals dataset (twirl borders)"

    def get_fields(self) -> list[DatasetField]:
        return [
            DatasetField(
                name="points_per_class",
                label="Точек на класс",
                field_type=FieldType.INTEGER,
                default_value=200,
                min_value=50,
                max_value=2000,
            ),
            DatasetField(
                name="noise",
                label="Шум (стандартное отклонение)",
                field_type=FieldType.FLOAT,
                default_value=0.05,
                min_value=0.0,
                max_value=0.2,
            ),
            DatasetField(
                name="turns",
                label="Количество витков",
                field_type=FieldType.FLOAT,
                default_value=2.0,
                min_value=1.0,
                max_value=5.0,
            ),
        ]

    def generate(self, config: dict[str, Any]) -> DatasetResult:
        n_points = config.get("points_per_class", 200)
        noise = config.get("noise", 0.05)
        turns = config.get("turns", 2.0)

        # Генерация спиралей
        theta = np.linspace(0, turns * 2 * np.pi, n_points)
        r = np.linspace(0, 1, n_points)

        # Спираль класса 0
        x0 = r * np.cos(theta)
        y0 = r * np.sin(theta)
        # Спираль класса 1 (повёрнута на pi)
        x1 = r * np.cos(theta + np.pi)
        y1 = r * np.sin(theta + np.pi)

        # Добавление шума
        x0 += np.random.normal(0, noise, n_points)
        y0 += np.random.normal(0, noise, n_points)
        x1 += np.random.normal(0, noise, n_points)
        y1 += np.random.normal(0, noise, n_points)

        # Формирование массивов
        X_class0 = np.column_stack([x0, y0])
        X_class1 = np.column_stack([x1, y1])

        X = np.vstack([X_class0, X_class1])
        # One-hot метки: класс 0 -> [1,0], класс 1 -> [0,1]
        y = np.vstack(
            [np.tile([1.0, 0.0], (n_points, 1)), np.tile([0.0, 1.0], (n_points, 1))]
        )

        # Перемешивание
        indices = np.random.permutation(2 * n_points)
        X, y = X[indices], y[indices]

        return DatasetResult(
            X=X,
            y=y,
            title="Две спирали",
            description=f"Две спирали, {n_points} точек на класс, шум={noise}, витков={turns}",
        )
