# n4 Library Usage Guide

n4 is a minimalist autograd neural network framework written in Python, inspired by PyTorch. This guide covers imports, core concepts, and how to use the library for building and training neural networks.

## Table of Contents

1. [Library Philosophy](#library-philosophy)
2. [Core Architecture](#core-architecture)
3. [Imports & Module Organization](#imports--module-organization)
4. [Numeric Backends](#numeric-backends)
5. [Value & Autograd](#value--autograd)
6. [Tensors](#tensors)
7. [Neural Network Layers](#neural-network-layers)
8. [Models & Sequential](#models--sequential)
9. [Loss Functions](#loss-functions)
10. [Optimization](#optimization)
11. [Quick Reference Examples](#quick-reference-examples)

---

## Library Philosophy

### Generics & Type Safety

n4 enforces **strict generic typing** throughout. Every Value, Tensor, Layer, and Model is parametrized by a numeric backend type `T` that conforms to `NumericProtocol`. This design ensures:

- **No implicit type promotion**: You must keep all Values/Tensors on the same backend. Mixing backends raises a `TypeError`.
- **Backend explicitness**: Backends are passed explicitly (e.g., `Tensor.zeros((3, 4), backend=PyFloat)`). This makes it clear which numeric type is used.
- **Type preservation**: The framework preserves type information through all operations, enabling static type checking via mypy.

### Backend Independence

The framework is not tied to a single numeric implementation. By implementing `NumericProtocol`, you can support different numeric types (e.g., `PyFloat` for standard Python floats, custom fixed-point or decimal types).

### Immutability-Like Pattern

Tensor and Layer operations are designed to avoid mutation:

- Tensor arithmetic returns **new Tensor objects** (not in-place modifications).
- Layer parameters are stored in Tensor/Value objects and managed by layers/models.
- Use `layer.zero_grad()` to reset gradients before a training iteration.

---

## Core Architecture

### Computation Graph

n4 builds a **dynamic computation graph**:

1. **Value**: Represents a scalar with `data` (numeric value), `grad` (accumulated gradient), and `parent_op` (operation that created it).
2. **Op**: Abstract base class for operations (e.g., Add, Mul, Relu). Each Op implements `forward_pass()` and `backward_pass()`.
3. **Tensor**: n-dimensional array of Values with broadcasting support. Operations on Tensors perform elementwise Value operations.

### Backward Pass

Call `value.backward()` to compute gradients:

- Sets the root Value's grad to 1.
- Traverses the computation graph via BFS.
- Each Op's `backward_pass()` accumulates gradients into its inputs.

---

## Imports & Module Organization

### Top-Level Imports

```python
from n4.core import Value, Op
from n4.tensor import Tensor
from n4.numeric import PyFloat, NumericProtocol
from n4.nn import (
    DenseLayer, ConvLayer, SoftmaxLayer, TanhLayer,
    Sequential, Model
)
from n4.nn.loss import MSELoss, CrossEntropyLoss
from n4.optim import SGD
from n4.op import Add, Mul, Div, Sub, Pow, Exp, Log, Relu, Tanh, Neg, NonOp
```

### Module Organization

| Module | Purpose |
|--------|---------|
| `n4.core` | Value, Op, and computation graph |
| `n4.numeric` | NumericProtocol and backends (PyFloat) |
| `n4.tensor` | Tensor class with broadcasting |
| `n4.nn` | Layers (DenseLayer, etc.), Sequential, Model base class |
| `n4.nn.loss` | Loss functions (MSELoss, CrossEntropyLoss) |
| `n4.op` | Operations (Add, Mul, Relu, etc.) |
| `n4.optim` | Optimizers (SGD) |

---

## Numeric Backends

### PyFloat

The default numeric backend wrapping Python's `float`:

```python
from n4.numeric import PyFloat

# Create a Value with PyFloat backend
val = Value.from_float(3.14, PyFloat)
```

### NumericProtocol

Implement this to support custom numeric types:

```python
from n4.numeric import NumericProtocol

class MyNumeric(NumericProtocol):
    @classmethod
    def from_float(cls, f: float) -> Self: ...
    
    @classmethod
    def random_uniform(cls, start: float, end: float) -> Self: ...
    
    def __add__(self, other) -> Self: ...
    def __sub__(self, other) -> Self: ...
    def __mul__(self, other) -> Self: ...
    def __truediv__(self, other) -> Self: ...
    def __pow__(self, other) -> Self: ...
    def __neg__(self) -> Self: ...
    
    def exp(self) -> Self: ...
    def tanh(self) -> Self: ...
    def log(self) -> Self: ...
    # ... other required methods
```

---

## Value & Autograd

### Creating Values

```python
from n4.core import Value
from n4.numeric import PyFloat

# From float
v1 = Value.from_float(5.0, PyFloat)

# From int
v2 = Value.from_int(10, PyFloat)

# Directly (backend inferred from data type)
v3 = Value(PyFloat.from_float(2.5))
```

### Scalar Operations

Values support standard operators:

```python
a = Value.from_float(2.0, PyFloat)
b = Value.from_float(3.0, PyFloat)

c = a + b      # Add
d = a * b      # Mul
e = a - b      # Sub
f = a / b      # Div
g = a ** b     # Pow
h = -a         # Neg

# Activations
r = a.relu()   # ReLU
```

### Backward Pass

```python
a = Value.from_float(2.0, PyFloat)
b = Value.from_float(3.0, PyFloat)
c = a * b + a

c.backward()

print(c.grad)  # Gradient of c w.r.t. c (= 1.0)
print(a.grad)  # Gradient of c w.r.t. a
print(b.grad)  # Gradient of c w.r.t. b
```

### Zero Gradients

```python
value.zero_grad()  # Reset grad to 0
```

### Apply Custom Operations

```python
from n4.op import Exp

result = value.apply_activation(Exp)
```

---

## Tensors

### Creating Tensors

```python
from n4.tensor import Tensor
from n4.numeric import PyFloat

# From Value list and shape
values = [Value.from_float(float(i), PyFloat) for i in range(6)]
t1 = Tensor(values, shape=(2, 3))

# Zeros
t2 = Tensor.zeros((3, 4), backend=PyFloat)

# Ones
t3 = Tensor.ones((2, 5), backend=PyFloat)

# Random uniform
t4 = Tensor.random_uniform((2, 3), backend=PyFloat, low=-1.0, high=1.0)
```

### Properties

```python
t = Tensor.zeros((3, 4), backend=PyFloat)

print(t.shape)      # (3, 4)
print(t.ndim)       # 2 (number of dimensions)
print(t.size)       # 12 (total elements)
print(t.backend)    # PyFloat
```

### Indexing & Slicing

```python
t = Tensor.random_uniform((3, 4), backend=PyFloat)

# Access scalar (full index)
scalar_value = t[0, 1]  # returns Value

# Slice (partial index)
row = t[0]      # returns Tensor with shape (4,)
```

### Reshape

```python
t = Tensor.random_uniform((12,), backend=PyFloat)
t_reshaped = t.reshape((3, 4))
```

### Elementwise Operations

```python
t1 = Tensor.random_uniform((2, 3), backend=PyFloat)
t2 = Tensor.random_uniform((2, 3), backend=PyFloat)

# Elementwise operations
t_sum = t1 + t2
t_diff = t1 - t2
t_prod = t1 * t2
t_div = t1 / t2
t_neg = -t1

# With broadcasting
v = Value.from_float(2.0, PyFloat)
t_scaled = t1 + v
```

### Broadcasting

Tensors automatically broadcast to compatible shapes:

```python
t1 = Tensor.random_uniform((1, 4), backend=PyFloat)
t2 = Tensor.random_uniform((3, 1, 4), backend=PyFloat)

# Broadcasts t1 to (1, 1, 4), then to (3, 1, 4)
result = t1 + t2  # shape (3, 1, 4)
```

### Matrix Operations

```python
# Matrix multiplication (2D only)
t1 = Tensor.random_uniform((3, 4), backend=PyFloat)
t2 = Tensor.random_uniform((4, 5), backend=PyFloat)
result = t1 @ t2  # shape (3, 5)

# Transpose (2D only)
t_transposed = t1.Transposed  # shape (4, 3)
```

### Aggregations

```python
t = Tensor.random_uniform((3, 4), backend=PyFloat)

# Sum all elements
total = t.sum()  # returns Value

# Sum along dimension
row_sums = t.sum_dim(1)  # shape (3,)

# Mean all elements
avg = t.mean()  # returns Value

# Mean along dimension
row_means = t.mean_dim(1)  # shape (3,)
```

### Activations

```python
from n4.op import Relu, Tanh

t = Tensor.random_uniform((2, 3), backend=PyFloat)

# Apply activation to all elements
t_relu = t.apply_activation(Relu)
t_tanh = t.apply_activation(Tanh)
```

### Convert to List

```python
t = Tensor.random_uniform((2, 3), backend=PyFloat)
nested_list = t.to_list()  # List structure mirroring shape
```

---

## Neural Network Layers

All layers inherit from `Layer[T]` and require a backend parameter.

### DenseLayer (Fully Connected)

```python
from n4.nn import DenseLayer
from n4.op import Relu
from n4.numeric import PyFloat

layer = DenseLayer(
    in_features=10,
    out_features=20,
    backend=PyFloat,
    activation=Relu
)

# Forward pass
x = Tensor.random_uniform((batch_size, 10), backend=PyFloat)
output = layer(x)  # or layer.forward_pass(x)

# Get parameters (weights + bias)
params = layer.parameters()  # returns list[Value]
```

**Parameters:**
- `in_features`: Input size (matches last dimension of input Tensor)
- `out_features`: Output size (number of neurons)
- `backend`: Numeric backend type
- `activation`: Optional activation Op class (default: `NonOp` = identity)

### ConvLayer (2D Convolution)

```python
from n4.nn import ConvLayer
from n4.op import Relu
from n4.numeric import PyFloat

layer = ConvLayer(
    in_channels=3,
    out_channels=16,
    kernel_size=3,
    backend=PyFloat,
    stride=1,
    padding=1,
    activation=Relu
)

# Forward pass: expects (batch, channels, height, width)
x = Tensor.random_uniform((batch_size, 3, 32, 32), backend=PyFloat)
output = layer(x)

params = layer.parameters()
```

**Parameters:**
- `in_channels`: Number of input channels (e.g., 3 for RGB)
- `out_channels`: Number of output channels (filters)
- `kernel_size`: Size of convolution kernel
- `stride`: Stride of convolution
- `padding`: Padding applied to input
- `activation`: Optional activation Op

### SoftmaxLayer

```python
from n4.nn import SoftmaxLayer
from n4.numeric import PyFloat

layer = SoftmaxLayer(backend=PyFloat)

# Forward pass: softmax applied to last dimension
x = Tensor.random_uniform((batch_size, num_classes), backend=PyFloat)
output = layer(x)  # probabilities summing to 1 per sample

params = layer.parameters()  # returns []
```

### TanhLayer

```python
from n4.nn import TanhLayer
from n4.numeric import PyFloat

layer = TanhLayer(backend=PyFloat)

# Forward pass: tanh activation
x = Tensor.random_uniform((batch_size, features), backend=PyFloat)
output = layer(x)

params = layer.parameters()  # returns []
```

### Accessing Layer Parameters

```python
layer = DenseLayer(10, 20, backend=PyFloat, activation=Relu)

# Get all learnable parameters
params = layer.parameters()

# Zero all gradients
layer.zero_grad()
```

### Custom Activation

```python
from n4.op import NonOp

# No activation (identity)
layer = DenseLayer(10, 20, backend=PyFloat, activation=NonOp)
```

---

## Models & Sequential

### Sequential Container

Chains layers in sequence:

```python
from n4.nn import Sequential, DenseLayer
from n4.op import Relu, NonOp
from n4.numeric import PyFloat

model = Sequential(
    DenseLayer(10, 64, backend=PyFloat, activation=Relu),
    DenseLayer(64, 32, backend=PyFloat, activation=Relu),
    DenseLayer(32, 5, backend=PyFloat, activation=NonOp)
)

# Forward pass
x = Tensor.random_uniform((batch_size, 10), backend=PyFloat)
output = model(x)

# Get all parameters
all_params = model.parameters()

# Zero gradients
model.zero_grad()
```

**Requirements:**
- All layers must have the **same numeric backend**.
- At least one layer required.

### Custom Model

Subclass `Model[T]` to define custom architectures:

```python
from n4.nn import Model, Sequential, DenseLayer, SoftmaxLayer
from n4.op import Relu, NonOp
from n4.numeric import PyFloat
from n4.tensor import Tensor
from typing import Self

class MyClassifier(Model[PyFloat]):
    def __init__(self) -> None:
        super().__init__()
        self.model = Sequential(
            DenseLayer(784, 128, backend=PyFloat, activation=Relu),
            DenseLayer(128, 64, backend=PyFloat, activation=Relu),
            DenseLayer(64, 10, backend=PyFloat, activation=NonOp),
            SoftmaxLayer(backend=PyFloat)
        )
    
    def forward_pass(self, x: Tensor[PyFloat]) -> Tensor[PyFloat]:
        return self.model(x)

# Usage
model = MyClassifier()
x = Tensor.random_uniform((batch_size, 784), backend=PyFloat)
predictions = model.forward_pass(x)
```

---

## Loss Functions

### MSELoss (Mean Squared Error)

```python
from n4.nn.loss import MSELoss
from n4.numeric import PyFloat

loss_fn = MSELoss()

predictions = Tensor.random_uniform((batch_size, 10), backend=PyFloat)
targets = Tensor.random_uniform((batch_size, 10), backend=PyFloat)

loss = loss_fn(predictions, targets)  # returns Value
```

Formula: $\text{MSE} = \frac{1}{n} \sum (y_{\text{pred}} - y_{\text{target}})^2$

### CrossEntropyLoss

```python
from n4.nn.loss import CrossEntropyLoss
from n4.numeric import PyFloat

loss_fn = CrossEntropyLoss()

# predictions: output of SoftmaxLayer (probabilities)
predictions = Tensor.random_uniform((batch_size, num_classes), backend=PyFloat)

# targets: one-hot encoded
targets = Tensor.zeros((batch_size, num_classes), backend=PyFloat)
# ... set one element per sample to 1

loss = loss_fn(predictions, targets)  # returns Value
```

**Note:** Expects `predictions` to already be probabilities (e.g., from SoftmaxLayer).

### Computing Loss

```python
loss_value = loss_fn(pred, target)

# Get scalar value
scalar = loss_value.data  # or access loss_value.grad after backward
```

---

## Optimization

### SGD (Stochastic Gradient Descent)

```python
from n4.optim import SGD
from n4.numeric import PyFloat

model = ...  # your model

# Create optimizer
optimizer = SGD(params=model.parameters(), lr=0.001)

# Training loop
for epoch in range(num_epochs):
    for batch_x, batch_y in dataloader:
        # Forward pass
        output = model.forward_pass(batch_x)
        
        # Compute loss
        loss = loss_fn(output, batch_y)
        
        # Backward pass
        loss.backward()
        
        # Update parameters
        optimizer.step()
        
        # Reset gradients
        optimizer.zero_grad()
```

### SGD API

```python
# Initialize with model parameters
optimizer = SGD(model.parameters(), lr=0.01)

# Apply one optimization step
optimizer.step()  # param.data = param.data - lr * param.grad

# Zero gradients
optimizer.zero_grad()
```

**Parameters:**
- `params`: Iterable of Values to optimize
- `lr`: Learning rate (float)

### Manual Optimization

```python
# Without optimizer, manually update:
for param in model.parameters():
    param.data = param.data - learning_rate * param.grad
    param.zero_grad()
```

---

## Quick Reference Examples

### Example 1: Scalar Autograd

```python
from n4.core import Value
from n4.numeric import PyFloat

# Create values
a = Value.from_float(2.0, PyFloat)
b = Value.from_float(3.0, PyFloat)

# Build computation graph
c = a * b + a

# Backward pass
c.backward()

print(f"c = {c.data}")       # 8.0
print(f"dc/da = {a.grad}")   # 4.0
print(f"dc/db = {b.grad}")   # 2.0
```

### Example 2: Simple Regression

```python
from n4.tensor import Tensor
from n4.nn import DenseLayer
from n4.nn.loss import MSELoss
from n4.optim import SGD
from n4.numeric import PyFloat

# Data
X = Tensor.random_uniform((100, 5), backend=PyFloat)
y = Tensor.random_uniform((100, 1), backend=PyFloat)

# Model
model = DenseLayer(5, 1, backend=PyFloat, activation=None)
loss_fn = MSELoss()
optimizer = SGD(model.parameters(), lr=0.01)

# Training
for epoch in range(100):
    pred = model(X)
    loss = loss_fn(pred, y)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
    
    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.data}")
```

### Example 3: Multi-Layer Classifier

```python
from n4.nn import Sequential, DenseLayer, SoftmaxLayer
from n4.nn.loss import CrossEntropyLoss
from n4.optim import SGD
from n4.tensor import Tensor
from n4.op import Relu
from n4.numeric import PyFloat

# Model
model = Sequential(
    DenseLayer(784, 128, backend=PyFloat, activation=Relu),
    DenseLayer(128, 64, backend=PyFloat, activation=Relu),
    DenseLayer(64, 10, backend=PyFloat, activation=None),
    SoftmaxLayer(backend=PyFloat)
)

loss_fn = CrossEntropyLoss()
optimizer = SGD(model.parameters(), lr=0.01)

# Training (pseudo-code)
for epoch in range(10):
    model.zero_grad()
    
    # Forward pass
    logits = model(batch_X)  # batch_X shape: (batch_size, 784)
    
    # Compute loss
    loss = loss_fn(logits, batch_y_onehot)
    
    # Backward & update
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

### Example 4: Using Custom Numeric Backend

```python
from n4.core import Value
from n4.tensor import Tensor

class MyBackend:
    """Implement NumericProtocol methods..."""
    pass

# Create values/tensors with custom backend
v = Value.from_float(1.5, MyBackend)
t = Tensor.zeros((3, 4), backend=MyBackend)
```

---

## Common Patterns & Gotchas

### Backend Mismatch Error

```python
# ❌ This raises TypeError
v1 = Value.from_float(1.0, PyFloat)
v2 = Value.from_float(2.0, MyBackend)
v3 = v1 + v2  # TypeError: Cannot perform operation on different backends
```

### Layer Backend Consistency

```python
# ❌ This raises ValueError
model = Sequential(
    DenseLayer(10, 20, backend=PyFloat),
    DenseLayer(20, 10, backend=MyBackend)  # Mismatch!
)
```

### Shape Incompatibility

```python
# ❌ This raises ValueError
layer = DenseLayer(10, 20, backend=PyFloat)
x = Tensor.random_uniform((batch_size, 5), backend=PyFloat)  # Wrong size
output = layer(x)  # ValueError: Expected last dimension to be 10
```

### Forgetting to Zero Gradients

```python
# ⚠️ Gradients accumulate
for i in range(3):
    loss.backward()
    # gradients now = 2x, 3x the computed values!

# ✅ Correct pattern
for i in range(3):
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()  # Reset before next iteration
```

---

## Performance Notes

- n4 is a **pure Python framework** optimized for **clarity and correctness**, not speed.
- Forward passes build a dynamic computation graph; backward passes traverse it via BFS.
- No automatic batching or GPU support; everything runs on CPU.
- Suitable for **educational purposes, prototyping, and research** on small datasets.

---

## Summary

| Concept | Key Classes | Notes |
|---------|-------------|-------|
| **Values** | `Value[T]` | Scalar with grad and parent_op |
| **Operators** | `Op[T]` subclasses | Forward/backward pass; autodiff building blocks |
| **Tensors** | `Tensor[T]` | N-D array of Values; broadcasting support |
| **Layers** | `DenseLayer`, `ConvLayer`, `SoftmaxLayer`, `TanhLayer` | Learnable or fixed transformations |
| **Models** | `Sequential[T]`, `Model[T]` | Container for layers; custom architectures |
| **Loss** | `MSELoss`, `CrossEntropyLoss` | Output scalar Value for training |
| **Optimize** | `SGD[T]` | Parameter update via gradients |
| **Backend** | `PyFloat`, `NumericProtocol` | Numeric type for all Values |
