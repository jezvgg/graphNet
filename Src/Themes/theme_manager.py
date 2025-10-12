import json
from collections import OrderedDict

import dearpygui.dearpygui as dpg

from Src.Enums import Themes


class ThemeManager:
    '''
    Менеджер тем для графического редактора
    Работает с енум классом "Themes"
    '''
    _themes_config: dict = {}
    _created_themes: dict = {}
    _item_themes: dict[int | str, list[Themes]] = {}
    _themes_categories: dict = {
        "mvNodeCol": dpg.mvThemeCat_Nodes,
        "mvPlotCol": dpg.mvThemeCat_Plots,
        "mvThemeCol": dpg.mvThemeCat_Core
    }
    _dpg_attrs: dict = {
        "FrameRounding": "frame_rounding",
        "FramePadding": "frame_padding",
        "ItemSpacing": "item_spacing",
        "WindowRounding": "window_rounding",
        "PopupRounding": "popup_rounding",
    }


    @classmethod
    def load_themes(cls, theme_path: str):
        """
        Загружает конфигурацию тем из JSON-файла
        args:
            theme_path: str - Путь до файла конфига
        """
        with open(theme_path, 'r') as f:
            cls._themes_config = json.load(f)


    @classmethod
    def apply_theme(cls, theme_names: list[Themes], item_id: str | int):
        """
        Находит (или создает) и применяет тему к указанному элементу.
        В качестве идентификатора темы используется член Enum "Themes".
        args:
            theme_names: list[Themes] - темы для применения
            item_id: str | int - id объекта, к которому применяется тема
        """
        cls._item_themes[item_id] = theme_names
        cls._update_item_theme(item_id)


    @classmethod
    def add_theme(cls, theme_names: list[Themes], item_id: str | int):
        """
        Прибавляет тему к наложенным на элемент темам.

        args:
            theme_names: list[Themes] - темы для добавления
            item_id: str | int - id объекта, для прибавления темы
        """
        current_themes = cls._item_themes.get(item_id, [])

        for theme in theme_names:
            if theme not in current_themes:
                current_themes.append(theme)

        cls._item_themes[item_id] = current_themes
        cls._update_item_theme(item_id)


    @classmethod
    def remove_theme(cls, item_id: str | int, theme_names: list[Themes]):
        """
        Удаляет указанные темы из списка тем элемента.

        args:
            item_id: str | int - идентификатор объекта, у которого удаляется тема
            theme_names: list[Themes] - темы для удаления
        """
        current_themes = cls._item_themes.get(item_id, [])

        new_themes = [theme for theme in current_themes if theme not in theme_names]

        cls._item_themes[item_id] = new_themes
        cls._update_item_theme(item_id)


    @classmethod
    def get_theme(cls, theme_names: list[Themes]):
        '''
        Возвращает id искомой темы темы
        args:
            theme_names: list[Themes] - темы для поиска
        '''
        theme_key = tuple(theme_names)

        if not theme_key in cls._created_themes:
            cls._create_theme(theme_names)

        return cls._created_themes[theme_key]

    @classmethod
    def _update_item_theme(cls, item_id: str | int):
        """
        Собирает все темы для элемента из _item_themes,
        создает одну объединенную тему и применяет ее.

        args:
            item_id: str | int - идентификатор объекта
        """
        theme_names = cls._item_themes.get(item_id, [])
        if not theme_names:
            dpg.bind_item_theme(item_id, 0) # 0 - дефолтная тема
            return

        theme_key = tuple(theme_names)

        if theme_key not in cls._created_themes:
            cls._create_theme(theme_names)

        dpg.bind_item_theme(item_id, cls._created_themes[theme_key])


    @classmethod
    def _create_theme(cls, theme_names: list[Themes]):
        '''
        Создает тему по параметрам указанных тем.
        Темы, идущие позже в списке, перезаписывают стили предыдущих.
        args:
            theme_names: list[Themes] - список тем, используемых для создания
        '''
        theme_key = tuple(theme_names)
        merged = OrderedDict()

        for theme_name in theme_names:
            if theme_name in cls._themes_config:
                for comp, data in cls._themes_config[theme_name].items():
                    if comp not in merged:
                        merged[comp] = {}
                    merged[comp].update(data)

        with dpg.theme() as theme_id:
            for comp, data in merged.items():
                dpg_comp = getattr(dpg, comp, None)
                if dpg_comp:
                    with dpg.theme_component(dpg_comp):
                        for attr, value in data.items():
                            dpg_attr = getattr(dpg, attr, None)
                            if dpg_attr:
                                category = cls._themes_categories.get(attr.split("_")[0], dpg.mvThemeCat_Core)
                                dpg.add_theme_color(dpg_attr, value, category=category)

        cls._created_themes[theme_key] = theme_id

