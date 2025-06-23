from enum import Enum
import keras


class Metrics(Enum):
    """
    Enum для метрик в Keras
    """
    accuracy = ["accuracy"]
    binary_accuracy = ["binary_accuracy"]
    categorical_accuracy = ["categorical_accuracy"]
    sparse_categorical_accuracy = ["sparse_categorical_accuracy"]
    top_k_categorical_accuracy = ["top_k_categorical_accuracy"]
    sparse_top_k_categorical_accuracy = ["sparse_top_k_categorical_accuracy"]
    precision = ["precision"]
    recall = ["recall"]
    f1_score = ["f1_score"]
    auc = ["auc"]
    mean_squared_error = ["mean_squared_error"]
    root_mean_squared_error = ["root_mean_squared_error"]
    mean_absolute_error = ["mean_absolute_error"]
    mean_absolute_percentage_error = ["mean_absolute_percentage_error"]
    mean_squared_logarithmic_error = ["mean_squared_logarithmic_error"]
    cosine_similarity = ["cosine_similarity"]
    logcosh_error = ["logcosh"]
    kullback_leibler_divergence = ["kullback_leibler_divergence"]
    poisson = ["poisson"]
    hinge = ["hinge"]
    squared_hinge = ["squared_hinge"]
    categorical_hinge = ["categorical_hinge"]