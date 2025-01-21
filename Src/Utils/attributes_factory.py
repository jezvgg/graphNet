from functools import singledispatchmethod

import dearpygui.dearpygui as dpg

from Src.Utils import InputsFactory
from Src.Nodes import AbstractNode



class AttributesFactory:
    '''
    Фабрика, реализующая создание аттрибутов нода в зависимости от переданных параметров.
    '''
    inputs: InputsFactory
    
    def __init__(self):
        self.inputs = InputsFactory()


    @singledispatchmethod
    def build(self, hint, parent: str | int, *args, **kwargs):
        '''
        Создать аттрибут

        Args:
            hint: type | tuple | AbstractNode - тип, по которому будет создаваться аттрибут.
            parent: str | int - родительский элемент в котором размещать
            *args, **kwargs - параметры для инпутов
        '''
        with dpg.node_attribute(parent=parent, attribute_type=dpg.mvNode_Attr_Static) as attr:
            self.inputs.build(hint, parent=attr, *args, **kwargs)
    

    @build.register
    def build_object(self, hint: AbstractNode, parent: str | int, *args, **kwargs):
        with dpg.node_attribute(parent=parent, attribute_type=dpg.mvNode_Attr_Input):
            if 'label' in kwargs: dpg.add_text(kwargs['label'])