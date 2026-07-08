from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from Src.Utils import instancelessmethod
from Src.Config.Annotations import AParam
from Src.Config.Annotations.single import Single
from Src.Enums import DPGType
from Src.Managers import ThemeManager
from Src.Utils import lateinit, get_userdata



@dataclass
class ANode(AParam):
    __themes = lateinit(ThemeManager)
    node_type: type = object
    single: bool = False


    def __init__(self, node_type: type = object, single: bool = False):
        self.node_type = node_type
        self.single = single


    def __class_getitem__(cls, item):
        if isinstance(item, Single): return ANode(item.node_type, True)
        return ANode(item, False)


    @instancelessmethod
    def _build(self, *args, **kwargs) -> str | int:
        if hasattr(self.node_type, 'theme_name'):
            self.__themes.apply(kwargs['parent'], self.node_type.theme_name)

        return dpg.add_text(kwargs.get('label'), label=kwargs.get('label'))


    def get(self, input_id: int | str):
        from Src.Nodes import AbstractNode

        parent = dpg.get_item_parent(input_id)

        if DPGType(parent) != DPGType.NODE_ATTRIBUTE:
            raise Exception(f"Incompatable parent of item {dpg.get_item_type(parent)} must be mvAppItemType::mvNodeAttribute")

        user_data = get_userdata(parent)

        node_in: list[tuple[str, AbstractNode]] = [(dpg.get_item_label(attribute),
                                                    get_userdata(dpg.get_item_parent(attribute)))
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
