import ast
from typing import Any

from n4.nn import Model
from n4.numeric import NumericProtocol

from ide.domain.backend import get_backend_registry

# Список запрещённых модулей для импорта в целях безопасности
_RESERVED_SANDBOX_NAMES: frozenset[str] = frozenset(
    {
        "Value",
        "Op",
        "Tensor",
        "Model",
        "Sequential",
        "DenseLayer",
        "ConvLayer",
        "SoftmaxLayer",
        "TanhLayer",
        "MSELoss",
        "CrossEntropyLoss",
        "SGD",
        "Relu",
        "Tanh",
        "NonOp",
        "Add",
        "Mul",
        "Div",
        "Sub",
        "Pow",
    }
)

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
        self._registry = get_backend_registry()

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
    }

    def safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if name not in self.ALLOWED_MODULES:
            raise ImportError(f"Import of '{name}' not allowed in sandbox")
        return __import__(name, globals, locals, fromlist, level)

    def execute(
        self,
        code: str,
        backend_type: type[NumericProtocol],
    ) -> dict[str, Any]:
        """Безопасно выполнить Python код в изолированном namespace.

        Предоставляет доступ к n4 API и выбранному backend для определения
        и запуска пользовательских моделей.

        Args:
            code: Python код для выполнения
            backend_type: Класс вычислительного backend (PyFloat, NumpyFloat, DecimalNum)

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
            },
        }

        local_env: dict[str, Any] = {}

        # Добавить n4 модули в глобальное окружение
        self._inject_n4_modules(safe_globals, backend_type)

        exec(compiled, safe_globals, local_env)

        return local_env

    def _inject_n4_modules(
        self,
        safe_globals: dict[str, Any],
        backend_type: type[NumericProtocol],
    ) -> None:
        """Инжектировать n4 модули и выбранный backend в namespace.

        Предоставляет доступ к основным классам n4 для определения моделей
        и выполнения операций автоматического дифференцирования.

        Args:
            safe_globals: Глобальный namespace для выполнения
            backend_type: Класс backend для инжекции
        """
        try:
            # Импортировать основные компоненты n4
            from n4.core import Op, Value
            from n4.loss import CrossEntropyLoss, MSELoss
            from n4.nn import (
                ConvLayer,
                DenseLayer,
                Model,
                Sequential,
                SoftmaxLayer,
                TanhLayer,
            )
            from n4.op import Add, Div, Mul, NonOp, Pow, Relu, Sub, Tanh
            from n4.optim import SGD
            from n4.tensor import Tensor

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

            # T is the canonical backend alias; also expose under the class name
            # so user code can write either `Model[T]` or `Model[PyFloat]`.
            safe_globals["T"] = backend_type
            safe_globals[backend_type.__name__] = backend_type

            # Expose every registered backend so imports like `PyFloat` still
            # resolve even when a different backend is active.
            for name in self._registry.list_display_names():
                cls = self._registry.get_class(name)
                if cls.__name__ in _RESERVED_SANDBOX_NAMES:
                    raise RuntimeError(
                        f"Backend class name {cls.__name__!r} collides with a reserved sandbox name"
                    )
                safe_globals[cls.__name__] = cls

        except ImportError as e:
            raise RuntimeError(f"Failed to import n4 modules: {e}")

    def extract_model(self, env: dict[str, Any]) -> type[Model]:
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

        for obj in env.values():
            if isinstance(obj, type):
                try:
                    if issubclass(obj, Model) and obj is not Model:
                        return obj
                except TypeError:
                    pass

        raise RuntimeError("No Model subclass found")
