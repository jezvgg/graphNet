from enum import Enum


class Datasets(Enum):
    """
    Enum выбора возможных датасетов в Keras
    """
    BOSTON_HOUSING = "boston_housing"
    CALIFORNIA_HOUSING = "california_housing"
    CIFAR10 = "cifar10"
    CIFAR100 = "cifar100"
    FASHION_MNIST = "fashion_mnist"
    IMBD = "imdb"
    MNIST = "mnist"
    REUTERS = "reuters"
