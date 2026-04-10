import typing
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
    """Безопасное выполнение пользовательского Python кода с поддержкой n4.

    Изолирует выполнение пользовательского кода, предоставляя доступ к n4
    и выбранному вычислительному backend, при этом блокируя опасные операции.
    """

    def __init__(self) -> None:
        """Инициализировать исполнитель."""
        pass

    def _validate_ast(self, tree: ast.AST) -> None:
        """Проверить AST на запрещённые конструкции.

        Args:
            tree: AST дерево для проверки

        Raises:
            SecurityError: Если найдены запрещённые конструкции
        """

        for node in ast.walk(tree):
            # Проверка импортов
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    if module_name in FORBIDDEN_IMPORTS:
                        raise SecurityError(f"Import forbidden: {alias.name}")

            if isinstance(node, ast.ImportFrom):
                module_name = node.module if node.module else ""
                root_module = module_name.split(".")[0]

                if root_module in FORBIDDEN_IMPORTS:
                    raise SecurityError(f"Import forbidden: {module_name}")

            # Запрет на вызовы eval/exec/compile
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"exec", "eval", "compile"}:
                        raise SecurityError(f"Forbidden call: {node.func.id}")

    ALLOWED_MODULES = {
        "typing",
        # Add other safe stdlib modules as needed
    }

    def safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if name not in self.ALLOWED_MODULES:
            raise ImportError(f"Import of '{name}' not allowed in sandbox")
        return __import__(name, globals, locals, fromlist, level)

    def execute(
        self,
        code: str,
        backend_name: str = "PyFloat",
    ) -> dict[str, Any]:
        """Безопасно выполнить Python код в изолированном namespace.

        Предоставляет доступ к n4 API и выбранному backend для определения
        и запуска пользовательских моделей.

        Args:
            code: Python код для выполнения
            backend_name: Название вычислительного backend (PyFloat, NumPy, PyTorch)

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
                "__build_class__": __build_class__,
                "__import__": self.safe_import,
                "__name__": __name__,
                "range": range,
                "len": len,
                "print": print,
                "float": float,
                "int": int,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "str": str,
                "bool": bool,
                "type": type,
            },
        }

        local_env: dict[str, Any] = {}

        # Добавить n4 модули в глобальное окружение
        self._inject_n4_modules(safe_globals, backend_name)

        exec(compiled, safe_globals, local_env)

        return local_env

    def _inject_n4_modules(
        self,
        safe_globals: dict[str, Any],
        backend_name: str,
    ) -> None:
        """Инжектировать n4 модули и выбранный backend в namespace.

        Предоставляет доступ к основным классам n4 для определения моделей
        и выполнения операций автоматического дифференцирования.

        Args:
            safe_globals: Глобальный namespace для выполнения
            backend_name: Название backend для инжекции (PyFloat, NumPy и т.д.)
        """
        try:
            # Импортировать основные компоненты n4
            from n4.core import Value, Op
            from n4.tensor import Tensor
            from n4.numeric import PyFloat
            from n4.nn import (
                DenseLayer,
                ConvLayer,
                SoftmaxLayer,
                TanhLayer,
                Model,
                Sequential,
            )
            from n4.loss import MSELoss, CrossEntropyLoss
            from n4.op import Relu, Tanh, NonOp, Add, Mul, Div, Sub, Pow
            from n4.optim import SGD

            # Добавить базовые классы
            safe_globals["Value"] = Value
            safe_globals["Op"] = Op
            safe_globals["Tensor"] = Tensor

            # Добавить nn классы
            safe_globals["Model"] = Model
            safe_globals["Sequential"] = Sequential
            safe_globals["DenseLayer"] = DenseLayer
            safe_globals["ConvLayer"] = ConvLayer
            safe_globals["SoftmaxLayer"] = SoftmaxLayer
            safe_globals["TanhLayer"] = TanhLayer

            # Добавить loss функции
            safe_globals["MSELoss"] = MSELoss
            safe_globals["CrossEntropyLoss"] = CrossEntropyLoss

            # Добавить оптимизатор
            safe_globals["SGD"] = SGD

            # Добавить операции
            safe_globals["Relu"] = Relu
            safe_globals["Tanh"] = Tanh
            safe_globals["NonOp"] = NonOp
            safe_globals["Add"] = Add
            safe_globals["Mul"] = Mul
            safe_globals["Div"] = Div
            safe_globals["Sub"] = Sub
            safe_globals["Pow"] = Pow

            safe_globals["typing"] = typing

            # Инжектировать backend (выбранный или PyFloat по умолчанию)
            if backend_name == "PyFloat":
                backend = PyFloat
            else:
                # TODO: Поддержка NumPy и других backend
                backend = PyFloat

            safe_globals["T"] = backend
            safe_globals[backend_name] = backend
            safe_globals["PyFloat"] = PyFloat

        except ImportError as e:
            raise RuntimeError(f"Failed to import n4 modules: {e}")

    def extract_model(self, env: dict[str, Any]) -> Type[Any]:
        """Найти и вернуть класс модели из namespace выполнения.

        Ищет в пространстве имён класс, который является подклассом n4.nn.Model
        и не является самим базовым классом Model.

        Args:
            env: Namespace с переменными из выполненного кода

        Returns:
            Класс модели (подкласс n4.nn.Model)

        Raises:
            RuntimeError: Если не найдено подходящего класса модели
        """
        # Импортируем Model для проверки подклассов
        from n4.nn.model import Model

        for obj in env.values():
            if isinstance(obj, type):
                try:
                    if issubclass(obj, Model) and obj is not Model:
                        return obj
                except TypeError:
                    pass

        raise RuntimeError("No Model subclass found")
