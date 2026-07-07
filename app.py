import json
from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Logging import logging
from Src.node_editor import NodeEditor
from Src.Managers import EventManager, ThemeManager, FontManager, SizeManager
from Src.Enums import EventType




class App:
    """
    Основной класс приложения, который отвечает за
    создание UI и запуск главного цикла DearPyGui.
    """
    font_manager: FontManager
    theme_manager: ThemeManager
    event_manager: EventManager
    size_manager: SizeManager


    def __init__(
            self,
            title: str,
            logger_config_path: str,
            font_path: str,
            themes_path: str,
    ):
        """
        Инициализирует приложение
        """
        self.title = title
        self.logger_config_path = logger_config_path

        self.logger = None
        self.size_manager = None
        self.node_editor = None

        self._setup_logging()
        dpg.create_context()
        dpg.create_viewport(title=self.title)

        self.font_manager = FontManager(Path(font_path))
        self.theme_manager = ThemeManager(Path(themes_path))
        self.event_manager = EventManager()

        dpg.setup_dearpygui()

        self._create_ui()

        self.size_manager = SizeManager()


    def _setup_logging(self):
        """Настраивает систему логирования."""
        logging(logging.open_config("Assets/logger_config.json", False))

        debug_config = logging.open_config('Assets/logger_debug.json')
        group_config = logging.open_config('Assets/logger_group.json')
        stream_config = logging.open_config('Assets/logger_stream.json')

        self.logger = logging()('main', group_config)
        logging()('nodes', group_config | debug_config)
        logging()('functions', group_config | debug_config)
        logging()('events', group_config | debug_config)
        logging()('managers', group_config | debug_config)

        self.logger.info("Система логирования инициализирована.")


    def _create_ui(self):
        """Создает основной интерфейс приложения."""
        self.node_editor = NodeEditor(
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_TopRight
        )

        with dpg.window(tag="Prime") as wnd:
            self.node_editor.show("Prime")

        dpg.set_primary_window("Prime", True)

        self.event_manager.add(
            EventType.MOUSE_WHEEL,
            self.__size_increase
            )
        self.logger.info("UI создан.")


    def __size_increase(self, sender, app_data: int):
        sizing_method = self.size_manager.increase if app_data > 0 else self.size_manager.reduce
        height, width = self.size_manager.get_bbox("node_editor")
        if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
            sizing_method("Prime")

        elif dpg.is_item_hovered("node_editor"):
            # Приближение увеличивает узлы, у которых размер рассчитывается абсолютно
            # для избежания накопления ошибки плавающей точки
            # С изменением позиции для имитации зума так не получиться, поэтому
            # там рассчитывается относительный ratio

            prev_size = self.font_manager.get("node_editor").size
            sizing_method("node_editor")
            actual_size = self.font_manager.get("node_editor").size
            self.node_editor.zoom(actual_size / prev_size)

        self.size_manager.set_bbox("node_editor", height, width)



    def run(self):
        """Запускает главный цикл приложения."""
        dpg.show_viewport()
        self.logger.info("Приложение запущено.")
        dpg.start_dearpygui()
        dpg.destroy_context()
