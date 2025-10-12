from keras import layers

from Src.Enums import Themes
from Src.Nodes import LayerNode, LayerResult



class InputLayerNode(LayerNode):
    '''
    Класс для связи данных и нейронной сети, реализует логику keras.Input.
    '''
    OUTPUT: LayerResult
    theme_name: Themes = Themes.LAYER


    @staticmethod
    def create_input(*args, **kwargs) -> LayerResult:
        input_layer = layers.Input(**kwargs)
        return LayerResult(input_layer, set([input_layer]))
        