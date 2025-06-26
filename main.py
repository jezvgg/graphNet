import json

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory
from Src.node_editor import NodeEditor
from Src.size_manager import SizeManager

dpg.create_context()
dpg.create_viewport(title='Custom Title')


with open("Src/Logging/logger_config.json") as f:
    config = json.load(f)

log_factory = Logger_factory(config)
main_logger = log_factory("main")

# Конфигурация размеров и шрифтов
font_path = "notomono-regular.ttf"
initial_app_font_size = 14
initial_node_font_size = 14
min_node_font_size_limit = 8
max_node_font_size_limit = 28

initial_global_scale = 1.0
min_global_scale = 0.5
max_global_scale = 2.0

size_manager = SizeManager(
    font_limits=[min_node_font_size_limit, max_node_font_size_limit],
    initial_node_font_size=initial_node_font_size,
    initial_global_scale=initial_global_scale,
    global_scale_limits=[min_global_scale, max_global_scale]
)

# Шрифты
fonts = [
    {
        "path": font_path,
        "size": initial_app_font_size,
        "dpg_tag": "app_font_default",
        "make_default": True
    }
]


for size in range(min_node_font_size_limit, max_node_font_size_limit + 1):
    fonts.append({
        "path": font_path,
        "size": size,
        "dpg_tag": f"font_{size}"
    })

# Загружаем все сконфигурированные шрифты
with dpg.font_registry():
    size_manager.load_fonts(fonts)
#  Конец конфигурации размеров и шрифтов

# Создаем NodeEditor с уже готовыми шрифтами, управляемыми SizeManager
node_editor = NodeEditor(
    size_manager=size_manager,
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

dpg.destroy_context()
