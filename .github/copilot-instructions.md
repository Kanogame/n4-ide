# N4-IDE Agent Instructions

## Project Vision

**N4-IDE** is a visual neural network IDE for the n4 autograd framework, enabling users to write Python code that defines neural networks while seeing real-time visualizations of computation graphs and layer hierarchies.

### Core Principles

- **Decoupled Architecture**: Strict separation between UI, orchestration, and domain logic
- **Type-Safe**: Full typing (`Python ≥3.13`) throughout for IDE support and runtime clarity
- **Thread-Safe**: All long-running operations isolated from main thread
- **Signal-Driven**: Qt signal/slot architecture for loose coupling between components
- **Immutable Data Flow**: Signals pass immutable data structures, never mutable references
- **Single Source of Truth**: Application state centralized in one location

---

## Mandatory Folder Layout

The project MUST follow this directory structure to maintain strict separation of concerns:

```
ide/
├── __init__.py                          # Entry point with IDE class
├── presentation/                        # Presentation Layer (PyQt6 UI)
│   ├── __init__.py
│   ├── components/                      # Reusable UI components
│   │   ├── __init__.py
│   │   ├── console_widget.py           # Console output display
│   │   ├── graph_view.py               # Computation graph visualization
│   │   ├── weights_table.py            # Model parameters table
│   │   ├── dataset_panel.py            # Dataset management
│   │   ├── debug_panel.py              # Debug controls
│   │   └── editor_widget.py            # Python code editor
│   └── views/                           # Full views (windows/dialogs)
│       ├── __init__.py
│       └── main_window.py              # Main application window
├── application/                         # Application Layer (State & Orchestration)
│   ├── __init__.py
│   └── app.py                          # Central Application state machine
└── domain/                              # Domain Layer (Business Logic)
    ├── __init__.py
    └── execution/                       # Code execution logic
        ├── __init__.py
        ├── executor.py                 # Safe code execution (SafeExecutor)
        ├── redirect.py                 # Output redirection (stdout/stderr)
        └── controller.py               # Execution orchestration
```

### Key Principles for Folder Structure

1. **Presentation Layer** (`ide/presentation/`)
   - Contains ONLY PyQt6 widgets and UI components
   - NO business logic or domain imports (except via signals)
   - Components are reusable and self-contained
   - All communication via `pyqtSignal` emissions

2. **Application Layer** (`ide/application/`)
   - Contains `Application` class: central state machine
   - Manages state: models, execution results, user settings
   - Emits signals when state changes
   - Coordinates between Presentation and Domain layers
   - Contains immutable data structures (dataclasses) for signal passing

3. **Domain Layer** (`ide/domain/`)
   - Contains business logic completely independent of PyQt6
   - `execution/` subdirectory handles code execution and safety
   - No UI dependencies whatsoever
   - Can be tested without PyQt6

**IMPORTANT**: Never deviate from this structure. All new features MUST fit into one of these three layers.

---

## Architecture Principles

### Layered Design

```
┌────────────────────────────────────────────┐
│ Presentation Layer (PyQt6 Widgets)         │
│ - Only handles rendering and user input    │
│ - Emits signals, never calls methods       │
└────────────────┬─────────────────────────┘
                 │ Signals
┌────────────────▼─────────────────────────┐
│ Application Layer (State & Orchestration)  │
│ - Central state machine                    │
│ - Coordinates between UI and domain        │
└────────────────┬─────────────────────────┘
                 │ Method calls
┌────────────────▼─────────────────────────┐
│ Domain Layer (Business Logic)              │
│ - Code execution, graph analysis, etc.    │
│ - No dependency on PyQt6                   │
└────────────────┬─────────────────────────┘
                 │ Imports
┌────────────────▼─────────────────────────┐
│ Integration Layer (n4 Library)             │
│ - Import n4 symbols                        │
│ - Type-safe wrappers if needed             │
└─────────────────────────────────────────┘
```

### Data Flow

```
User Input (EditorWidget)
         ↓ (signal)
Application State
         ↓ (calls domain)
Domain Logic (Executor, GraphBuilder, etc.)
         ↓ (returns result)
Application State (updated)
         ↓ (signal emitted)
UI Widgets (updated)
```

