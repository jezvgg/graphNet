import json

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory
from Src.node_editor import NodeEditor
from Src.font_manager import FontManager

dpg.create_context()
dpg.create_viewport(title='Custom Title')


with open("Src/Logging/logger_config.json") as f:
    config = json.load(f)

log_factory = Logger_factory(config)
main_logger = log_factory("main")

font_manager = FontManager()

# Конфигурация основного шрифта приложения
font_path = "notomono-regular.ttf"
app_font_size = 13
font_manager.configure_app_font(
    user_tag="DefaultAppFont",
    font_path=font_path,
    size=app_font_size,
    make_default=True
)

# Параметры шрифтов для нодов
initial_node_font_size = 13
min_node_font_size_limit = 8
max_node_font_size_limit = 28
node_font_tag_prefix = "NodeFont"

# Генерируем список размеров шрифтов для нодов
node_font_sizes_to_load = list(
    range(
        min_node_font_size_limit,
        max_node_font_size_limit + 1,
        1
    )
)

# Конфигурируем шрифты для нодов
font_manager.configure_node_fonts(
    font_path=font_path,
    base_size=initial_node_font_size,
    sizes=node_font_sizes_to_load,
    tag_prefix=node_font_tag_prefix
)

# Загружаем все сконфигурированные шрифты (и для приложения, и для узлов)
with dpg.font_registry():
    font_manager.load_fonts()

# Создаем NodeEditor с уже готовыми шрифтами
node_editor = NodeEditor(
    font_manager=font_manager,
    initial_node_font_size=initial_node_font_size,
    min_node_font_size_limit=min_node_font_size_limit,
    max_node_font_size_limit=max_node_font_size_limit,
    minimap=True,
    minimap_location=dpg.mvNodeMiniMap_Location_TopRight
)

with dpg.window(tag="Prime"):
    node_editor.show("Prime")
    log_factory.show("Prime")
    main_logger.warning("НАЧАЛИ")


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Prime", True)
dpg.start_dearpygui()

font_manager.clear()
dpg.destroy_context()
