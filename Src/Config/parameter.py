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
        kwargs['parent'] = parent
        # Возможно исправить потом на более гибкую версию
        attribute_type =  dpg.mvNode_Attr_Output if self.attr_type == AttrType.OUTPUT else dpg.mvNode_Attr_Static
        attribute_kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)

        with dpg.node_attribute(*args, **attribute_kwargs, attribute_type=attribute_type) as attr:
            kwargs['parent'] = attr
            self.hint.build(*args, **kwargs)

        return attr
    

    def get_value(self, argument: int):
        # ! Ебучие циклически импорты, питон заебал с ними
        # from Src.Utils import GetterFactory
        # value = GetterFactory.get_value(self.hint, argument)
        # print(value)
        value = self.hint.get(argument)
        return value

