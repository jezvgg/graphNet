from typing import Callable 
from functools import wraps

import dearpygui.dearpygui as dpg

from Src.Utils import InputsFactory, TypesFactory
from Src.Nodes import ParameterNode



class AttributesFactory(TypesFactory):
    '''
    Фабрика, реализующая создание аттрибутов нода в зависимости от переданных параметров.
    '''
    inputs: InputsFactory
    map: dict[type: Callable]
    

    def __init__(self):
        self.inputs = InputsFactory()
        super().__init__()

        self.mapping_subclasses(ParameterNode, self.build_object)


    def build(self, value: type, parent: str | int, *args, **kwargs):
        if value in self.type_map:
            return self.build(value, *args, **kwargs)
        return self.build_other(value, *args, **kwargs)


    def build_other(self, value: type, *args, **kwargs):
        with dpg.node_attribute(parent=kwargs.get('parent') or 0, attribute_type=dpg.mvNode_Attr_Static) as attr:
            self.inputs.build(value, shape=value, parent=attr, *args, **kwargs)
        return attr
    

    @wraps(dpg.node_attribute, assigned=())
    def build_object(self, *args, **kwargs):
        with dpg.node_attribute(*args, **kwargs, attribute_type=dpg.mvNode_Attr_Input, user_data=[]) as attr:
            dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))
        return attr