### Key Design Patterns

1. **MVC with Signals**: Model state changes emit signals; Views listen passively
2. **Dependency Injection**: All components receive dependencies via constructor
3. **Repository Pattern**: Data access abstraction for files, models, datasets
4. **Command Pattern**: Actionable events (Run, Debug, Save) as distinct operations
5. **Observer**: Qt signals/slots for inter-component communication

### Invariants

- **No blocking main thread**: All I/O and computation runs on QThread
- **Type consistency**: All n4 Values/Tensors share the same numeric backend
- **State locality**: Domain logic doesn't access UI directly; uses callbacks/signals
- **Signal immutability**: Signals carry frozen dataclasses or primitives
- **Decoupled widgets**: Widgets don't reference each other; only communicate via Application

---

## Python & PyQt6 Standards

### Type Hints (Mandatory)

Every function must have complete type annotations:

```python
from typing import Optional, Callable, Any, TypeVar, Generic

# Basic function
def process_code(code: str, timeout_ms: int) -> ExecutionResult:
    """Execute code with timeout."""
    pass

# With generics
T = TypeVar('T')

def transform(value: T, fn: Callable[[T], T]) -> T:
    """Apply function to value."""
    return fn(value)

# Complex types
from typing import Protocol, TypeVar

class Visualizable(Protocol):
    """Something that can be rendered."""
    def to_graphics_item(self) -> QGraphicsItem:
        """Convert to Qt graphics item."""
        ...

def display(obj: Visualizable) -> None:
    """Display object."""
    scene.addItem(obj.to_graphics_item())
```

**Rule**: If type checker complains, add explicit type. Don't use `Any` unless truly generic.

### Dataclasses for Data Transfer

Use `@dataclass` for immutable data objects (DTO pattern):

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ExecutionResult:
    """Immutable result of code execution."""
    success: bool
    output: str
    error: Optional[str] = None
    duration_ms: float = 0.0
    variables: dict[str, Any] = field(default_factory=dict)

# Usage: signals pass dataclass instances
finished = pyqtSignal(ExecutionResult)  # Type-safe signal
finished.emit(ExecutionResult(success=True, output="OK"))
```

**Benefits**:

- Immutable prevents accidental mutations
- IDE autocomplete for all fields
- Serializable for persistence
- Better than `dict` for clarity

### Enums for Constants

Use `Enum` for fixed sets of values:

```python
from enum import Enum, auto

class ExecutionMode(Enum):
    """Execution mode for code runner."""
    RUN = auto()
    DEBUG = auto()
    STEP = auto()

class NodeType(Enum):
    """Types of nodes in computation graph."""
    VALUE = "value"
    OPERATION = "operation"
    LAYER = "layer"

# Use in type hints
def configure_executor(mode: ExecutionMode) -> None:
    if mode == ExecutionMode.DEBUG:
        # Debug-specific setup
        pass

# Compare safely
assert result.node_type == NodeType.OPERATION
```

**Benefits**:

- Type-safe instead of magic strings
- IDE catches typos
- Prevents invalid values

### Error Handling with Context

Always provide context in exceptions:

```python
class CodeExecutionError(Exception):
    """Code execution failed."""
    def __init__(
        self,
        code: str,
        line_number: int,
        error: Exception,
    ) -> None:
        self.code = code
        self.line_number = line_number
        self.error = error
        super().__init__(
            f"Execution error at line {line_number}: {error}"
        )

# Raise with context
try:
    exec(user_code, namespace)
except Exception as e:
    raise CodeExecutionError(
        code=user_code,
        line_number=extract_line_number(e),
        error=e,
    ) from e
