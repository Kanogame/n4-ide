from .executor import SafeExecutor
from .redirect import StdoutRedirect
import sys


class ExecutionController:
    """Контроллер выполнения пользовательского кода."""

    def __init__(self, editor, console):
        self.editor = editor
        self.console = console
        self.executor = SafeExecutor()

    def run(self):
        """Запуск пользовательского кода."""

        code = self.editor.get_code()

        stdout = StdoutRedirect(self.console.append_text)
        stderr = StdoutRedirect(self.console.append_text)

        old_out = sys.stdout
        old_err = sys.stderr

        sys.stdout = stdout
        sys.stderr = stderr

        try:

            env = self.executor.execute(code)

            model_class = self.executor.extract_model(env)

            self.console.append_text(
                f"Model detected: {model_class.__name__}"
            )

        except Exception as e:

            self.console.append_text(f"Error: {e}")

        finally:

            sys.stdout = old_out
            sys.stderr = old_err