from typing import Optional, Self, TYPE_CHECKING
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal

from ide.presentation.common.layouts import create_vertical_layout
from ide.presentation.components.common.button import Button, ButtonStyle
from ide.presentation.components.common.combobox import ComboBox
from ide.presentation.components.common.form_field import FormField

from ide.presentation.components.model_panel.editor import Editor
from ide.presentation.components.common.panel_view import PanelView, PanelToolbar

if TYPE_CHECKING:
    from ide.application.file_manager import FileSaveResult, FileLoadResult


@dataclass(frozen=True)
class ModelInfo:
    """Неизменяемый снимок информации о модели.

    Attributes:
        backend: Имя вычислительного бекенда (по умолчанию "PyFloat").
        layer_count: Количество слоёв в модели.
        total_parameters: Общее количество параметров модели.
        code: Исходный код модели.
    """

    backend: str = "PyFloat"
    layer_count: int = 0
    total_parameters: int = 0
    code: str = ""


class ModelPanelView(QWidget):
    """Панель визуализации и редактирования модели нейронной сети.

    Компонент отображает редактор кода модели и позволяет выбрать
    вычислительный бекенд для выполнения.

    Signals:
        train_requested: Сигнал при нажатии на кнопку обучения.
        backend_changed: Сигнал при изменении выбранного бекенда.
        file_new_requested: Создать новый файл.
        file_open_requested: Открыть файл.
        file_save_requested: Сохранить файл.
        file_save_as_requested: Сохранить файл как...
    """

    # Сигнал при нажатии на кнопку обучения.
    train_requested = pyqtSignal()

    # Сигнал при изменении выбора вычислительного бекенда.
    backend_changed = pyqtSignal(str)

    # Сигналы файловых операций (для главного окна)
    file_new_requested = pyqtSignal()
    file_open_requested = pyqtSignal()
    file_save_requested = pyqtSignal()
    file_save_as_requested = pyqtSignal()

    # Сигналы для загрузки/сохранения из приложения
    model_save_finished = pyqtSignal(object)  # FileSaveResult
    model_load_finished = pyqtSignal(object)  # FileLoadResult

    def __init__(self: Self, parent: Optional[QWidget] = None) -> None:
        """Инициализировать панель модели"""
        super().__init__(parent)

        self._current_model_info = ModelInfo()
        self._current_file_path: Optional[str] = None

        # Основной layout панели
        layout = create_vertical_layout(self)

        # Создать панель с тулбаром
        self.toolbar = self.create_toolbar()
        self.main_content = PanelView("Описание модели", self.toolbar)

        # Создать выбор бекенда
        self.create_backend_selector()

        # Создать редактор кода
        self.editor = Editor()
        self.main_content.add_widget(self.editor)

        # Создать кнопки управления
        self.create_buttons()

        layout.addWidget(self.main_content)

        # Подключить сигналы тулбара к обработчикам (без App)
        self.toolbar.new_file_requested.connect(self._on_new_file)
        self.toolbar.open_file_requested.connect(self._on_open_file)
        self.toolbar.save_file_requested.connect(self._on_save_file)
        self.toolbar.save_as_file_requested.connect(self._on_save_as_file)
        self.toolbar.undo_requested.connect(self._on_undo)
        self.toolbar.redo_requested.connect(self._on_redo)

        # Подключить сигналы редактора для отслеживания состояния undo/redo
        self.editor.editor.textChanged.connect(self._on_editor_text_changed)

    def _on_new_file(self: Self) -> None:
        """Обработчик создания нового файла.

        Очищает редактор и сбрасывает состояние.
        """
        # Спросить подтверждение если есть неохраненный код
        if self.editor.editor.isModified():
            reply = QMessageBox.question(
                self,
                "Новый файл",
                "Текущий файл содержит несохраненные изменения.\nПродолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Очистить редактор и установить шаблон
        self.editor.editor.setText(self.editor._default_template())
        self.editor.editor.setModified(False)

    def _on_open_file(self: Self) -> None:
        """Обработчик открытия файла.

        Эмитирует сигнал для главного окна, который откроет диалог.
        """
        # Эмитировать сигнал для главного окна
        self.file_open_requested.emit()

    def _on_save_file(self: Self) -> None:
        """Обработчик сохранения текущего файла.

        Если файл еще не был сохранён, открывает диалог.
        """
        # Если есть текущий путь — сохранить туда, иначе — "Сохранить как"
        if not hasattr(self, "_current_file_path") or not self._current_file_path:
            self._on_save_as_file()
            return

        # Эмитировать сигнал для главного окна
        self.file_save_requested.emit()

    def _on_save_as_file(self: Self) -> None:
        """Обработчик сохранения файла с выбором пути.

        Эмитирует сигнал для главного окна, который откроет диалог сохранения.
        """
        # Эмитировать сигнал для главного окна
        self.file_save_as_requested.emit()

    def _on_undo(self: Self) -> None:
        """Обработчик отмены последнего действия.

        Делегирует команду редактору QScintilla.
        """
        if self.editor.editor.isUndoAvailable():
            self.editor.editor.undo()

    def _on_redo(self: Self) -> None:
        """Обработчик повтора отменённого действия.

        Делегирует команду редактору QScintilla.
        """
        if self.editor.editor.isRedoAvailable():
            self.editor.editor.redo()

    def _on_editor_text_changed(self: Self) -> None:
        """Обработчик изменения текста в редакторе.

        Обновляет доступность команд undo/redo.
        """
        undo_available = self.editor.editor.isUndoAvailable()
        redo_available = self.editor.editor.isRedoAvailable()
        self.toolbar.set_undo_enabled(undo_available)
        self.toolbar.set_redo_enabled(redo_available)

    def _on_model_save_result(self: Self, result: "FileSaveResult") -> None:
        """Обработчик результата сохранения модели из приложения.

        Args:
            result: FileSaveResult с информацией о результате.
        """
        if not result.success:
            QMessageBox.warning(
                self, "Ошибка сохранения", f"Не удалось сохранить файл: {result.error}"
            )
        else:
            # Сохранить текущий путь и очистить флаг изменений
            if result.file_path:
                self._current_file_path = result.file_path
            self.editor.editor.setModified(False)

    def _on_model_load_result(self: Self, result: "FileLoadResult") -> None:
        """Обработчик результата загрузки модели из приложения.

        Args:
            result: FileLoadResult с загруженным содержимым.
        """
        if result.success and result.content:
            # Установить загруженный код в редактор
            self.editor.editor.setText(result.content)
            self.editor.editor.setModified(False)
        elif not result.success:
            QMessageBox.warning(
                self, "Ошибка загрузки", f"Не удалось загрузить файл: {result.error}"
            )

    def create_toolbar(self: Self) -> PanelToolbar:
        """Создать тулбар панели.

        Returns:
            Экземпляр PanelToolbar с кнопками действий.
        """
        return PanelToolbar()

    def create_backend_selector(self: Self) -> None:
        """Создать выпадающий список выбора вычислительного бекенда.

        Поддерживаемые бекенды: PyFloat, NumPy, PyTorch.
        Подключает сигнал изменения на backend_changed.
        """
        self.backend_combo = ComboBox()
        self.backend_combo.addItems(["PyFloat", "NumPy", "PyTorch"])
        self.backend_combo.value_changed.connect(self.backend_changed.emit)

        backend_field = FormField("Вычислительный бекенд", self.backend_combo)
        self.main_content.add_widget(backend_field)

    def create_buttons(self: Self) -> None:
        """Создать кнопки управления панели.

        Включает кнопку "Обучить" для запуска процесса обучения модели.
        """
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        self.train_button = Button("Обучить", ButtonStyle.ACCENT)
        self.train_button.clicked.connect(self.train_requested.emit)
        buttons_layout.addWidget(self.train_button)

        self.main_content.add_layout(buttons_layout)

    def get_selected_backend(self: Self) -> str:
        """Get currently selected backend.

        Returns:
            Backend name
        """
        return self.backend_combo.currentText()

    def get_current_model_info(self: Self) -> ModelInfo:
        """Get current model information.

        Returns:
            ModelInfo dataclass
        """
        return self._current_model_info

    def get_model_code(self: Self) -> str:
        """Получить исходный код модели из редактора.

        Returns:
            Текст кода модели.
        """
        return self.editor.get_model_code()
