class TwirlBordersModel(Model[PyFloat]):
    """
    Модель для разделения двух спиралей.
    Требует глубокой архитектуры с нелинейностями (Tanh).
    """

    def __init__(
        self, input_dim: int = 2, hidden_dims: list[int] = [32, 64, 32]
    ) -> None:
        self.backend = PyFloat
        layers = []
        prev_dim = input_dim
        for hdim in hidden_dims:
            layers.append(DenseLayer(prev_dim, hdim, self.backend, activation=Tanh))
            prev_dim = hdim
        layers.append(DenseLayer(prev_dim, 2, self.backend, activation=NonOp))
        layers.append(SoftmaxLayer(self.backend))
        self.model = Sequential(*layers)

    def forward_pass(self, x: Tensor[PyFloat]) -> Tensor[PyFloat]:
        return self.model.forward_pass(x)

    def parameters(self):
        return self.model.parameters()