```

**Rule**: Never raise bare exceptions. Provide actionable context.

### PyQt6 Patterns

1. **Signals for Communication**: Never directly call methods on widgets

   ```python
   # ❌ WRONG: Direct coupling
   class Button(QPushButton):
       def on_click(self):
           self.parent().editor.run_code()

   # ✅ CORRECT: Signals for decoupling
   class Button(QPushButton):
       run_requested = pyqtSignal(str)

       def __init__(self):
           super().__init__()
           self.clicked.connect(self._on_click)

       def _on_click(self):
           self.run_requested.emit(self.text())
   ```

2. **Model/View Separation**: Custom Qt models for data binding

   ```python
   from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex

   class DataModel(QAbstractTableModel):
       """Separates data from UI."""

       def __init__(self, data: list[dict]) -> None:
           super().__init__()
           self._data = data

       def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
           return len(self._data)

       def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
           return len(self._data[0]) if self._data else 0

       def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
           if role == Qt.ItemDataRole.DisplayRole:
               return self._data[index.row()][index.column()]
           return None
   ```

3. **Threading for Blocking Operations**

   ```python
   from PyQt6.QtCore import QThread, pyqtSignal

   class WorkerThread(QThread):
       finished = pyqtSignal(object)
       error = pyqtSignal(str)
       progress = pyqtSignal(int)

       def __init__(self, work_fn: Callable[[], Any]) -> None:
           super().__init__()
           self.work_fn = work_fn

       def run(self) -> None:
           try:
               result = self.work_fn()
               self.finished.emit(result)
           except Exception as e:
               self.error.emit(str(e))

   # Usage
   thread = WorkerThread(lambda: expensive_computation())
   thread.finished.connect(on_done)
   thread.error.connect(on_error)
   thread.start()
   ```

4. **Slot Type Checking**: Verify signals match slots

   ```python
   from PyQt6.QtCore import Qt

   # Set connection type to catch type mismatches early
   self.button.clicked.connect(
       self.on_button_clicked,
       type=Qt.ConnectionType.DirectConnection  # Debug mode
   )
   ```

5. **Resource Cleanup**: Always clean up resources
   ```python
   def closeEvent(self, event: QCloseEvent) -> None:
       """Save state and cleanup before close."""
       # Save settings
       QSettings("N4IDE", "N4IDE").setValue("geometry", self.saveGeometry())

       # Stop threads
       if self.worker_thread.isRunning():
           self.worker_thread.quit()
           self.worker_thread.wait()

       # Disconnect signals
       self.app.state_changed.disconnect()

       super().closeEvent(event)
   ```

### Architecture Principles

1. **Dependency Injection**: Components receive dependencies via constructor

   ```python
   # ❌ WRONG: Hard-coded dependency
   class Controller:
       def __init__(self):
           self.executor = CodeExecutor()  # Tightly coupled

   # ✅ CORRECT: Injected dependency
   class Controller:
       def __init__(self, executor: CodeExecutor, app: Application):
           self.executor = executor
           self.app = app
   ```

2. **Single Responsibility**: Each class does one thing

   ```python
   # ❌ WRONG: Multiple responsibilities
   class EditorWidget(QWidget):
       def execute_code(self): pass
       def render_graph(self): pass
       def save_file(self): pass

   # ✅ CORRECT: Separated concerns
   class EditorWidget(QWidget):
       run_requested = pyqtSignal(str)  # Only emits signals

   class EditorController:
       def run_code(self, code: str): pass  # Handles execution

   class FileManager:
       def save_file(self, path: str, content: str): pass  # Handles I/O
   ```

3. **Immutable Signal Data**: Signals carry immutable data

   ```python
   # ❌ WRONG: Mutable data passed through signal
   model_data = {"name": "Model"}
   signal.emit(model_data)
   model_data["name"] = "Modified"  # Receiver sees modified data!

   # ✅ CORRECT: Use frozen dataclass
   @dataclass(frozen=True)
   class ModelData:
       name: str

   signal.emit(ModelData(name="Model"))
   ```

4. **Composition Over Inheritance**: Prefer composition

   ```python
   # ❌ WRONG: Deep inheritance hierarchy
   class BaseWidget(QWidget): pass
   class EditableWidget(BaseWidget): pass
   class ValidatedWidget(EditableWidget): pass

   # ✅ CORRECT: Composition
   class Widget(QWidget):
       def __init__(self, editor: Editor, validator: Validator):
           self.editor = editor
           self.validator = validator
   ```

---

## Data Flow & Signal Architecture

### Typical User Workflow

```
User edits code in EditorWidget
         ↓
User clicks "Run" button
         ↓
EditorWidget.run_requested.emit(code)
         ↓
