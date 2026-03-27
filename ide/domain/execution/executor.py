import ast
from typing import Type, Any


# Список запрещённых модулей для импорта в целях безопасности
FORBIDDEN_IMPORTS = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
}


class SecurityError(Exception):
    """Ошибка безопасности при выполнении кода."""

    pass


class SafeExecutor:
    """Безопасное выполнение пользовательского Python кода."""

    def __init__(self) -> None:
        pass

    def _validate_ast(self, tree: ast.AST) -> None:
        """
        Проверить AST на запрещённые конструкции.

        Args:
            tree: AST дерево для проверки

        Raises:
            SecurityError: Если найдены запрещённые конструкции
        """

        for node in ast.walk(tree):
            # Запрет на импорт запрещённых модулей
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in FORBIDDEN_IMPORTS:
                        raise SecurityError(f"Import forbidden: {alias.name}")

            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in FORBIDDEN_IMPORTS:
                    raise SecurityError(f"Import forbidden: {node.module}")

            # Запрет на вызовы eval/exec/compile
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"exec", "eval", "compile"}:
                        raise SecurityError(f"Forbidden call: {node.func.id}")

    def execute(self, code: str) -> dict:
        """
        Безопасно выполнить Python код в изолированном namespace.

        Args:
            code: Python код для выполнения

        Returns:
            Словарь с переменными из локального namespace

        Raises:
            SecurityError: Если код содержит запрещённые конструкции
        """

        tree = ast.parse(code)
        self._validate_ast(tree)

        compiled = compile(tree, "<user_code>", "exec")

        # Безопасное глобальное окружение с минимальными встроенными функциями
        safe_globals = {
            "__builtins__": {
                "range": range,
                "len": len,
                "print": print,
                "float": float,
                "int": int,
            }
        }

        local_env: dict[str, Any] = {}

        exec(compiled, safe_globals, local_env)

        return local_env

    def extract_model(self, env: dict) -> Type[Any]:
        """
        Найти и вернуть класс модели из namespace выполнения.

        Args:
            env: Namespace с переменными из выполненного кода

        Returns:
            Класс модели (подкласс n4.nn.Model)

        Raises:
            RuntimeError: Если не найдено подходящего класса модели
        """
        # Импортируем Model при необходимости для проверки

        from n4.nn.model import Model

        for obj in env.values():
            if isinstance(obj, type):
                try:
                    if issubclass(obj, Model) and obj is not Model:
                        return obj
                except TypeError:
                    pass

        raise RuntimeError("No Model subclass found")
