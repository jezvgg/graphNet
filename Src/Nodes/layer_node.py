from itertools import chain

from keras import layers
import dearpygui.dearpygui as dpg

from Src.Nodes import AbstractNode



class LayerNode(AbstractNode):
    '''
    Класс хранящий данные, для связи нода с слоём нейроной сети.
    '''
    inputs: set["LayerNode"]


    def compile(self):
        self.layer: layers.Layer = super().compile()
        input_nodes = [dpg.get_item_user_data(dpg.get_item_parent(node)) \
                        for node in chain(*self.incoming.values())]

        input_layers = [getattr(node, 'layer') for node in input_nodes]
        if len(input_layers) == 1: input_layers = input_layers[0]

        self.layer = self.layer(input_layers)

        inputs = [getattr(node, 'inputs') for node in input_nodes]
        self.inputs = set().union(*inputs)

        return self.layer



