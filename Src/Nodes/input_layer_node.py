from keras import layers
import dearpygui.dearpygui as dpg

from Src.Nodes import LayerNode



class InputLayerNode(LayerNode):
    '''
    Класс для связи данных и нейронной сети, реализует логику keras.Input.
    '''
    logic: layers.Input


    def compile(self):
        # TODO Какого хуя тут логику get_value? Убрать её нахер
        attributes = dpg.get_item_children(self.node_tag)
        arguments = dpg.get_item_children(attributes[1][2])[1]

        kwargs = {}

        for argument in arguments:
            name = dpg.get_item_label(argument)
            if name in self.annotations:
                if isinstance(self.annotations[name], tuple):
                    kwargs[name] = tuple(dpg.get_values(dpg.get_item_children(argument)[1])[:len(self.annotations[name])])
                    continue
                        
                kwargs[name] = dpg.get_value(argument)

        self.layer = self.logic(**kwargs)
        return self.layer