import json

import dearpygui.dearpygui as dpg

from Src.Logging.logger_factory import Logger_factory
from Src.node_editor import NodeEditor
from Src.size_manager import SizeManager
from Src.Events import EventManager




class App:
    """
    Основной класс приложения, который отвечает за
    создание UI и запуск главного цикла DearPyGui.
    """


    def __init__(
            self,
            title: str,
            logger_config_path: str,
            font_path: str,
            initial_app_font_size: int,
            initial_node_font_size: int,
            font_limits: tuple[int, int],
            initial_global_scale: float,
            global_scale_limits: tuple[float, float]
    ):
        """
        Инициализирует приложение
        """
        self.title = title
        self.logger_config_path = logger_config_path
        self.font_path = font_path
        self.initial_app_font_size = initial_app_font_size
        self.initial_node_font_size = initial_node_font_size
        self.font_limits = font_limits
        self.initial_global_scale = initial_global_scale
        self.global_scale_limits = global_scale_limits

        self.logger_factory = None
        self.main_logger = None
        self.size_manager = None
        self.node_editor = None

        self._setup_dpg()
        self._setup_logging()

        EventManager.set_logger(self.logger_factory("EventManager"))

        self._setup_sizing_and_fonts()
        self._create_ui()


    def _setup_dpg(self):
        """Настраивает контекст и вьюпорт DearPyGui."""
        dpg.create_context()
        dpg.create_viewport(title=self.title)
        dpg.setup_dearpygui()


    def _setup_logging(self):
        """Настраивает систему логирования."""
        with open(self.logger_config_path) as f:
            log_config = json.load(f)

        self.logger_factory = Logger_factory(log_config)
        self.main_logger = self.logger_factory("main")
        self.main_logger.info("Система логирования инициализирована.")


    def _setup_sizing_and_fonts(self):
        """Инициализирует менеджер размеров и загружает шрифты."""
        self.size_manager = SizeManager(
            font_limits=list(self.font_limits),
            initial_node_font_size=self.initial_node_font_size,
            initial_global_scale=self.initial_global_scale,
            global_scale_limits=list(self.global_scale_limits)
        )

        fonts_to_load = self._build_font_list()

        with dpg.font_registry():
            self.size_manager.load_fonts(fonts_to_load)
        self.main_logger.info("Шрифты загружены.")

        dpg.set_viewport_resize_callback(callback=self._on_viewport_resize_callback)
        with dpg.handler_registry():
            dpg.add_mouse_wheel_handler(callback=self._mouse_wheel_zoom_callback)


    def _build_font_list(self) -> list:
        """Собирает список шрифтов для загрузки на основе конфигурации."""
        fonts = [
            {
                "path": self.font_path,
                "size": self.initial_app_font_size,
                "dpg_tag": "app_font_default",
                "make_default": True
            }
        ]
        min_size, max_size = self.font_limits
        for size in range(min_size, max_size + 1):
            fonts.append({
                "path": self.font_path,
                "size": size,
                "dpg_tag": f"font_{size}"
            })
        return fonts


    def _create_ui(self):
        """Создает основной интерфейс приложения."""
        self.node_editor = NodeEditor(
            size_manager=self.size_manager,
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_TopRight
        )

        with dpg.window(tag="Prime"):
            self.node_editor.show("Prime")
            self.logger_factory.show("Prime")

        dpg.set_primary_window("Prime", True)
        self.main_logger.info("UI создан.")


    def _mouse_wheel_zoom_callback(self, sender: str | int, app_data: float):
        """
        Callback для масштабирования с помощью колеса мыши.
        Масштабирует редактор узлов, если курсор над редактором и зажат Shift.
        В противном случае масштабирует всё приложение, если зажат Shift.
        """
        if not dpg.is_key_down(dpg.mvKey_LShift):
            return

        if dpg.is_item_hovered('node_editor'):
            self.size_manager.resize_node_editor('node_editor', app_data)
        else:
            self.size_manager.resize_global(app_data)


    def _on_viewport_resize_callback(self, sender, app_data):
        """Callback для изменения размера node_editor'a"""
        if dpg.does_item_exist('node_editor'):
            dpg.configure_item('node_editor', height=dpg.get_viewport_height() * 0.9)


    def run(self):
        """Запускает главный цикл приложения."""
        dpg.show_viewport()
        self.main_logger.warning("Приложение запущено.")
        dpg.start_dearpygui()
        dpg.destroy_context()