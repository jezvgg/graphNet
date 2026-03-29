from enum import Enum


class Callbacks(Enum):
    """
    Enum для callback'ов при обучении
    """
    EARLY_STOPPING = "EarlyStopping"
    REDUCE_LRO_ON_PLATEAU = "ReduceLROnPlateau"
    TERMINATE_ON_NAN = "TerminateOnNaN"
    LOG2WINDOW = "Log2Window"
