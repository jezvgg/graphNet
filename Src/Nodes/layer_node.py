from keras import layers

from Src.Nodes import AbstractNode



class LayerNode(AbstractNode):
    '''
    Класс хранящий данные, для связи нода с слоём нейроной сети.
    '''
    incoming: list["LayerNode"]
    outcoming: list["LayerNode"]


    def compile(self):
        self.layer: layers.Layer = super().compile()

        input_layers = [node.layer for node in self.incoming]
        if len(input_layers) == 1: input_layers = input_layers[0]

        self.layer = self.layer(input_layers)

        return self.layer



