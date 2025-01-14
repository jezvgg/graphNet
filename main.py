import dearpygui.dearpygui as dpg

from Src.Logging import logger
from Src.Nodes import node_editor


dpg.create_context()

logger = logger("main")
logger.warning("НАЧАЛИ")

with dpg.window(tag="Prime"):
    node_editor(minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_TopRight)

dpg.create_viewport(title='Custom Title')
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Prime", True)
dpg.set_global_font_scale(2)
dpg.start_dearpygui()
dpg.destroy_context()