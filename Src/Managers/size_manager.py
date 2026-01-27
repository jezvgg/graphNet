import dearpygui.dearpygui as dpg

from Src.Utils import lateinit, singleton, get_children
from Src.Logging import logging
from Src.Managers.font_manager import FontManager



@singleton
class SizeManager:
    __logger = lateinit(logging(), 'managers')
    __font_manager = lateinit(FontManager)


    def get_bbox(self, item: int | str):
        return dpg.get_item_height(item) or 0, dpg.get_item_width(item) or 0


    def set_bbox(self, item: int | str, height: int, width: int):
        height_, width_ = self.get_bbox(item)
        if height_ != 0: dpg.set_item_height(item, height)
        if width_ != 0: dpg.set_item_width(item, width)


    def transform(self, id: int | str, ratio: float, children: bool = True):
        items = {id}
        if children: items|= get_children(id)

        for item in items:
            height, width = self.get_bbox(item)
            self.set_bbox(item, int(height * ratio), int(width * ratio))
        
        return ratio


    def increase(self, item: str | int, children: bool = True):
        prev_size = self.__font_manager.get(item).size
        next_size = self.__font_manager.increase(item).size
        ratio = next_size / prev_size
        
        return self.transform(item, ratio, children)


    def reduce(self, item: str | int, children: bool = True):
        prev_size = self.__font_manager.get(item).size
        next_size = self.__font_manager.reduce(item).size
        ratio = next_size / prev_size
        
        return self.transform(item, ratio, children)