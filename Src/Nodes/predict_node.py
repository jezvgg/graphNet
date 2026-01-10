import keras

from Src.Enums import Themes
from Src.Nodes import DataNode



# TODO: Переписать на SelfNode
class PredictNode(DataNode):
    theme_name: Themes = Themes.PREDICT
    logic: keras.models.Model.predict


    @staticmethod
    def predict(model: keras.models.Model, **kwargs):
        return model.predict(**kwargs, verbose=False)