MainWindow connects signal to EditorController.run_code()
         ↓
EditorController spawns CodeExecutionThread
         ↓
Thread executes code in isolated namespace
         ↓
Thread emits finished(ExecutionResult)
         ↓
EditorController receives result
         ↓
If successful:
  - Extract model from result.namespace
  - Build computation graph
  - Update Application state
  - Application.model_loaded.emit(model)
         ↓
MainWindow listens to Application signals:
  - model_loaded → GraphView.set_graph()
  - model_loaded → WeightsTable.set_model()
  - output_received → ConsoleWidget.append_text()
         ↓
UI updates reflect new state
```

### Signal Flow Rules

1. **UI → Controller**: Signals for user actions

   ```python
   class EditorWidget(QWidget):
       run_requested = pyqtSignal(str)  # Passes code to controller
   ```

2. **Controller → Application**: Updates to central state

   ```python
   self.app.set_model(model)  # State change
   # Internally emits: Application.model_loaded
   ```

3. **Application → UI**: UI observes application state

   ```python
   self.app.model_loaded.connect(self.graph.set_graph)
   self.app.output_received.connect(self.console.append_text)
   ```

4. **No Direct Widget Access**: Never store references between widgets

   ```python
   # ❌ WRONG
   class EditorWidget:
       def __init__(self, graph_view):
           self.graph_view = graph_view  # Direct coupling

       def run(self):
           result = execute()
           self.graph_view.set_graph(result)  # Tight coupling

   # ✅ CORRECT
   class EditorWidget:
       run_requested = pyqtSignal(object)  # Emit signal

   # In MainWindow
   self.editor.run_requested.connect(self.controller.run_code)
   self.app.model_loaded.connect(self.graph.set_graph)
   ```

---

## Common Implementation Patterns

### Pattern 1: Adding a New Visualization Widget

Goal: Create a new widget showing model statistics

```python
# Step 1: Define data model (immutable)
from dataclasses import dataclass

@dataclass(frozen=True)
class ModelStats:
    """Immutable statistics snapshot."""
    layer_count: int
    total_parameters: int
    total_gradient_norm: float
    memory_usage_mb: float

# Step 2: Create widget with signal-only interface
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal

class StatsWidget(QWidget):
    """Display model statistics."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel("No model loaded")
        layout.addWidget(self.label)

    def set_stats(self, stats: ModelStats) -> None:
        """Update display with new statistics."""
        text = f"""
        Layers: {stats.layer_count}
        Parameters: {stats.total_parameters:,}
        Gradient Norm: {stats.total_gradient_norm:.4f}
        Memory: {stats.memory_usage_mb:.2f} MB
        """
        self.label.setText(text)

# Step 3: Update Application to compute and emit stats
class Application(QObject):
    stats_updated = pyqtSignal(ModelStats)

    def set_model(self, model: Model) -> None:
        """Update model and compute stats."""
        self._model = model
        stats = self._compute_stats(model)
        self.stats_updated.emit(stats)

    def _compute_stats(self, model: Model) -> ModelStats:
        """Extract statistics from model."""
        params = model.parameters()
        return ModelStats(
            layer_count=len(model.layers),
            total_parameters=sum(p.size for p in params),
            total_gradient_norm=0.0,  # TODO: compute
            memory_usage_mb=0.0,  # TODO: compute
        )

# Step 4: Connect in MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        # ... existing code ...
        self.stats = StatsWidget()
        bottom_tabs.addTab(self.stats, "Stats")

        # Connect signal
        self.app.stats_updated.connect(self.stats.set_stats)
```

### Pattern 2: Adding Code Execution Features

Goal: Add code profiling during execution

```python
# Step 1: Extend ExecutionResult dataclass
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    success: bool
    namespace: dict[str, Any]
    output: str
    error_message: Optional[str] = None
    execution_time: float = 0.0
    profile_data: Optional[dict] = None  # NEW

# Step 2: Use cProfile in executor
import cProfile
import pstats
from io import StringIO

class CodeExecutor:
    def execute(
        self,
        code: str,
        profile: bool = False,
    ) -> ExecutionResult:
        """Execute code with optional profiling."""
        namespace = self.BUILTIN_NAMESPACE.copy()

        if profile:
            profiler = cProfile.Profile()
            profiler.enable()

        try:
            exec(code, namespace)

            if profile:
                profiler.disable()
                profile_data = self._get_profile_stats(profiler)
            else:
                profile_data = None

            return ExecutionResult(
                success=True,
                namespace=namespace,
                output=output_buffer.getvalue(),
                profile_data=profile_data,
            )

        except Exception as e:
            if profile:
                profiler.disable()
            # ... error handling

    def _get_profile_stats(self, profiler: cProfile.Profile) -> dict:
        """Extract profiling statistics."""
        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        return {"stats": s.getvalue()}

# Step 3: Display profile in console
class EditorController:
    def _on_execution_finished(self, result: ExecutionResult) -> None:
        if result.profile_data:
            self.app.append_output("\n--- Profiling Results ---\n")
            self.app.append_output(result.profile_data["stats"])
```

### Pattern 3: State Persistence

Goal: Save and restore IDE state

```python
from PyQt6.QtCore import QSettings
import json

class Application(QObject):
    """Enhanced with persistence."""

    def save_state(self) -> None:
        """Save application state to disk."""
        settings = QSettings("N4IDE", "N4IDE")

        # Save recent files
        if hasattr(self, '_recent_files'):
            settings.setValue("recent_files", json.dumps(self._recent_files))

        # Save window state saved in MainWindow.closeEvent

    def load_state(self) -> None:
        """Restore application state from disk."""
        settings = QSettings("N4IDE", "N4IDE")

        recent = settings.value("recent_files", "[]")
        self._recent_files = json.loads(recent)

class MainWindow(QMainWindow):
    def __init__(self):
        # ... existing code ...
        self.app.load_state()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Save state before closing."""
        self.app.save_state()

        settings = QSettings("N4IDE", "N4IDE")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        super().closeEvent(event)
