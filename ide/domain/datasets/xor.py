from typing import Any

import numpy as np

from ide.domain.datasets.base import Dataset, DatasetField, DatasetResult, FieldType


class XorDataset(Dataset):
    """Улучшенный датасет XOR с возможностью увеличения размерности и добавления шума."""

    name = "improved_xor"
    description = "Improved XOR Dataset with optional extra dimensions"

    def get_fields(self) -> list[DatasetField]:
        return [
            DatasetField(
                name="samples_per_class",
                label="Количество точек на класс",
                field_type=FieldType.INTEGER,
                default_value=250,
                min_value=1,
                max_value=10000,
            ),
            DatasetField(
                name="noise",
                label="Стандартное отклонение шума",
                field_type=FieldType.FLOAT,
                default_value=0.15,
                min_value=0.0,
                max_value=0.5,
            ),
            DatasetField(
                name="extra_dimensions",
                label="Дополнительные измерения (шумовые)",
                field_type=FieldType.INTEGER,
                default_value=2,
                min_value=0,
                max_value=10,
            ),
        ]

    def generate(self, config: dict[str, Any]) -> DatasetResult:
        samples_per_class = config.get("samples_per_class", 250)
        noise = config.get("noise", 0.15)
        extra_dims = config.get("extra_dimensions", 2)

        # Базовые точки XOR
        base_points = [
            np.array([0.0, 0.0]),  # класс 0
            np.array([1.0, 1.0]),  # класс 0
            np.array([0.0, 1.0]),  # класс 1
            np.array([1.0, 0.0]),  # класс 1
        ]
        # One-hot метки
        one_hot_targets = [
            np.array([1.0, 0.0]),  # класс 0
            np.array([0.0, 1.0]),  # класс 1
        ]
        target_indices = [0, 0, 1, 1]

        X_list = []
        y_list = []

        for point, t_idx in zip(base_points, target_indices):
            # Основные координаты с шумом
            samples_2d = np.random.normal(
                loc=point, scale=noise, size=(samples_per_class, 2)
            )
            # Добавляем дополнительные измерения (шумовые)
            if extra_dims > 0:
                extra = np.random.normal(
                    loc=0.5, scale=0.2, size=(samples_per_class, extra_dims)
                )
                samples = np.hstack([samples_2d, extra])
            else:
                samples = samples_2d

            X_list.append(samples)
            y_list.extend([one_hot_targets[t_idx]] * samples_per_class)

        X = np.vstack(X_list)
        y = np.vstack(y_list)

        # Перемешивание
        indices = np.random.permutation(len(X))
        X, y = X[indices], y[indices]

        return DatasetResult(
            X=X,
            y=y,
            title="Улучшенный XOR",
            description=f"XOR с {len(X)} примерами, шум={noise}, доп.измерений={extra_dims}",
        )
