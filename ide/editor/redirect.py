import sys


class StdoutRedirect:
    """Перехват stdout для отображения в консоли IDE."""

    def __init__(self, callback):
        self.callback = callback

    def write(self, text):
        if text.strip():
            self.callback(text)

    def flush(self):
        pass


class StderrRedirect:
    """Перехват stderr."""

    def __init__(self, callback):
        self.callback = callback

    def write(self, text):
        if text.strip():
            self.callback(text)

    def flush(self):
        pass