```

### Pattern 4: Custom Model Inspector

Goal: Extract typed information from n4 models

```python
from typing import TypeVar, Generic
from n4.nn import Sequential, Model, DenseLayer

T = TypeVar('T')  # Numeric backend type

@dataclass
class LayerInfo:
    """Typed information about a layer."""
    layer_type: str
    parameters: list[tuple[str, tuple[int, ...]]]  # (name, shape)
    activation: Optional[str]
    input_shape: Optional[tuple[int, ...]]
    output_shape: Optional[tuple[int, ...]]

class ModelInspector:
    """Extract typed information from models."""

    def inspect_layers(self, model: Model) -> list[LayerInfo]:
        """Get layer information."""
        layers = []

        if isinstance(model, Sequential):
            for i, layer in enumerate(model.layers):
                layers.append(self._inspect_layer(layer, i))

        return layers

    def _inspect_layer(self, layer: DenseLayer, index: int) -> LayerInfo:
        """Extract info from single layer."""
        params = layer.parameters()

        return LayerInfo(
            layer_type=type(layer).__name__,
            parameters=[],  # TODO: extract from layer
            activation=getattr(layer, 'activation', None),
            input_shape=None,  # TODO: infer from forward
            output_shape=None,  # TODO: infer from forward
        )
```

---

## Testing Strategy

### Unit Testing

Test business logic in isolation without PyQt6:

```python
# tests/domain/test_executor.py
from ide.domain.executor import CodeExecutor, ExecutionResult

def test_successful_execution():
    """Code execution succeeds with valid code."""
    executor = CodeExecutor()

    result = executor.execute("x = 1 + 1")

    assert result.success
    assert result.namespace["x"] == 2
    assert result.error_message is None

def test_execution_error():
    """Execution error captured."""
    executor = CodeExecutor()

    result = executor.execute("raise ValueError('test')")

    assert not result.success
    assert "ValueError" in result.error_message

def test_n4_imports_available():
    """n4 library symbols available in namespace."""
    executor = CodeExecutor()

    result = executor.execute("model = Sequential()")

    assert result.success
    assert result.namespace["model"] is not None
```

### Integration Testing

Test signal/slot connections and full workflows:

```python
# tests/ui/test_editor_integration.py
from PyQt6.QtCore import QSignalSpy
from ide.ui.main_window import MainWindow
from ide.domain.executor import CodeExecutor

