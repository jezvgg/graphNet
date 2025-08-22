import keras

from Src.Nodes import AbstractNode



class PredictNode(AbstractNode):
    logic: keras.models.Model.predict


    @staticmethod
    def predict(model: keras.models.Model, **kwargs):
        return model.predict(**kwargs, verbose=False)
