from enum import Enum

class TextOutputMode(Enum):
    INT = "int"
    MULTI_HOT = "multi_hot"
    COUNT = "count"
    TF_IDF = "tf_idf"