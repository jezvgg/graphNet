from enum import Enum


class Losses(Enum):
    """
    Enum для функций потерь в Keras
    """
    mean_squared_error = "mean_squared_error"
    mean_absolute_error = "mean_absolute_error"
    mean_absolute_percentage_error = "mean_absolute_percentage_error"
    mean_squared_logarithmic_error = "mean_squared_logarithmic_error"
    squared_hinge = "squared_hinge"
    hinge = "hinge"
    categorical_hinge = "categorical_hinge"
    logcosh = "logcosh"
    huber = "huber"
    categorical_crossentropy = "categorical_crossentropy"
    sparse_categorical_crossentropy = "sparse_categorical_crossentropy"
    binary_crossentropy = "binary_crossentropy"
    kullback_leibler_divergence = "kullback_leibler_divergence"
    poisson = "poisson"
    cosine_similarity = "cosine_similarity"