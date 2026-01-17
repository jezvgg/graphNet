from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Utils import lateinit, singleton


class FontUnit:
    name: str
    size: int
    id: str | int

    prev: "FontUnit"
    next: "FontUnit"

    __range_map = {
        'default': dpg.mvFontRangeHint_Default,
        'japanese': dpg.mvFontRangeHint_Japanese,
        'korean': dpg.mvFontRangeHint_Korean,
        'chinese_full': dpg.mvFontRangeHint_Chinese_Full,
        'chinese_simplified_common': dpg.mvFontRangeHint_Chinese_Simplified_Common,
        'cyrillic': dpg.mvFontRangeHint_Cyrillic,
        'thai': dpg.mvFontRangeHint_Thai,
        'vietnamese': dpg.mvFontRangeHint_Vietnamese
    }
    __registry: int | str = lateinit(singleton(dpg.add_font_registry))


    def __init__(self, path: Path, hints: list[str], 
                name: str, size: int, id: str | int, 
                prev: "FontUnit" = None, next: "FontUnit" = None):
        # Негде не сохраняю path и hints будем надееться, что не понадобяться
        self.name = name
        self.size = size
        self.id = id
        self.prev = prev or self
        self.next = next or self

        with dpg.font(path, self.size, parent=self.__registry, tag=self.id):
            for hint in hints:
                dpg.add_font_range_hint(self.__range_map[hint], parent=self.id)

        dpg.set_item_user_data(self.id, self)
