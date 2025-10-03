import json

import dearpygui.dearpygui as dpg

from Src.Enums import Themes


class ThemeManager:
    '''
    Менеджер тем для графического редактора
    Работает с енум классом "Themes"
    '''
    _themes_config: dict = {}
    _created_themes: dict = {}
    _themes_categories: dict = {
        "mvNodeCol":dpg.mvThemeCat_Nodes,
        "mvPlotCol":dpg.mvThemeCat_Plots,
        "mvThemeCol":dpg.mvThemeCat_Core
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
            theme_name: list[Themes] - темы для применения
            item_id: str | int - id объекта, к которому применяется тема
        """
        theme_key = tuple(theme_names)

        if theme_key not in cls._created_themes:
            merged_theme_data = {}
            for theme_name in theme_names:
                theme_data = cls._themes_config[theme_name]
                for component_name, component_data in theme_data.items():
                    if component_name not in merged_theme_data:
                        merged_theme_data[component_name] = {}
                    merged_theme_data[component_name].update(component_data)

            with dpg.theme() as theme_id:
                for component_name, component_data in merged_theme_data.items():
                    dpg_component = getattr(dpg, component_name)
                    if not dpg_component: continue

                    with dpg.theme_component(dpg_component):
                        for color_attr, color_value in component_data.items():
                            dpg_color_attr = getattr(dpg, color_attr)
                            if not dpg_color_attr: continue

                            category = cls._themes_categories[color_attr.split("_")[0]]
                            dpg.add_theme_color(dpg_color_attr, color_value, category=category)

            cls._created_themes[theme_key] = theme_id

        dpg.bind_item_theme(item_id, cls._created_themes[theme_key])

