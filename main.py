import json

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory
from Src.page_controller import PageController


dpg.create_context()
dpg.create_viewport(title='Custom Title')


with open("Src/Logging/logger_config.json") as f:
    config = json.load(f)

log_factory = Logger_factory(config)
controller = PageController()
main_logger = log_factory("main")


with dpg.font_registry():
    with dpg.font("notomono-regular.ttf", 13, default_font=True, tag="Default font") as f:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
dpg.bind_font("Default font")

with dpg.window(tag="Prime"):
    controller.start_polling("Prime")
    log_factory.show("Prime")
    main_logger.warning("НАЧАЛИ")


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Prime", True)
dpg.set_global_font_scale(2)
dpg.start_dearpygui()
dpg.destroy_context()