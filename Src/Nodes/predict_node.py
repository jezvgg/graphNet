import keras

from Src.Nodes import DataNode



# TODO: Переписать на SelfNode
class PredictNode(DataNode):
    color = (34, 255, 255, 255)
    logic: keras.models.Model.predict


    @staticmethod
    def predict(model: keras.models.Model, **kwargs):
        return model.predict(**kwargs, verbose=False)
