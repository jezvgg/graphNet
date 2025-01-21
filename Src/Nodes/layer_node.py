from keras import layers
from typing import Optional

from Src.Nodes import AbstractNode



class LayerNode(AbstractNode):
    '''
    Класс хранящий данные, для связи нода с слоём нейроной сети.
    '''
    # TODO Сделать геттер на layer, с проверкой что он заполнен и варнингом
    layer: Optional[layers.Layer]
    incoming: list["LayerNode"]
    outcoming: list["LayerNode"]


    def compile(self):
        self.layer: layers.Layer = super().compile()

        input_layers = [node.layer for node in self.incoming]
        if len(input_layers) == 1: input_layers = input_layers[0]

        return self.layer(input_layers)



