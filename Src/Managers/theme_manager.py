import json
from collections import defaultdict
from typing import Any
from pathlib import Path
from types import MappingProxyType

import dearpygui.dearpygui as dpg

from Src.Enums import Themes, DPGType
from Src.Enums.theme_elements import ThemeElement
from Src.Utils import singleton, set_userdata, lateinit
from Src.Logging import logging



@singleton
class ThemeManager:
    """
    Менеджер тем для графического редактора.
    Работает с енум классом "Themes".
    """
    __logger = lateinit(logging(), 'themes')
    __created_themes: dict[tuple[Themes], int | str] = {}
    __item_themes: dict[int | str, set[Themes]] = defaultdict(set)
    __themes_categories = {
        "mvNode": dpg.mvThemeCat_Nodes,
        "mvPlot": dpg.mvThemeCat_Plots,
        "mvThem": dpg.mvThemeCat_Core,
        "mvStyl": dpg.mvThemeCat_Core
    }
    config: MappingProxyType[str, MappingProxyType[str, MappingProxyType[str, Any]]]


    def __init__(self, theme_path: Path):
        """
        Загружает конфигурацию тем из JSON-файла.
        args:
            theme_path: str - Путь до файла конфига
        """
        with open(theme_path, "r") as f:
            self.config = json.load(f, object_hook=MappingProxyType)


    def apply(self, item_id: str | int, *theme_names: Themes):
        """
        Находит (или создает) и применяет тему к указанному элементу.
        В качестве идентификатора темы используется член Enum "Themes".
        args:
            item_id: str | int - id объекта, к которому применяется тема
            *theme_names: Themes - темы для применения
        """
        self.__item_themes[item_id] = set(theme_names)
        self.__update_item_theme(item_id)


    def add(self, item_id: str | int, *theme_names: Themes):
        """
        Прибавляет тему к наложенным на элемент темам.
        args:
            item_id: str | int - id объекта, для прибавления темы
            *theme_names: Themes - темы для добавления
        """
        self.__item_themes[item_id] |= set(theme_names)
        self.__update_item_theme(item_id)


    def remove(self, item_id: str | int, *theme_names: Themes):
        """
        Удаляет указанные темы из списка тем элемента.
        args:
            item_id: str | int - идентификатор объекта, у которого удаляется тема
            *theme_names: Themes - темы для удаления
        """
        self.__item_themes[item_id] -= set(theme_names)
        self.__update_item_theme(item_id)


    def get(self, *theme_names: Themes) -> int:
        """
        Возвращает id искомой темы.
        args:
            *theme_names: Themes - темы для поиска
        """
        theme_key = tuple(sorted(theme_names, key=lambda x: x.name))

        if theme_key not in self.__created_themes:
            self.__create_theme(*theme_names)

        return self.__created_themes[theme_key]


    def get_component(self, *theme_names: Themes, component: DPGType) -> str | None:
        theme_key = tuple(sorted(theme_names, key=lambda x: x.name))
        theme_tag = "-".join(theme_key)
        component_tag = f"{theme_tag} {component.mvName}"
        return component_tag if dpg.does_item_exist(component_tag) else None


    def get_element(self, *theme_names: Themes, component: DPGType, element: ThemeElement) -> str | None:
        theme_key = tuple(sorted(theme_names, key=lambda x: x.name))
        theme_tag = "-".join(theme_key)
        element_tag = f"{theme_tag} {component.mvName} {element.value}"
        return element_tag if dpg.does_item_exist(element_tag) else None


    def __create_theme(self, *theme_names: Themes):
        """
        Создает тему по параметрам указанных тем.
        Темы, идущие позже в списке, перезаписывают стили предыдущих.
        args:
            *theme_names: Themes - список тем, используемых для создания
        """
        theme_key = tuple(sorted(theme_names, key=lambda x: x.name))
        theme_tag = "-".join(theme_key)

        merged = defaultdict(dict)
        for theme_name in theme_key:
            for comp, data in self.config[theme_name].items():
                merged[comp] |= data

        with dpg.theme(tag=theme_tag):
            for comp, data in merged.items():
                if not (dpg_comp := getattr(dpg, comp)):
                    continue

                component_tag = f"{theme_tag} {comp}"
                with dpg.theme_component(dpg_comp, tag=component_tag):
                    for attr, value in data.items():
                        if not (dpg_attr := getattr(dpg, attr)):
                            continue

                        category = self.__themes_categories.get(
                            attr.split("_")[0][:6], dpg.mvThemeCat_Core
                        )

                        element_tag = f"{theme_tag} {comp} {attr}"

                        if attr.split("_")[0].endswith('Col'):
                            dpg.add_theme_color(dpg_attr, value, tag=element_tag, category=category)
                        elif isinstance(value, list):
                            dpg.add_theme_style(dpg_attr, *value, tag=element_tag, category=category)
                        else:
                            dpg.add_theme_style(dpg_attr, value, tag=element_tag, category=category)

        set_userdata(theme_tag, value=theme_key)
        self.__created_themes[theme_key] = theme_tag


    def __update_item_theme(self, item_id: str | int):
        """
        Собирает все темы для элемента, создает одну объединенную тему и применяет ее.
        args:
            item_id: str | int - идентификатор объекта
        """
        theme_names = self.__item_themes.get(item_id)
        if not theme_names:
            dpg.bind_item_theme(item_id, 0)  # 0 - дефолтная тема
            return

        dpg.bind_item_theme(item_id, self.get(*theme_names))
        set_userdata(item_id, "theme", tuple(sorted(theme_names, key=lambda x: x.name)))
