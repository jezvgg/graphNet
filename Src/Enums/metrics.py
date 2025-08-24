from enum import Enum




class Metrics(Enum):
    """
    Enum for metrics in Keras
    """
    ACCURACY = "accuracy"
    MEAN_SQUARED_ERROR = "mean_squared_error"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    PRECISION = "precision"
    RECALL = "recall"
    AUC = "auc"
    BINARY_ACCURACY = "binary_accuracy"
    CATEGORICAL_ACCURACY = "categorical_accuracy"
    SPARSE_CATEGORICAL_ACCURACY = "sparse_categorical_accuracy"
    COSINE_SIMILARITY = "cosine_similarity"