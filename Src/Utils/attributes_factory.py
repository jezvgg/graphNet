from functools import singledispatchmethod

import dearpygui.dearpygui as dpg

from Src.Utils import InputsFactory
from Src.Nodes import Node



class AttributesFactory:
    inputs: InputsFactory
    
    def __init__(self):
        self.inputs = InputsFactory()


    @singledispatchmethod
    def build(self, hint, parent: str | int, *args, **kwargs):
        with dpg.node_attribute(parent=parent, attribute_type=dpg.mvNode_Attr_Static) as attr:
            self.inputs.build(hint, parent=attr, *args, **kwargs)
    

    @build.register
    def build_object(self, hint: Node, parent: str | int, *args, **kwargs):
        with dpg.node_attribute(parent=parent, attribute_type=dpg.mvNode_Attr_Input):
            if 'label' in kwargs: dpg.add_text(kwargs['label'])