from enum import Enum, auto

from dataclasses import dataclass


class ApplicationState(Enum):
    IDLE = auto()
    TRAINING = auto()
    ERORRED = auto()
    COMPLETED = auto()


@dataclass(frozen=True)
class ApplicationStatus:
    status = ApplicationState.IDLE
    last_error_message = ""
