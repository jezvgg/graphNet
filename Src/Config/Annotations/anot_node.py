from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from Src.Config.Annotations.annotation import Annotation
from Src.Config.Annotations.single import Single
from Src.Enums import DPGType
from Src.Themes import ThemeManager




@dataclass
class ANode(Annotation):
    node_type: type = object
    single: bool = False


    def __class_getitem__(cls, item):
        if isinstance(item, Single): return ANode(item.node_type, True)
        return ANode(item, False)


    def build(self, parent: int | str, *args, **kwargs):
        if DPGType(dpg.get_item_type(parent)) != DPGType.NODE_ATTRIBUTE:
            raise Exception(f"Incompatable parent {dpg.get_item_type(parent)} must be mvAppItemType::mvNodeAttribute")

        new_parent = dpg.get_item_parent(parent)
        dpg.delete_item(parent)
        kwargs = Annotation.check_kwargs(dpg.node_attribute, kwargs)
        kwargs['parent'] = new_parent
        kwargs['user_data'] = []
        if 'attribute_type' not in kwargs.keys():
            kwargs['attribute_type'] = dpg.mvNode_Attr_Input

        with dpg.node_attribute(*args, **kwargs) as attr:
            input_id = dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))

        if hasattr(self.node_type, 'theme_name'):
            ThemeManager.apply_theme(attr, [self.node_type.theme_name])

        return input_id


    def get(self, input_id: int | str):
        from Src.Nodes import AbstractNode

        parent = dpg.get_item_parent(input_id)

        if DPGType(dpg.get_item_type(parent)) != DPGType.NODE_ATTRIBUTE:
            raise Exception(f"Incompatable parent of item {dpg.get_item_type(parent)} must be mvAppItemType::mvNodeAttribute")

        user_data = dpg.get_item_user_data(parent)

        node_in: list[tuple[str, AbstractNode]] = [(dpg.get_item_label(attribute),
                                                    dpg.get_item_user_data(dpg.get_item_parent(attribute)))
                                                   for attribute in user_data]

        results = []
        for field, node in node_in:
            if not hasattr(node, field):
                raise AttributeError(f"Атрибут '{field}' не найден в объекте узла типа '{node.__class__.__name__}'.")

            results.append(getattr(node, field))

        # TODO: Сделать raise AttributeException если results пустой
        if self.single and results: return results[0]
        return results


    def set(self, input_id: str | int, value) -> bool:
        return False