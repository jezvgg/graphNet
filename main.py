import json
import sys
from pathlib import Path

import dearpygui.dearpygui as dpg

from Src.Logging import Logger_factory
from Src.Managers import ThemeManager
from Src.node_editor import NodeEditor


dpg.create_context()
dpg.create_viewport(title='Custom Title')

base_path = Path(sys._MEIPASS if hasattr(sys, '_MEIPASS') else '.')
config_path = base_path / "Src/Logging/logger_config.json"
font_path = base_path / "Assets/notomono-regular.ttf"
themes_path = base_path / "Assets/themes.json"


with open(config_path) as f:
    config = json.load(f)

log_factory = Logger_factory(config)
ThemeManager.load_themes(themes_path)
node_editor = NodeEditor(minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_TopRight)
main_logger = log_factory("main")



with dpg.font_registry():
    with dpg.font(font_path, 18, default_font=True, tag="Default font") as f:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
dpg.bind_font("Default font")

with dpg.window(tag="Prime"):
    node_editor.show("Prime")
    log_factory.show("Prime")
    main_logger.warning("НАЧАЛИ")


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Prime", True)
dpg.set_global_font_scale(1)
dpg.start_dearpygui()


dpg.destroy_context()
