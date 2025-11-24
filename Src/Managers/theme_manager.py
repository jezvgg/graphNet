import json
from collections import defaultdict
from typing import Any
from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Enums import Themes




class ThemeManager:
    """
    Менеджер тем для графического редактора.
    Работает с енум классом "Themes".
    """
    _themes_config: dict[str, dict[str, dict[str, Any]]] = {}
    _created_themes: dict[tuple[Themes], int | str] = {}
    _item_themes: dict[int | str, set[Themes]] = {}
    _themes_categories = {
        "mvNodeCol": dpg.mvThemeCat_Nodes,
        "mvPlotCol": dpg.mvThemeCat_Plots,
        "mvThemeCol": dpg.mvThemeCat_Core,
    }


    @classmethod
    def __create_theme(cls, *theme_names: Themes):
        """
        Создает тему по параметрам указанных тем.
        Темы, идущие позже в списке, перезаписывают стили предыдущих.
        args:
            *theme_names: Themes - список тем, используемых для создания
        """
        theme_key = tuple(sorted(theme_names))

        merged = defaultdict(dict)
        for theme_name in theme_key:
            for comp, data in cls._themes_config[theme_name].items():
                merged[comp] |= data


        with dpg.theme() as theme_id:
            for comp, data in merged.items():
                if not (dpg_comp := getattr(dpg, comp)):
                    continue

                with dpg.theme_component(dpg_comp):
                    for attr, value in data.items():
                        if not (dpg_attr := getattr(dpg, attr)):
                            continue
                        category = cls._themes_categories.get(
                            attr.split("_")[0], dpg.mvThemeCat_Core
                        )
                        dpg.add_theme_color(dpg_attr, value, category=category)

        cls._created_themes[theme_key] = theme_id


    @classmethod
    def __update_item_theme(cls, item_id: str | int):
        """
        Собирает все темы для элемента, создает одну объединенную тему и применяет ее.
        args:
            item_id: str | int - идентификатор объекта
        """
        theme_names = cls._item_themes.get(item_id)
        if not theme_names:
            dpg.bind_item_theme(item_id, 0)  # 0 - дефолтная тема
            return

        dpg.bind_item_theme(item_id, cls.get_theme(*theme_names))


    @classmethod
    def load_themes(cls, theme_path: Path):
        """
        Загружает конфигурацию тем из JSON-файла.
        args:
            theme_path: str - Путь до файла конфига
        """
        with open(theme_path, "r") as f:
            cls._themes_config = json.load(f)


    @classmethod
    def apply_theme(cls, item_id: str | int, *theme_names: Themes):
        """
        Находит (или создает) и применяет тему к указанному элементу.
        В качестве идентификатора темы используется член Enum "Themes".
        args:
            item_id: str | int - id объекта, к которому применяется тема
            *theme_names: Themes - темы для применения
        """
        cls._item_themes[item_id] = set(theme_names)
        cls.__update_item_theme(item_id)


    @classmethod
    def add_theme(cls, item_id: str | int, *theme_names: Themes):
        """
        Прибавляет тему к наложенным на элемент темам.
        args:
            item_id: str | int - id объекта, для прибавления темы
            *theme_names: Themes - темы для добавления
        """
        cls._item_themes[item_id] |= set(theme_names)
        cls.__update_item_theme(item_id)


    @classmethod
    def remove_theme(cls, item_id: str | int, *theme_names: Themes):
        """
        Удаляет указанные темы из списка тем элемента.
        args:
            item_id: str | int - идентификатор объекта, у которого удаляется тема
            *theme_names: Themes - темы для удаления
        """
        cls._item_themes[item_id] -= set(theme_names)
        cls.__update_item_theme(item_id)


    @classmethod
    def get_theme(cls, *theme_names: Themes) -> int:
        """
        Возвращает id искомой темы.
        args:
            *theme_names: Themes - темы для поиска
        """
        theme_key = tuple(sorted(theme_names, key=lambda x: x.name))

        if theme_key not in cls._created_themes:
            cls.__create_theme(*theme_names)

        return cls._created_themes[theme_key]