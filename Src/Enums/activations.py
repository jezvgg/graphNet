from enum import Enum


class Activations(Enum):
    """
    Enum для функций активации в Keras
    """
    LINEAR = "linear"
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    SOFTMAX = "softmax"
    SOFTPLUS = "softplus"
    SOFTSIGN = "softsign"
    SWISH = "swish"
    GELU = "gelu"
    ELU = "elu"
    SELU = "selu"
    LEAKY_RELU = "leaky_relu"
    PRELU = "prelu"
    EXPONENTIONAL = "exponential"
    HARD_SIGMOID = "hard_sigmoid"
    MISH = "mish"