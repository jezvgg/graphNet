import json
from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Logging import logging
from Src.node_editor import NodeEditor
from Src.Managers import EventManager, ThemeManager, FontManager
from Src.Enums import EventType




class App:
    """
    Основной класс приложения, который отвечает за
    создание UI и запуск главного цикла DearPyGui.
    """
    font_manager: FontManager
    theme_manager: ThemeManager
    event_manager: EventManager


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
        self._setup_dpg()

        self.font_manager = FontManager(Path(font_path))
        self.theme_manager = ThemeManager(Path(themes_path))
        self.event_manager = EventManager()

        self._create_ui()


    def _setup_dpg(self):
        """Настраивает контекст и вьюпорт DearPyGui."""
        dpg.create_context()
        dpg.create_viewport(title=self.title)
        dpg.setup_dearpygui()


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

        with dpg.window(tag="Prime"):
            self.node_editor.show("Prime")

        dpg.set_primary_window("Prime", True)
        # Убрать когда будет сделана нормальная работа дефолтного шрифта
        self.font_manager.set("Prime")
        self.event_manager.add(
            EventType.MOUSE_CLICK,
            lambda sender, app_data: self.font_manager.increase("Prime")
            )
        self.logger.info("UI создан.")


    def run(self):
        """Запускает главный цикл приложения."""
        dpg.show_viewport()
        self.logger.info("Приложение запущено.")
        dpg.start_dearpygui()
        dpg.destroy_context()