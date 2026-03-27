import sys
from typing import Callable, Optional, Any

from ide.domain.execution.executor import SafeExecutor
from ide.domain.execution.redirect import StdoutRedirect, StderrRedirect


class ExecutionController:
    """
    Контроллер для выполнения пользовательского кода с перенаправлением вывода.

    Служит мостом между presentation (UI сигналы) и domain (SafeExecutor).
    """

    def __init__(
        self,
        output_callback: Callable[[str], None],
    ) -> None:
        """
        Инициализировать контроллер выполнения.

        Args:
            output_callback: Функция для получения вывода программы
        """
        self.output_callback = output_callback
        self.executor = SafeExecutor()
        self._old_stdout: Optional[Any] = None
        self._old_stderr: Optional[Any] = None

    def run(self, code: str) -> dict[str, Any]:
        """
        Выполнить код с перенаправлением вывода.

        Args:
            code: Python код для выполнения

        Returns:
            Namespace (словарь переменных) из выполненного кода

        Raises:
            Exception: Если произошла ошибка при выполнении
        """
        # Перенаправить stdout/stderr
        stdout = StdoutRedirect(self.output_callback)
        stderr = StderrRedirect(self.output_callback)

        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr

        sys.stdout = stdout
        sys.stderr = stderr

        try:
            env = self.executor.execute(code)
            return env

        except Exception as e:
            self.output_callback(f"Error: {e}")
            raise

        finally:
            # Восстановить оригинальные stdout/stderr
            if self._old_stdout:
                sys.stdout = self._old_stdout
            if self._old_stderr:
                sys.stderr = self._old_stderr

    def extract_and_validate_model(self, env: dict[str, Any]) -> Any:
        """
        Найти модель в namespace и проверить её.

        Args:
            env: Namespace из выполненного кода

        Returns:
            Класс модели

        Raises:
            RuntimeError: Если модель не найдена
        """
        model_class = self.executor.extract_model(env)
        self.output_callback(f"Model detected: {model_class.__name__}")
        return model_class
