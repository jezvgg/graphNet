import dearpygui.dearpygui as dpg

from Src.Utils import lateinit, singleton, get_children
from Src.Logging import logging
from Src.Managers.font_manager import FontManager, FontUnit
from Src.Utils import get_userdata, set_userdata


@singleton
class SizeManager:
    __logger = lateinit(logging(), 'managers')
    __font_manager: FontManager = lateinit(FontManager)


    def __init__(self):

        for item in {"node_editor"} | get_children("node_editor"):
            height, width = self.get_bbox(item)
            # if  height == 0 or width == 0: continue
            current_font_size: int = self.__font_manager.get(item).size
            min_font_size = get_userdata(item, 'min_font_size').size
            font_ratio = min_font_size / current_font_size
            set_userdata(item, 'min_width', width * font_ratio)
            set_userdata(item, 'min_height', height * font_ratio)


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
            height = get_userdata(item, 'min_height')
            width = get_userdata(item, 'min_width')
            print(dpg.get_item_type(item))
            print(dpg.get_item_configuration(item))
            print(dpg.get_item_info(item))
            print(height, width)
            self.set_bbox(item, int(height * ratio), int(width * ratio))

        return ratio


    def increase(self, item: str | int, children: bool = True):
        min_font_size = get_userdata(item, 'min_font_size').size
        next_size = self.__font_manager.increase(item).size
        ratio = next_size / min_font_size
        print(ratio)
        print(next_size / min_font_size)

        return self.transform(item, ratio, children)


    def reduce(self, item: str | int, children: bool = True):
        min_font_size = get_userdata(item, 'min_font_size').size
        next_size = self.__font_manager.reduce(item).size
        ratio = 1 / (min_font_size / next_size)
        print(ratio)
        print(next_size / min_font_size)

        return self.transform(item, ratio, children)
