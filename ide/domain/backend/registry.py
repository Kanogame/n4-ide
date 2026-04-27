from dataclasses import dataclass
from typing import Optional

from n4.numeric import DecimalNum, NumericProtocol, NumpyFloat, PyFloat


@dataclass(frozen=True)
class BackendEntry:
    """Immutable descriptor for a numeric backend."""

    display_name: str
    backend_class: type[NumericProtocol]


class BackendRegistry:
    """Registry mapping display names to numeric backend classes.

    Backends are registered in priority order; the first registered
    is the default.
    """

    def __init__(self) -> None:
        self._entries: list[BackendEntry] = []
        self._by_name: dict[str, BackendEntry] = {}
        self._by_class: dict[type[NumericProtocol], BackendEntry] = {}

    def register(self, display_name: str, backend_class: type[NumericProtocol]) -> None:
        """Register a backend under a display name."""
        entry = BackendEntry(display_name=display_name, backend_class=backend_class)
        self._entries.append(entry)
        self._by_name[display_name] = entry
        self._by_class[backend_class] = entry

    def get_class(self, display_name: str) -> type[NumericProtocol]:
        """Return the backend class for *display_name*.

        Raises:
            KeyError: If no backend with that name is registered.
        """
        entry = self._by_name.get(display_name)
        if entry is None:
            raise KeyError(f"Unknown backend: {display_name!r}")
        return entry.backend_class

    def get_display_name(self, backend_class: type[NumericProtocol]) -> Optional[str]:
        """Return the display name for a backend class, or None if not found."""
        entry = self._by_class.get(backend_class)
        return entry.display_name if entry is not None else None

    def list_display_names(self) -> list[str]:
        """Return all registered display names in registration order."""
        return [e.display_name for e in self._entries]

    def get_default(self) -> type[NumericProtocol]:
        """Return the default (first registered) backend class."""
        if not self._entries:
            raise RuntimeError("No backends registered")
        return self._entries[0].backend_class

    def get_default_display_name(self) -> str:
        """Return the display name of the default backend."""
        if not self._entries:
            raise RuntimeError("No backends registered")
        return self._entries[0].display_name


# Module-level singleton — backends registered in display-name order.
_registry = BackendRegistry()
_registry.register("PyFloat", PyFloat)
_registry.register("NumpyFloat", NumpyFloat)
_registry.register("DecimalNum", DecimalNum)


def get_backend_registry() -> BackendRegistry:
    """Return the global backend registry."""
    return _registry
