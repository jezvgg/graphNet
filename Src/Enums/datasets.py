from enum import Enum


class Datasets(Enum):
    """
    Enum выбора возможных датасетов в Keras
    """
    boston_housing = "boston_housing"
    california_housing = "california_housing"
    cifar10 = "cifar10"
    cifar100 = "cifar100"
    fashion_mnist = "fashion_mnist"
    imdb = "imdb"
    mnist = "mnist"
    reuters = "reuters"
