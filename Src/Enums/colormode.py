from enum import Enum


class ColorMode(Enum):
    """
    Enum для режимов цвета при загрузке изображений
    """
    grayscale = "grayscale"
    rgb = "rgb"
    rgba = "rgba"