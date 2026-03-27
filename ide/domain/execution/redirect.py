class StdoutRedirect:
    """Перенаправление stdout для отображения в консоли IDE."""

    def __init__(self, callback) -> None:
        self.callback = callback

    def write(self, text: str) -> None:
        """Перехватить вывод и передать в callback."""
        if text.strip():
            self.callback(text)

    def flush(self) -> None:
        """Flush буфера (заглушка)."""
        pass


class StderrRedirect:
    """Перенаправление stderr для отображения в консоли IDE."""

    def __init__(self, callback) -> None:
        self.callback = callback

    def write(self, text: str) -> None:
        """Перехватить ошибку и передать в callback."""
        if text.strip():
            self.callback(text)

    def flush(self) -> None:
        """Flush буфера (заглушка)."""
        pass
