from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from Src.Enums.attr_type import AttrType
from Src.Config.Annotations import Annotation
from Src.Utils import Backfield



@dataclass
class Parameter:
    attr_type: AttrType
    hint: Annotation
    default: object = None
    backfield: Backfield = None


    def build(self, parent: int | str, *args, **kwargs) -> str | int:
        if (dpg.get_item_type(parent) != 'mvAppItemType::mvNode'):
            raise Exception(f"Incompatable parent {dpg.get_item_type(parent)} must be mvAppItemType::mvNode")

        kwargs['parent'] = parent
        # Возможно исправить потом на более гибкую версию
        attribute_type =  dpg.mvNode_Attr_Output if self.attr_type == AttrType.OUTPUT else dpg.mvNode_Attr_Static
        attribute_kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)

        with dpg.node_attribute(*args, **attribute_kwargs, attribute_type=attribute_type) as attr:
            kwargs['parent'] = attr
            if self.attr_type != AttrType.INPUT: kwargs['enabled'] = False
            input_id = self.hint.build(*args, **kwargs)

        if isinstance(self.backfield, Backfield): 
            self.backfield.callback = lambda x: self.hint.set(input_id, x)

        if self.default: self.set_value(attr, self.default)

        return attr
    

    def get_value(self, argument: int | str):
        field = dpg.get_item_children(argument)[1][0]
        value = self.hint.get(field)
        return value
    

    def set_value(self, argument: int | str, value) -> bool:
        field = dpg.get_item_children(argument)[1][0]
        return self.hint.set(field, value)
