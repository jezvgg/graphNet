from enum import Enum

import dearpygui.dearpygui as dpg

class EventType(Enum):
    CLICK = dpg.add_item_clicked_handler
    DOUBLE_CLICK = dpg.add_item_double_clicked_handler
    HOVER = dpg.add_item_hover_handler
    FOCUS = dpg.add_item_focus_handler
    VISIBLE = dpg.add_item_visible_handler
    ACTIVATED = dpg.add_item_activated_handler
    DEACTIVATED = dpg.add_item_deactivated_handler
    EDITED = dpg.add_item_edited_handler