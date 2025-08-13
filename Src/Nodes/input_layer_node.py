from keras import layers
import dearpygui.dearpygui as dpg

from Src.Nodes import AbstractNode



class InputLayerNode(AbstractNode):
    '''
    Класс для связи данных и нейронной сети, реализует логику keras.Input.
    '''
    logic: layers.Input
    layer: layers.Input
    inputs: set["InputLayerNode"]


    def compile(self):
        self.layer = super().compile()
        self.inputs = set([self])
        return self.layer
        