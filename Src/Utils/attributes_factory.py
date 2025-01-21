from typing import Callable 

import dearpygui.dearpygui as dpg

from Src.Utils import InputsFactory
from Src.Nodes import ParameterNode



class AttributesFactory:
    '''
    Фабрика, реализующая создание аттрибутов нода в зависимости от переданных параметров.
    '''
    inputs: InputsFactory
    map: dict[type: Callable]
    

    def __init__(self):
        self.inputs = InputsFactory()
        self.map = {
            ParameterNode: self.build_object
        }


    def build(self, hint, parent: str | int, *args, **kwargs):
        '''
        Создать аттрибут

        Args:
            hint: type | tuple | AbstractNode - тип, по которому будет создаваться аттрибут.
            parent: str | int - родительский элемент в котором размещать
            *args, **kwargs - параметры для инпутов
        '''
        if hint in self.map:
            return self.map[hint](hint, parent=parent, *args, **kwargs)
        return self.build_other(hint, parent, *args, **kwargs)


    def build_other(self, hint, parent: str | int, *args, **kwargs):
        with dpg.node_attribute(parent=parent, attribute_type=dpg.mvNode_Attr_Static) as attr:
            self.inputs.build(hint, parent=attr, *args, **kwargs)
    

    def build_object(self, hint: ParameterNode, parent: str | int, *args, **kwargs):
        with dpg.node_attribute(parent=parent, attribute_type=dpg.mvNode_Attr_Input, user_data=[]):
            dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))