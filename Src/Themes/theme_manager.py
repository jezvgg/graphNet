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
    def apply_theme(cls, theme_name: Themes, item_id: str | int):
        """
        Находит (или создает) и применяет тему к указанному элементу.
        В качестве идентификатора темы используется член Enum "Themes".
        args:
            theme_name: Themes - тема для применения
            item_id: str | int - id объекта, к которому применяется тема
        """
        if theme_name not in cls._themes_config:
            theme_name = Themes.DEFAULT

        if theme_name not in cls._created_themes:
            theme_data = cls._themes_config[theme_name]

            with dpg.theme() as theme_id:
                for component_name, component_data in theme_data.items():
                    dpg_component = getattr(dpg, component_name)
                    if not dpg_component: continue

                    with dpg.theme_component(dpg_component):
                        for color_attr, color_value in component_data.items():
                            dpg_color_attr = getattr(dpg, color_attr)
                            if not dpg_color_attr: continue

                            category = cls._get_category_for_color(color_attr)
                            dpg.add_theme_color(dpg_color_attr, color_value, category=category)

            cls._created_themes[theme_name] = theme_id
        dpg.bind_item_theme(item_id, cls._created_themes[theme_name])


    @staticmethod
    def _get_category_for_color(color_attr_name: str) -> int:
        '''
        Функция для выбора категории атрибута темы
        args:
            color_attr_name: str - название атрибута цвета объекта
        '''
        if color_attr_name.startswith("mvNodeCol"):
            return dpg.mvThemeCat_Nodes
        if color_attr_name.startswith("mvPlotCol"):
            return dpg.mvThemeCat_Plots
        return dpg.mvThemeCat_Core
