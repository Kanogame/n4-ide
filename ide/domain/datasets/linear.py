from typing import Any

import numpy as np

from ide.domain.datasets.base import Dataset, DatasetField, DatasetResult, FieldType


class LinearRegressionDataset(Dataset):
    """
    Датасет для линейной регрессии: y = w*x + b + noise.
    Можно задать количество признаков, коэффициенты и уровень шума.
    """

    name = "linear_regression"
    description = "Classical linear regression dataset"

    def get_fields(self) -> list[DatasetField]:
        return [
            DatasetField(
                name="n_samples",
                label="Количество примеров",
                field_type=FieldType.INTEGER,
                default_value=500,
                min_value=10,
                max_value=100000,
            ),
            DatasetField(
                name="n_features",
                label="Количество признаков",
                field_type=FieldType.INTEGER,
                default_value=3,
                min_value=1,
                max_value=20,
            ),
            DatasetField(
                name="noise",
                label="Стандартное отклонение шума",
                field_type=FieldType.FLOAT,
                default_value=0.5,
                min_value=0.0,
                max_value=5.0,
            ),
            DatasetField(
                name="seed",
                label="Зерно генератора",
                field_type=FieldType.INTEGER,
                default_value=42,
                min_value=0,
                max_value=2**31 - 1,
            ),
        ]

    def generate(self, config: dict[str, Any]) -> DatasetResult:
        n_samples = config.get("n_samples", 500)
        n_features = config.get("n_features", 3)
        noise = config.get("noise", 0.5)
        seed = config.get("seed", 42)

        np.random.seed(seed)

        # Генерация истинных весов и смещения
        true_weights = np.random.uniform(-2.0, 2.0, size=(n_features, 1))
        true_bias = np.random.uniform(-1.0, 1.0)

        # Признаки из нормального распределения
        X = np.random.normal(0, 1, size=(n_samples, n_features))
        # Целевая переменная без шума
        y_clean = X @ true_weights + true_bias
        # Добавление шума
        y = y_clean + np.random.normal(0, noise, size=(n_samples, 1))

        return DatasetResult(
            X=X,
            y=y,
            title="Линейная регрессия",
            description=f"{n_samples} примеров, {n_features} признаков, шум={noise}",
        )
