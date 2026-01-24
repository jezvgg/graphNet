from pathlib import Path
import json
from collections import defaultdict, namedtuple
from itertools import cycle
from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from Src.Managers.font_manager.font import FontUnit
from Src.Utils import singleton, lateinit, get_children
from Src.Logging import logging



@singleton
class FontManager:
    __logger = lateinit(logging(), 'managers')
    __registry: str | int
    fonts: dict[str, dict[int, FontUnit]]
    default: str | int


    def __init__(self, path_config: Path): 
        if not path_config.exists():
            self.__logger.error(f"Не существует конфигационного файла {font_config}")
            return

        config = json.load(path_config.open())
        self.fonts = defaultdict(defaultdict)
        self.default = None
        for font_name, font_config in config.items():
            
            font_ids = [dpg.generate_uuid() for _ in font_config['sizes']]

            font = FontUnit(font_config['path'], font_config['hints'], 
                            font_name, font_config['sizes'][0], font_ids[0])
            self.fonts[font_name][font_config['sizes'][0]] = font

            for size, curr_id, next_id in zip(font_config['sizes'][1:], font_ids[:-1], font_ids[1:]):
                
                font: FontUnit = dpg.get_item_user_data(curr_id)
                next_font = FontUnit(Path(font_config['path']).resolve(), font_config['hints'], 
                                     font_name, size, next_id, prev = font)
                font.next = next_font
                self.fonts[font_name][size] = font
                
            if not font_config.get('default'): continue
            if self.default:
                self.__logger.error(f"Конфигурация шрифтов имеет несколько стандартных шрифтов! Установите один.")

            self.default = self.fonts[font_name][font_config.get('default_size', 14)]
            dpg.bind_font(self.default.id)
        self.__logger.info("Шрифты инициализированы!")


    def __set(self, id: str | int, font: FontUnit, children: bool = True):
        items = {id}
        if children: items|= get_children(id)

        for item in items:
            dpg.bind_item_font(item, font.id)


    def get(self, item: str | int):
        return dpg.get_item_user_data(dpg.get_item_font(item) or self.default.id)


    def increase(self, item: str | int, children: bool = True):
        font: FontUnit = self.get(item)
        self.__set(item, font.next, children)


    def reduce(self, item: str | int, children: bool = True):
        font: FontUnit = self.get(item)
        self.__set(item, font.prev, children)


    def set(self, item: str | int, font_name: str = None, size: int = None, children: bool = True):
        font_name = font_name or self.default.name
        font_size = size or self.default.size
        font: FontUnit = self.fonts[font_name][font_size]
        self.__set(item, font, children)
