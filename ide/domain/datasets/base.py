from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class FieldType(Enum):
    """Тип поля конфигурации датасета.

    Используется для определения типа контрола в пользовательском интерфейсе.
    """

    # Целое число
    INTEGER = "integer"

    # Число с плавающей точкой
    FLOAT = "float"

    # Выбор из списка
    CHOICE = "choice"

    # Текстовое поле
    TEXT = "text"


@dataclass(frozen=True)
class DatasetField:
    """Определение поля конфигурации датасета.

    Immutable структура, описывающая одно поле конфигурации,
    которое пользователь может изменять через UI.

    Attributes:
        name: Внутреннее имя поля (используется для доступа).
        label: Отображаемое имя поля в UI.
        field_type: Тип поля (INTEGER, FLOAT, CHOICE, TEXT).
        default_value: Значение по умолчанию.
        min_value: Минимальное значение (для INTEGER/FLOAT).
        max_value: Максимальное значение (для INTEGER/FLOAT).
        choices: Возможные значения (для CHOICE).
    """

    name: str
    label: str
    field_type: FieldType
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[list[str]] = None


@dataclass(frozen=True)
class DatasetResult:
    """Результат генерации датасета.

    Immutable структура с результатом выполнения датасета,
    передаётся через Qt signals.

    Attributes:
        X: Массив входных данных (numpy array).
        y: Массив целевых значений (numpy array).
        title: Название датасета для отображения.
        description: Описание датасета.
    """

    X: Any  # numpy.ndarray
    y: Any  # numpy.ndarray
    title: str = ""
    description: str = ""


class Dataset(ABC):
    """Абстрактный базовый класс для датасетов.

    Определяет интерфейс, который должны реализовать все датасеты
    для интеграции с N4-IDE.

    Подклассы должны:
    1. Реализовать `get_fields()` для определения параметров конфигурации
    2. Реализовать `generate()` для создания данных датасета
    3. Задать уникальный `name` и `description`
    """

    # Имя датасета (уникальный идентификатор)
    name: str = ""

    # Описание датасета
    description: str = ""

    @abstractmethod
    def get_fields(self) -> list[DatasetField]:
        """Получить список полей конфигурации датасета.

        Возвращаемые поля определяют параметры, которые пользователь
        может изменять через интерфейс.

        Returns:
            Список DatasetField, описывающих конфигурируемые параметры.
        """
        pass

    @abstractmethod
    def generate(self, config: dict[str, Any]) -> DatasetResult:
        """Сгенерировать данные датасета с заданной конфигурацией.

        Args:
            config: Словарь конфигурации с ключами из DatasetField.name
                   и значениями, выбранными пользователем.

        Returns:
            DatasetResult с сгенерированными данными X и y.
        """
        pass
