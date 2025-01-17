from dataclasses import dataclass
import inspect

from keras import layers



@dataclass(init=False, repr=False)
class Layer:
    '''
    Класс хранящий данные, для связи нода с слоём нейроной сети.
    '''
    nnlayer: layers.Layer
    annotations: dict[str: type]
    docs: str


    def __init__(self, layer: layers.Layer, annotations: dict[str: type], docs: str = None):
        self.nnlayer = layer
        self.annotations = annotations
        if not docs: docs = inspect.getdoc(layer)
        self.docs = docs


    def __repr__(self):
        return self.nnlayer.__name__
