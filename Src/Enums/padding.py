from enum import Enum


class Padding(Enum):
    """
    Enum для типов padding в Keras слоях
    """
    valid = "valid"
    same = "same"