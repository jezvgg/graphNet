from enum import StrEnum

class Themes(StrEnum):
    '''
    Enum для тем в приложении
    '''
    # Node editor
    DEFAULT = "default"
    ERROR = "error"

    # Nodes
    ABSTRACT = "abstract"
    COMPILE = "compile"
    DATA = "data"
    FIT = "fit"
    LAYER = "layer"
    METRIC = "metric"
    PREDICT = "predict"
    SHAPE = "shape"
    UTILS = "utils"
    TABLE_DATA = "table_data"
    IMAGE_DATA = "image_data"