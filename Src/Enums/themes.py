from enum import StrEnum

class Themes(StrEnum):
    '''
    Enum для тем в приложении
    '''
    # Global
    DEFAULT = "default"
    ERROR = "error"

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