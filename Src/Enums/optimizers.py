from enum import Enum


class Optimizers(Enum):
    """
    Enum для оптимизаторов в Keras
    """
    sgd = "sgd"
    rmsprop = "rmsprop"
    adam = "adam"
    adadelta = "adadelta"
    adagrad = "adagrad"
    adamax = "adamax"
    nadam = "nadam"
    ftrl = "ftrl"
    adamw = "adamw"