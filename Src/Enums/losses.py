from enum import Enum


class Losses(Enum):
    """
    Enum для функций потерь в Keras
    """
    MEAN_SQUARED_ERROR = "mean_squared_error"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    MEAN_ABSOKUTE_PERCENTAGE_ERROR = "mean_absolute_percentage_error"
    MEAN_SQUARED_LOGARITHMIC_ERROR = "mean_squared_logarithmic_error"
    SQUAREd_HINGE = "squared_hinge"
    HINGE = "hinge"
    CATEGORICAL_HINGE = "categorical_hinge"
    LOGCOSH = "logcosh"
    HUBER = "huber"
    CATEGORICAL_CROSSENTROPY = "categorical_crossentropy"
    SPARCE_CATEGORICAL_CROSSENTOPY = "sparse_categorical_crossentropy"
    BINARY_CROSSENTROPY = "binary_crossentropy"
    KULLBACK_LEIBLER_DIVERGENCE = "kullback_leibler_divergence"
    POISSON = "poisson"
    COSINE_SIMILARITY = "cosine_similarity"