from enum import Enum


class Activations(Enum):
    """
    Enum для функций активации в Keras
    """
    linear = "linear"
    relu = "relu"
    sigmoid = "sigmoid"
    tanh = "tanh"
    softmax = "softmax"
    softplus = "softplus"
    softsign = "softsign"
    swish = "swish"
    gelu = "gelu"
    elu = "elu"
    selu = "selu"
    leaky_relu = "leaky_relu"
    prelu = "prelu"
    exponential = "exponential"
    hard_sigmoid = "hard_sigmoid"
    mish = "mish"