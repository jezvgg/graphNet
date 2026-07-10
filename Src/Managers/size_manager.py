import dearpygui.dearpygui as dpg

from Src.Utils import lateinit, singleton, get_children, get_userdata, set_userdata
from Src.Logging import logging
from Src.Managers import FontManager, ThemeManager
from Src.Enums import DPGType, Themes



@singleton
class SizeManager:
    SIZE_RATIO = 1 # Костыль, который появился из-за отсутствия изменения спейсинга и падинга

    __logger = lateinit(logging(), 'managers')
    __font_manager: FontManager = lateinit(FontManager)
    __theme_manager: ThemeManager = lateinit(ThemeManager)


    def __init__(self):

        for item in {"node_editor"} | get_children("node_editor"):
            height, width = self.get_bbox(item)
            current_font_size: int = self.__font_manager.get(item).size
            min_font_size = get_userdata(item, 'min_font_size').size
            font_ratio = min_font_size / current_font_size
            set_userdata(item, 'min_width', width * font_ratio)
            set_userdata(item, 'min_height', height * font_ratio)


    def get_bbox(self, item: int | str):
        return dpg.get_item_height(item) or 0, dpg.get_item_width(item) or 0


    def get_min_bbox(self, item: int | str):
        current_font_size: int = self.__font_manager.get(item).size
        min_font_size = get_userdata(item, 'min_font_size').size
        font_ratio = min_font_size / current_font_size
        if not (height := get_userdata(item, 'min_height')):
            height = set_userdata(item, 'min_height', dpg.get_item_height(item) or 0 * font_ratio)
        if not (width := get_userdata(item, 'min_width')):
            width = set_userdata(item, 'min_width', dpg.get_item_width(item) or 0 * font_ratio)
        return height, width


    def set_bbox(self, item: int | str, height: int, width: int):
        if DPGType(dpg.get_item_type(item)) is DPGType.TEXT: return # У текста бл*ть есть ширина, которую нельзя изменять, великолепно нахуй
        height_, width_ = self.get_bbox(item)
        if height_ != 0: dpg.set_item_height(item, height)
        if width_ != 0: dpg.set_item_width(item, width)


    def transform(self, id: int | str, ratio: float, children: bool = True):
        items = {id}
        if children: items|= get_children(id)

        for item in items:
            height, width = self.get_min_bbox(item)
            self.set_bbox(item, int(height * ratio), int(width * ratio * self.SIZE_RATIO))

            default_elements = self.__theme_manager.config \
                            .get(Themes.RESIZABLE.value) \
                            .get(DPGType.NODE.mvName)

            if not (theme_id := dpg.get_item_theme(item)): continue
            theme = get_userdata(theme_id)
            if not (component := self.__theme_manager \
                .get_component(*theme, component=DPGType(item))):
                    continue

            for element in get_children(component, depth=1):
                if (element := dpg.get_item_alias(element)).split()[2] not in default_elements: continue
                value = default_elements.get(element.split()[2])
                if not isinstance(value, list): value = [value]
                value = [val * ratio for val in value]
                # print(value)
                dpg.set_value(element, value)

        return ratio


    def increase(self, item: str | int, children: bool = True):
        min_font_size = get_userdata(item, 'min_font_size').size
        next_size = self.__font_manager.increase(item).size
        ratio = next_size / min_font_size

        return self.transform(item, ratio, children)


    def reduce(self, item: str | int, children: bool = True):
        min_font_size = get_userdata(item, 'min_font_size').size
        next_size = self.__font_manager.reduce(item).size
        ratio = 1 / (min_font_size / next_size)

        return self.transform(item, ratio, children)
