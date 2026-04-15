class ImprovedXORModel(Model[PyFloat]):
    """
    Улучшенная модель для XOR.
    - Два скрытых слоя с Tanh активацией (лучше подходит для центрированных данных).
    - Достаточная ширина для формирования нелинейной границы.
    """

    def __init__(self, input_dim: int = 2, hidden_dim: int = 16) -> None:
        self.backend = PyFloat
        self.model = Sequential(
            DenseLayer(input_dim, hidden_dim, self.backend, activation=Tanh),
            DenseLayer(hidden_dim, hidden_dim, self.backend, activation=Tanh),
            DenseLayer(hidden_dim, 2, self.backend, activation=NonOp),
            SoftmaxLayer(self.backend),
        )

    def forward_pass(self, x: Tensor[PyFloat]) -> Tensor[PyFloat]:
        return self.model.forward_pass(x)

    def parameters(self):
        return self.model.parameters()