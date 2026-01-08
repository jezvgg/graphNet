from enum import Enum


class Optimizers(Enum):
    """
    Enum для оптимизаторов в Keras
    """
    SGD = "sgd"
    RMSPROP = "rmsprop"
    ADAM = "adam"
    ADADELTA = "adadelta"
    ADAGRAD = "adagrad"
    ADAMAX = "adamax"
    NADAM = "nadam"
    FTRL = "ftrl"
    ADAMW = "adamw"