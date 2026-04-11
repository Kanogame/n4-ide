from typing import Type, Optional, Callable

from ide.domain.collectors.base import Collector


class CollectorRegistry:
    """Реестр для регистрации и создания экземпляров сборщиков.

    Позволяет регистрировать сборщики и получать их по имени для использования в процессе обучения
    """

    def __init__(self) -> None:
        """Инициализировать реестр метрик."""
        self._metrics: dict[str, Type[Collector]] = {}
        self._factories: dict[str, Callable[[], Collector]] = {}

    def register(
        self,
        name: str,
        metric_class: Type[Collector],
        factory: Optional[Callable[[], Collector]] = None,
    ) -> None:
        """Зарегистрировать новую метрику в реестре.

        Args:
            name: Уникальное имя метрики (e.g., "accuracy", "f1_score").
            metric_class: Класс метрики (подкласс Collector).
            factory: Опциональная фабрика для создания экземпляра.
                     Если не указана, использует metric_class().

        Raises:
            ValueError: Если метрика с таким именем уже зарегистрирована.
            TypeError: Если metric_class не является подклассом Collector.
        """
        if name in self._metrics:
            raise ValueError(f"Метрика '{name}' уже зарегистрирована")

        if not issubclass(metric_class, Collector):
            raise TypeError(
                f"Класс {metric_class.__name__} должен быть подклассом Collector"
            )

        self._metrics[name] = metric_class
        if factory:
            self._factories[name] = factory
        else:
            self._factories[name] = lambda: metric_class()

    def unregister(self, name: str) -> None:
        """Удалить метрику из реестра.

        Args:
            name: Имя метрики для удаления.

        Raises:
            KeyError: Если метрика с таким именем не зарегистрирована.
        """
        if name not in self._metrics:
            raise KeyError(f"Метрика '{name}' не зарегистрирована")

        del self._metrics[name]
        del self._factories[name]

    def create(self, name: str) -> Collector:
        """Создать экземпляр метрики по имени.

        Args:
            name: Имя зарегистрированной метрики.

        Returns:
            Новый экземпляр метрики.

        Raises:
            KeyError: Если метрика с таким именем не зарегистрирована.
        """
        if name not in self._metrics:
            available = ", ".join(self._metrics.keys())
            raise KeyError(
                f"Метрика '{name}' не найдена. Доступные метрики: {available}"
            )

        return self._factories[name]()

    def get_class(self, name: str) -> Type[Collector]:
        """Получить класс метрики по имени.

        Args:
            name: Имя зарегистрированной метрики.

        Returns:
            Класс метрики.

        Raises:
            KeyError: Если метрика с таким именем не зарегистрирована.
        """
        if name not in self._metrics:
            raise KeyError(f"Метрика '{name}' не зарегистрирована")

        return self._metrics[name]

    def list_metrics(self) -> list[str]:
        """Получить список всех зарегистрированных метрик.

        Returns:
            Список имён зарегистрированных метрик.
        """
        return list(self._metrics.keys())

    def is_registered(self, name: str) -> bool:
        """Проверить зарегистрирована ли метрика с таким именем.

        Args:
            name: Имя метрики для проверки.

        Returns:
            True если метрика зарегистрирована, False иначе.
        """
        return name in self._metrics

    def clear(self) -> None:
        """Очистить реестр (удалить все метрики).

        Используется в основном для тестирования.
        """
        self._metrics.clear()
        self._factories.clear()


# Глобальный экземпляр реестра
_global_registry: Optional[CollectorRegistry] = None


def get_collector_registry() -> CollectorRegistry:
    """Получить глобальный реестр сборщиков (создать если не существует)

    Returns:
        Глобальный экземпляр CollectoRegistry
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = CollectorRegistry()

    return _global_registry


def register_collector(
    name: str,
    metric_class: Type[Collector],
    factory: Optional[Callable[[], Collector]] = None,
) -> None:
    """Регистрация сборщиков в глобальном реестре.

    Args:
        metric_class: Класс сборщика
        factory: Опциональная фабрика для создания экземпляра,
                 без неё будет использоваться просто вызов класса без параметров
    """
    registry = get_collector_registry()
    registry.register(name, metric_class, factory)
