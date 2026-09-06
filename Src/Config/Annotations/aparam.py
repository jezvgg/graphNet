from abc import ABC, abstractmethod

import dearpygui.dearpygui as dpg

from Src.Managers import ThemeManager
from Src.Config.Annotations import Annotation
from Src.Enums import DPGType
from Src.Utils.instancelessmethod import instancelessmethod


class AParam(Annotation, ABC):
    @instancelessmethod
    def _build(self, *args, **kwargs) -> str | int:
        pass

    @instancelessmethod
    def build(self, *args, **kwargs) -> str | int:
        if DPGType(kwargs["parent"]) != DPGType.NODE_ATTRIBUTE:
            return self._build(*args, **kwargs)

        new_parent = dpg.get_item_parent(kwargs["parent"])
        dpg.delete_item(kwargs["parent"])

        attribute_kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        attribute_kwargs["parent"] = new_parent
        attribute_kwargs["user_data"] = []

        if "attribute_type" not in attribute_kwargs.keys():
            attribute_kwargs["attribute_type"] = dpg.mvNode_Attr_Input

        kwargs["parent"] = new_parent

        with dpg.node_attribute(*args, **attribute_kwargs) as attr:
            input_id = self._build(*args, **kwargs)

        if hasattr(self.node_type, "theme_name"):
            ThemeManager.apply_theme(attr, self.node_type.theme_name)

        return input_id
