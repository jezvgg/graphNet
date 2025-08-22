from keras import layers
import dearpygui.dearpygui as dpg

from Src.Nodes import LayerNode, AbstractNode



class InputLayerNode(LayerNode):
    '''
    Класс для связи данных и нейронной сети, реализует логику keras.Input.
    '''
    logic: layers.Input
    layer: layers.Input
    inputs: set["InputLayerNode"]


    def compile(self):
        status = AbstractNode.compile(self)
        self.layer = self.OUTPUT
        self.inputs = set([self])
        return status
        