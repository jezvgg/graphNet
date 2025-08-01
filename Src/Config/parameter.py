from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from Src.Enums.attr_type import AttrType
from Src.Config.Annotations import Annotation


AUTODEFAULT = 0


@dataclass
class Parameter:
    attr_type: AttrType
    hint: Annotation
    default: object = None


    def build(self, parent: int | str, *args, **kwargs):
        if (dpg.get_item_type(parent) != 'mvAppItemType::mvNode'):
            raise Exception(f"Incompatable parent {dpg.get_item_type(parent)} must be mvAppItemType::mvNode")
        
        kwargs['parent'] = parent
        # Возможно исправить потом на более гибкую версию
        attribute_type =  dpg.mvNode_Attr_Output if self.attr_type == AttrType.OUTPUT else dpg.mvNode_Attr_Static
        attribute_kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)

        with dpg.node_attribute(*args, **attribute_kwargs, attribute_type=attribute_type) as attr:
            kwargs['parent'] = attr
            self.hint.build(*args, **kwargs)

        return attr
    

    def get_value(self, argument: int):
        field = dpg.get_item_children(argument)[1][0]
        value = self.hint.get(field)
        return value

