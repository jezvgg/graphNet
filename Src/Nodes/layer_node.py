from keras import layers
import dearpygui.dearpygui as dpg

from Src.Nodes import Node



class LayerNode(Node):
    '''
    Класс хранящий данные, для связи нода с слоём нейроной сети.
    '''
    logic: layers.Layer


    def compile(self):
        layer: layers.Layer = super().compile()

        input_layers = [dpg.get_item_user_data(node.node_tag) for node in self.incoming]
        if len(input_layers) == 1: input_layers = input_layers[0]

        return layer(input_layers)



