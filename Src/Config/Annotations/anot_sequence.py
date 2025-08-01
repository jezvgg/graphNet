from typing import get_args

import dearpygui.dearpygui as dpg

from Src.Config.Annotations.annotation import Annotation
from Src.Config.Annotations import *


class ASequence(Annotation):
    items: tuple[type]


    def __class_getitem__(cls, items):
        if not isinstance(items, tuple):
            items = (items,)
        return ASequence(shape = items)
    

    def __init__(self, shape: tuple[Annotation]):
        self.shape = shape
        

    def build(self, *args, **kwargs):
        kwargs = Annotation.check_kwargs(dpg.group, kwargs)
        with dpg.group(horizontal=True, *args, **kwargs) as item:
            for hint in self.shape:
                if hint not in (ABoolean, AFloat, AInteger, AString):
                    raise Exception("Sequence annotations must be only Boolean, Float, Intege or String!")
                hint.build(hint, parent=item)

            # Если отсутсвует label, то создаст пустой текст
            dpg.add_text(kwargs.get('label') or '')
        return item


    def get(self, input_field: int | str):
        result = []
        for input_id in dpg.get_item_children(input_field)[1][:-1]:
            result.append(dpg.get_value(input_id))
        return result
    

    def set(self, input_id: str| int, value: tuple) -> bool:
        if not isinstance(value, tuple) or len(value) != len(self.shape): 
            return False
        
        for input_field, annotation, field_value in \
            zip(dpg.get_item_children(input_id)[1][:-1], self.shape, value):

            if not annotation.set(input_field, field_value):
                return False

        return True