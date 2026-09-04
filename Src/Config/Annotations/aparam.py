from abc import ABC

import dearpygui.dearpygui as dpg

from Src.Managers import ThemeManager
from Src.Config.Annotations import Annotation
from Src.Enums import DPGType
from Src.Utils import instancelessmethod, lateinit


class AParam(Annotation, ABC):
    __themes: ThemeManager = lateinit(ThemeManager)

    @instancelessmethod
    def _build(self, *args, **kwargs) -> str | int: pass

    @instancelessmethod
    def build(self, *args, **kwargs) -> str | int:
        if DPGType(kwargs['parent']) != DPGType.NODE_ATTRIBUTE:
            return self._build(*args, **kwargs)

        new_parent = dpg.get_item_parent(kwargs['parent'])
        dpg.delete_item(kwargs['parent'])

        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        kwargs['parent'] = new_parent
        kwargs['user_data'] = []

        if 'attribute_type' not in kwargs.keys():
            kwargs['attribute_type'] = dpg.mvNode_Attr_Input

        with dpg.node_attribute(*args, **kwargs) as attr:
            input_id = self._build(*args, **kwargs)

        if hasattr(self.node_type, 'theme_name'):
            self.__themes.apply(attr, self.node_type.theme_name)

        return input_id
