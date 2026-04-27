from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class ApplicationState(Enum):
    """Состояния приложения в явной машине состояний.

    Возможные переходы:
    - IDLE -> TRAINING (начало обучения)
    - TRAINING -> TRAINED (успешное завершение)
    - TRAINING -> ERROR (ошибка во время обучения)
    - ERROR -> TRAINING (повторное обучение)
    - Любое -> IDLE (сброс состояния)
    """

    # Начальное состояние, готовность к обучению
    IDLE = auto()

    # Процесс обучения модели
    TRAINING = auto()

    # Успешное завершение обучения
    TRAINED = auto()

    # Состояние ошибки
    ERROR = auto()


@dataclass(frozen=True)
class ApplicationStatus:
    """Неизменяемое состояние приложения.

    Attributes:
        state: Текущее состояние приложения (ApplicationState).
        error_message: Сообщение об ошибке (если state == ERROR).
    """

    state: ApplicationState
    error_message: Optional[str] = None

    def can_transition_to(self, next_state: "ApplicationState") -> bool:
        """Проверить допустимость перехода в новое состояние.

        Args:
            next_state: Целевое состояние.

        Returns:
            True если переход допустим, False иначе.
        """
        # Разрешённые переходы
        allowed_transitions: dict[ApplicationState, set[ApplicationState]] = {
            ApplicationState.IDLE: {ApplicationState.TRAINING},
            ApplicationState.TRAINING: {
                ApplicationState.TRAINED,
                ApplicationState.ERROR,
                ApplicationState.IDLE,
            },
            ApplicationState.TRAINED: {
                ApplicationState.TRAINING,
                ApplicationState.IDLE,
            },
            ApplicationState.ERROR: {ApplicationState.TRAINING, ApplicationState.IDLE},
        }

        return next_state in allowed_transitions.get(self.state, set())