def test_run_button_triggers_execution(qtbot):
    """Clicking run button emits signal with code."""
    window = MainWindow()
    qtbot.addWidget(window)

    spy = QSignalSpy(window.editor.run_requested)

    window.editor.editor.setText("x = 1")
    window.editor._on_run()

    assert len(spy) == 1
    assert spy[0][0] == "x = 1"

def test_execution_updates_console(qtbot):
    """Execution output appears in console."""
    window = MainWindow()
    qtbot.addWidget(window)

    code = "print('Hello, world!')"
    window.editor_controller.run_code(code)

    qtbot.wait(500)  # Wait for thread

    assert "Hello, world!" in window.console.text_edit.toPlainText()
```

### Performance Testing

Profile long-running operations:

```python
# tests/performance/test_graph_rendering.py
import time
from ide.domain.graph import ComputationGraphBuilder, GraphNode, GraphEdge

def test_graph_rendering_performance():
    """Large graph renders within acceptable time."""
    # Create large graph
    graph = ComputationGraph(
        nodes={f"node_{i}": GraphNode(...) for i in range(10000)},
        edges=[GraphEdge(...) for _ in range(20000)],
    )

    start = time.time()
    window = GraphView()
    window.set_graph(graph)
    elapsed = time.time() - start

    assert elapsed < 1.0, f"Rendering took {elapsed}s (should be <1s)"
```

---

## Code Quality Tools

Configure project for production-grade code quality:

```bash
# pyproject.toml additions
[tool.mypy]
python_version = "3.13"
strict = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "W", "C", "I", "UP"]

[tool.pytest.ini_options]
addopts = "--strict-markers -v"
testpaths = ["tests"]
```

Run checks before committing:

```bash
# Type checking
mypy ide/

# Linting
ruff check ide/

# Tests with coverage
pytest --cov=ide tests/
```

---

## Performance Optimization

### Thread Management

**Never block the main thread:**

```python
# ❌ WRONG: Blocks main thread
def on_run_clicked():
    code = editor.get_code()
    result = executor.execute(code)  # Freezes UI!
    update_ui(result)

# ✅ CORRECT: Execute in worker thread
def on_run_clicked():
    thread = CodeExecutionThread(code, executor)
    thread.finished.connect(self._on_execution_finished)
    thread.start()  # Runs in background
```

### Graph Rendering

**Optimize large computation graphs:**

```python
class GraphView(QGraphicsView):
    def set_graph(self, graph: ComputationGraph) -> None:
        """Render only visible portion of graph."""
        self.scene.clear()

        # Viewport-based rendering
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        for node_id, node in graph.nodes.items():
            # Only render nodes in or near viewport
            if self._is_visible(node, visible_rect):
                self.scene.addItem(GraphNodeItem(node, ...))

    def _is_visible(self, node: GraphNode, visible_rect: QRectF) -> bool:
        """Check if node should be rendered."""
        margin = 100  # Render slightly outside viewport
        return True  # TODO: implement bounds check
```

### Memory Management

**Clean up resources properly:**

```python
class Application(QObject):
    def set_model(self, model: Model) -> None:
        """Replace old model with new one."""
        # Clear old model
        if hasattr(self, '_model') and self._model is not None:
            # Disconnect any signals
            # Release large allocations
            del self._model

        # Set new model
        self._model = model
        self.model_loaded.emit(model)

    def __del__(self) -> None:
        """Cleanup on application exit."""
        if hasattr(self, '_model'):
            del self._model
```

### Signal Optimization

**Batch rapid updates:**

```python
from PyQt6.QtCore import QTimer

class Application(QObject):
    output_received = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._output_buffer: list[str] = []

        # Emit accumulated output every 100ms instead of per line
        self._flush_timer = QTimer()
        self._flush_timer.timeout.connect(self._flush_output)
        self._flush_timer.start(100)

    def append_output(self, text: str) -> None:
        """Buffer output, not immediate signal."""
        self._output_buffer.append(text)

    def _flush_output(self) -> None:
        """Emit accumulated output."""
        if self._output_buffer:
            combined = "\n".join(self._output_buffer)
            self.output_received.emit(combined)
            self._output_buffer.clear()
