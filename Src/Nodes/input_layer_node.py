from keras import layers

from Src.Nodes import LayerNode, LayerResult



class InputLayerNode(LayerNode):
    '''
    Класс для связи данных и нейронной сети, реализует логику keras.Input.
    '''
    OUTPUT: LayerResult
    color = (231, 231, 21, 255)


    @staticmethod
    def create_input(*args, **kwargs) -> LayerResult:
        input_layer = layers.Input(**kwargs)
        return LayerResult(input_layer, set([input_layer]))
        