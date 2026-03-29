from enum import Enum


class Callbacks(Enum):
    """
    Enum для Callback'ов при обучении
    """
    EARLY_STOPPING = "EarlyStopping"
    REDUCE_LRO_ON_PLATEAU = "ReduceLROnPlateau"
