from typing import get_args

import dearpygui.dearpygui as dpg

from Src.Config.Annotations.annotation import Annotation


class ASequence(Annotation):
    items: tuple[type]


    def __class_getitem__(cls, items):
        if not isinstance(items, tuple):
            items = (items,)
        cls.items = items
        return cls


    @classmethod
    def build(cls, *args, **kwargs):
        shape: tuple[Annotation] = get_args(cls.items)
        kwargs = Annotation.check_kwargs(dpg.group, kwargs)
        with dpg.group(horizontal=True, *args, **kwargs) as item:
            for hint in shape:
                hint.build(hint, parent=item)

            # Если отсутсвует label, то создаст пустой текст
            dpg.add_text(kwargs.get('label') or '')
        return item


    @staticmethod
    def get(input_field: int | str):
        return dpg.get_value(input_field)
    

    @staticmethod
    def set(): pass