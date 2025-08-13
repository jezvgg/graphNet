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

        input_layers = [getattr(dpg.get_item_user_data(dpg.get_item_parent(node)), 'layer') for node in self.incoming.values()]
        if len(input_layers) == 1: input_layers = input_layers[0]

        self.layer = self.layer(input_layers)

        inputs = [getattr(dpg.get_item_user_data(dpg.get_item_parent(node)),'inputs') for node in self.incoming.values()]
        self.inputs = set().union(*inputs)

        return self.layer



