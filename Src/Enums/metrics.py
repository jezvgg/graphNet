from enum import Enum




class Metrics(Enum):
    """
    Enum for metrics in Keras
    """
    ACCURACY = "accuracy"
    MEAN_SQUARED_ERROR = "mean_squared_error"
    MEAN_SQUERED_LOGARITHMIC_ERROR = "mean_squared_logarithmic_error"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    MEAN_PERCENTAGE_ABSOLUTE_ERROR = "mean_absolute_percentage_error"
    PRECISION = "precision"
    RECALL = "recall"
    AUC = "auc"
    BINARY_ACCURACY = "binary_accuracy"
    CATEGORICAL_ACCURACY = "categorical_accuracy"
    SPARSE_CATEGORICAL_ACCURACY = "sparse_categorical_accuracy"
    COSINE_SIMILARITY = "cosine_similarity"
    HINGE = "hinge"
    CATEGORICAL_HINGE = "categorical_hinge"
    PEARSON_CORRELATION = "pearson_correlation"
    SPARCE_TOPK_CATEGORICAL_ACCURACY = "sparse_top_k_categorical_accuracy"
    TOPK_CATEGORICAL_ACCURACY = 'top_k_categorical_accuracy'