```

### QSS Stylesheet Management

**Always use absolute paths for stylesheet loading:**

```python
from pathlib import Path

class StyledComponent(QWidget):
    """Компонент с автоматической загрузкой QSS-стилей."""

    def __init__(self, parent: Optional[QWidget] = None, stylesheet_name: Optional[str] = None) -> None:
        super().__init__(parent)

        # ❌ WRONG: Relative paths break when cwd changes
        # path = Path(f"ide/styles/components/{stylesheet_name}")

        # ✅ CORRECT: Use __file__ to build absolute path
        if stylesheet_name:
            ide_root = Path(__file__).parent.parent  # Navigate to ide/
            stylesheet_path = ide_root / "styles" / "components" / stylesheet_name
            self._load_stylesheet(stylesheet_path)

    def _load_stylesheet(self, path: Path) -> None:
        """Загрузить и применить стиль с обработкой ошибок."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Предупреждение: Файл стиля не найден: {path}")
```

**Best practices for QSS styling:**

- Use `setObjectName()` for CSS selectors in QSS files
- Load stylesheets once in `__init__`, not on every method call
- Use CSS pseudo-classes: `:hover`, `:pressed`, `:focus`, `:disabled`
- Use margins/padding in QSS, not `setContentsMargins()` when styling is needed
- Avoid hardcoded colors; use CSS variables or a theme system
- Test stylesheets with simple test case before deploying

---

## Troubleshooting Common Issues

### Issue: Signal/Slot Connection Not Working

**Symptoms**: Slot never called when signal emitted

**Debugging**:

```python
# Check signal connection
button.clicked.connect(self.on_click)
# Verify with QSignalSpy
spy = QSignalSpy(button.clicked)
button.click()
assert len(spy) > 0, "Signal not emitted"

# Ensure slot is spelled correctly (typos are silent)
# Ensure object lifetimes (don't connect to deleted objects)
```

### Issue: Code Execution Thread Doesn't Finish

**Symptoms**: Thread hangs indefinitely

**Debugging**:

```python
# Add debug output
class CodeExecutionThread(QThread):
    def run(self) -> None:
        print(f"Thread {self.objectName()} started")
        result = self.executor.execute(self.code)
        print(f"Thread {self.objectName()} finished")
        self.finished.emit(result)

# Check for infinite loops or blocking I/O in user code
# Add timeout to thread
timer = QTimer()
timer.timeout.connect(lambda: thread.terminate())
timer.start(60000)  # 60 second timeout
```

### Issue: Graph Visualization Not Updating

**Symptoms**: Graph doesn't reflect new model

**Debugging**:

```python
# Verify signal is emitted
self.app.model_loaded.connect(
    lambda m: print(f"Model loaded signal received: {m}")
)

# Verify slot receives data
def set_graph(self, graph: ComputationGraph) -> None:
    print(f"set_graph called with {len(graph.nodes)} nodes")
    self.scene.clear()  # Ensure scene is cleared

# Check scene bounds
self.scene.setSceneRect(self.scene.itemsBoundingRect())
```

### Issue: Output Truncated or Missing

**Symptoms**: Console doesn't show all program output

**Debugging**:

```python
# Verify output capture is active
old_stdout = sys.stdout
sys.stdout = StringIO()

# Flush output buffer
sys.stdout.flush()

# Check for unbuffered stderr
code = "import sys; sys.stderr.write('test')"
```

### Issue: Type Errors with n4 Backend

**Symptoms**: "Cannot perform operation on different backends" error

**Solution**: Ensure all Tensors/Values use same backend:

```python
# ❌ WRONG: Mixing backends
v1 = Value.from_float(1.0, PyFloat)
v2 = Value.from_float(2.0, MyBackend)
v3 = v1 + v2  # TypeError!

# ✅ CORRECT: Same backend
v1 = Value.from_float(1.0, PyFloat)
v2 = Value.from_float(2.0, PyFloat)
v3 = v1 + v2  # Works

# In execution namespace, ensure consistent backend
executor.BUILTIN_NAMESPACE["PyFloat"] = PyFloat
# All created values will use PyFloat
```
