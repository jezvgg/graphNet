from enum import Enum


class Padding(Enum):
    """
    Enum для типов padding в Keras слоях
    """
    VALID = "valid"
    SAME = "same"