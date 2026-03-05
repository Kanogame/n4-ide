import ast
from types import ModuleType
from typing import Type

from n4.nn import Model

# --- запрещённые модули
FORBIDDEN_IMPORTS = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
}


class SecurityError(Exception):
    """Ошибка безопасности."""
    pass


class SafeExecutor:
    """Безопасное выполнение пользовательского кода."""

    def __init__(self):
        pass

    def _validate_ast(self, tree: ast.AST) -> None:
        """Проверка AST на запрещённые конструкции."""

        for node in ast.walk(tree):

            # запрет import
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in FORBIDDEN_IMPORTS:
                        raise SecurityError(f"Import forbidden: {alias.name}")

            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in FORBIDDEN_IMPORTS:
                    raise SecurityError(f"Import forbidden: {node.module}")

            # запрет exec/eval
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"exec", "eval", "compile"}:
                        raise SecurityError(f"Forbidden call: {node.func.id}")

    def execute(self, code: str) -> dict:
        """Безопасное выполнение Python кода."""

        tree = ast.parse(code)

        self._validate_ast(tree)

        compiled = compile(tree, "<user_code>", "exec")

        # --- sandbox globals
        safe_globals = {
            "__builtins__": {
                "range": range,
                "len": len,
                "print": print,
                "float": float,
                "int": int,
            }
        }

        local_env = {}

        exec(compiled, safe_globals, local_env)

        return local_env

    def extract_model(self, env: dict) -> Type[Model]:
        """Поиск класса модели в окружении."""

        for obj in env.values():

            if isinstance(obj, type):

                try:
                    if issubclass(obj, Model) and obj is not Model:
                        return obj
                except TypeError:
                    pass

        raise RuntimeError("No Model subclass found")