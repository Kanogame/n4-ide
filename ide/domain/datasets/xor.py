from typing import Any
import numpy as np
from ide.domain.datasets.base import Dataset, DatasetField, DatasetResult, FieldType


class XORDataset(Dataset):
    """Датасет XOR (исключающее ИЛИ).

    Генерирует простой датасет с двумя входами и одним выходом,
    реализующий логическую операцию XOR:
    - [0, 0] → 0
    - [0, 1] → 1
    - [1, 0] → 1
    - [1, 1] → 0

    Датасет можно масштабировать путём добавления шума и дублирования
    основных точек.

    Attributes:
        name: Идентификатор датасета "xor"
        description: Человеческое описание "XOR Dataset"
    """

    name = "xor"
    description = "XOR Dataset"

    def get_fields(self) -> list[DatasetField]:
        """Получить параметры конфигурации XOR датасета.

        XOR датасет имеет два основных параметра:
        - samples_per_class: сколько раз дублировать каждый из 4 базовых примеров
        - noise: стандартное отклонение гауссова шума для добавления к входным данным

        Returns:
            Список из двух DatasetField для конфигурации.
        """
        return [
            DatasetField(
                name="samples_per_class",
                label="Samples per class",
                field_type=FieldType.INTEGER,
                default_value=100,
                min_value=1,
                max_value=10000,
            ),
            DatasetField(
                name="noise",
                label="Noise std",
                field_type=FieldType.FLOAT,
                default_value=0.1,
                min_value=0.0,
                max_value=1.0,
            ),
        ]

    def generate(self, config: dict[str, Any]) -> DatasetResult:
        """Сгенерировать XOR датасет с заданной конфигурацией.

        Процесс генерации:
        1. Создать 4 базовых точки XOR (углы квадрата)
        2. Дублировать каждую точку samples_per_class раз
        3. Добавить гауссов шум согласно noise параметру
        4. Создать соответствующие целевые значения (y)

        Args:
            config: Словарь с ключами "samples_per_class" и "noise".

        Returns:
            DatasetResult с массивами X (n_samples, 2) и y (n_samples,).
        """
        samples_per_class: int = config.get("samples_per_class", 100)
        noise: float = config.get("noise", 0.1)

        # Базовые точки XOR (4 класса на углах квадрата)
        # Класс 0: [0, 0] и [1, 1] (целевое значение 0)
        # Класс 1: [0, 1] и [1, 0] (целевое значение 1)
        base_points = [
            np.array([0.0, 0.0]),  # XOR: 0
            np.array([1.0, 1.0]),  # XOR: 0
            np.array([0.0, 1.0]),  # XOR: 1
            np.array([1.0, 0.0]),  # XOR: 1
        ]

        targets = [0, 0, 1, 1]

        X_list: list[np.ndarray] = []
        y_list: list[int] = []

        # Генерировать sample_per_class примеров около каждой базовой точки
        for point, target in zip(base_points, targets):
            # Создать samples_per_class примеров вокруг базовой точки
            samples = np.random.normal(
                loc=point,
                scale=noise,
                size=(samples_per_class, 2),
            )

            X_list.append(samples)
            y_list.extend([target] * samples_per_class)

        # Объединить все примеры
        X = np.vstack(X_list)
        y = np.array(y_list)

        # Перемешать датасет
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]

        return DatasetResult(
            X=X,
            y=y,
            title="XOR Dataset",
            description=f"XOR with {len(X)} samples and noise={noise}",
        )
