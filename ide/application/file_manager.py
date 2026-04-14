from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Self


@dataclass(frozen=True)
class FileSaveResult:
    """Неизменяемый результат операции сохранения файла.

    Attributes:
        success: Флаг успеха операции.
        file_path: Путь к сохранённому файлу (если успешно).
        error: Текст ошибки (если произошла).
    """

    success: bool
    file_path: Optional[str] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class FileLoadResult:
    """Неизменяемый результат операции загрузки файла.

    Attributes:
        success: Флаг успеха операции.
        content: Загруженное содержимое файла (если успешно).
        error: Текст ошибки (если произошла).
    """

    success: bool
    content: Optional[str] = None
    error: Optional[str] = None


class FileManager:
    """Менеджер для сохранения и загрузки кода моделей из файлов.

    Предоставляет методы для работы с кодом Python моделей,
    обеспечивая единую точку доступа для файловых операций.
    """

    def save_model_code(self: Self, file_path: str, code: str) -> FileSaveResult:
        """Сохранить код модели в файл.

        Args:
            file_path: Полный путь к файлу для сохранения.
            code: Содержимое кода модели.

        Returns:
            FileSaveResult с информацией о результате операции.
        """
        try:
            path = Path(file_path)

            # Создать родительскую директорию если её нет
            path.parent.mkdir(parents=True, exist_ok=True)

            # Записать код в файл
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

            return FileSaveResult(success=True, file_path=str(path))

        except IOError as e:
            return FileSaveResult(success=False, error=f"Ошибка ввода-вывода: {e}")
        except OSError as e:
            return FileSaveResult(
                success=False, error=f"Ошибка операционной системы: {e}"
            )
        except Exception as e:
            return FileSaveResult(success=False, error=f"Неизвестная ошибка: {e}")

    def load_model_code(self: Self, file_path: str) -> FileLoadResult:
        """Загрузить код модели из файла.

        Args:
            file_path: Полный путь к файлу для загрузки.

        Returns:
            FileLoadResult с содержимым файла или информацией об ошибке.
        """
        try:
            path = Path(file_path)

            # Проверить что файл существует
            if not path.exists():
                return FileLoadResult(
                    success=False, error=f"Файл не найден: {file_path}"
                )

            # Прочитать содержимое файла
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return FileLoadResult(success=True, content=content)

        except IOError as e:
            return FileLoadResult(success=False, error=f"Ошибка ввода-вывода: {e}")
        except OSError as e:
            return FileLoadResult(
                success=False, error=f"Ошибка операционной системы: {e}"
            )
        except Exception as e:
            return FileLoadResult(success=False, error=f"Неизвестная ошибка: {e}")
