from enum import Enum


class ColorMode(Enum):
    """
    Enum для режимов цвета при загрузке изображений
    """
    GRAYSCALE = "grayscale"
    RGB = "rgb"
    RGBA = "rgba"